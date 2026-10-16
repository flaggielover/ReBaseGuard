/* Linux/OpenSSL 3 source; verification against separately enrolled root pin. */
#define _GNU_SOURCE
#include "anchor_crypto.h"
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/x509.h>
#include <fcntl.h>
#include <stdint.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
static int root_dir(void){
    int f=open("/",O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);const char *parts[]={"etc","rebaseguard-p309"};struct stat s;
    for(size_t i=0;f>=0&&i<2;i++){if(fstat(f,&s)||s.st_uid||!S_ISDIR(s.st_mode)||(s.st_mode&0022)){close(f);return -1;}
        int n=openat(f,parts[i],O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);close(f);f=n;}
    if(f<0)return -1;if(fstat(f,&s)||s.st_uid||!S_ISDIR(s.st_mode)||(s.st_mode&0022)){close(f);return -1;}return f;
}
static int fixed(int d,const char *name,unsigned char *out,size_t cap,size_t *len){
    int f=openat(d,name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);if(f<0)return 0;struct stat s;int ok=0;
    if(fstat(f,&s)||!S_ISREG(s.st_mode)||s.st_uid||(s.st_mode&0777)!=0444||s.st_nlink!=1||s.st_size<=0||(uint64_t)s.st_size>cap)goto done;
    size_t at=0;while(at<(size_t)s.st_size){ssize_t n=read(f,out+at,(size_t)s.st_size-at);if(n<=0)goto done;at+=(size_t)n;}
    unsigned char more;if(read(f,&more,1)!=0)goto done;*len=at;ok=1;
done:close(f);return ok;
}
int p309_anchor_verify(const unsigned char *message,size_t length,const unsigned char signature[384]){
    if(!message||!length||length>4096||!signature)return 0;
    int d=root_dir();if(d<0)return 0;unsigned char der[1024],pin[65],digest[32];size_t dn=0,pn=0;
    int loaded=fixed(d,"host-anchor-ack-v10.spki.der",der,sizeof der,&dn)&&fixed(d,"host-anchor-ack-v10.spki.sha256",pin,sizeof pin,&pn);close(d);
    if(!loaded||pn!=65||pin[64]!='\n')return 0;unsigned int n=0;if(!EVP_Digest(der,dn,digest,&n,EVP_sha256(),NULL)||n!=32)return 0;
    static const char hex[]="0123456789abcdef";unsigned diff=0;for(size_t i=0;i<32;i++){diff|=pin[2*i]^(unsigned char)hex[digest[i]>>4];diff|=pin[2*i+1]^(unsigned char)hex[digest[i]&15];}if(diff)return 0;
    const unsigned char *cursor=der;EVP_PKEY *key=d2i_PUBKEY(NULL,&cursor,(long)dn);EVP_MD_CTX *ctx=NULL;EVP_PKEY_CTX *pk=NULL;int ok=0;
    if(!key||cursor!=der+dn||!EVP_PKEY_is_a(key,"RSA")||EVP_PKEY_get_bits(key)!=3072||EVP_PKEY_get_size(key)!=384)goto done;
    /* Require byte-canonical rsaEncryption SPKI; RSA-PSS-only keys are rejected. */
    unsigned char *canonical=NULL;int cn=i2d_PUBKEY(key,&canonical);int canonical_ok=cn==(int)dn&&canonical&&!memcmp(canonical,der,dn);OPENSSL_free(canonical);if(!canonical_ok)goto done;
    ctx=EVP_MD_CTX_new();if(!ctx||EVP_DigestVerifyInit(ctx,&pk,EVP_sha256(),NULL,key)<=0||EVP_PKEY_CTX_set_rsa_padding(pk,RSA_PKCS1_PADDING)<=0)goto done;
    ok=EVP_DigestVerify(ctx,signature,384,message,length)==1;
done:EVP_MD_CTX_free(ctx);EVP_PKEY_free(key);return ok;
}
