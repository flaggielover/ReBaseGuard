#define _GNU_SOURCE
#include "anchor_transport.h"
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
#define ENDPOINT "/run/rebaseguard-p309/host-anchor-v10.sock"
static int64_t now_ns(void){struct timespec t;if(clock_gettime(CLOCK_BOOTTIME,&t))return -1;return (int64_t)t.tv_sec*1000000000LL+t.tv_nsec;}
static int endpoint_ok(void){const char *paths[]={"/","/run","/run/rebaseguard-p309"};struct stat s;
    for(size_t i=0;i<3;i++)if(lstat(paths[i],&s)||!S_ISDIR(s.st_mode)||s.st_uid||(s.st_mode&0022))return 0;
    return !lstat(ENDPOINT,&s)&&S_ISSOCK(s.st_mode)&&s.st_uid==0&&(s.st_mode&0777)==0600;
}
static int exchange(const struct p309_start_control *control,const unsigned char *request,size_t length,unsigned char response[4480],size_t *out,unsigned char *second,size_t *second_out){
    if(!control||!request||!out||!length||length>4480||geteuid()!=0||p309_start_is_cancelled(control)||!endpoint_ok())return 0;
    *out=0;if(second_out)*second_out=0;int frame=0,ok=0;int64_t started=now_ns(),previous=started;if(started<0)return 0;
    int s=socket(AF_UNIX,SOCK_SEQPACKET|SOCK_NONBLOCK|SOCK_CLOEXEC,0);if(s<0)return 0;
    struct sockaddr_un address={0};address.sun_family=AF_UNIX;memcpy(address.sun_path,ENDPOINT,sizeof ENDPOINT);
    if(connect(s,(struct sockaddr*)&address,offsetof(struct sockaddr_un,sun_path)+sizeof ENDPOINT))goto done;
    struct ucred peer={0};socklen_t peerlen=sizeof peer;if(getsockopt(s,SOL_SOCKET,SO_PEERCRED,&peer,&peerlen)||peerlen!=sizeof peer||peer.uid!=0)goto done;
    if(p309_start_is_cancelled(control)||send(s,request,length,MSG_DONTWAIT|MSG_NOSIGNAL)!=(ssize_t)length)goto done;
    for(;;){int64_t now=now_ns();if(now<previous||now-started>=2000000000LL||p309_start_is_cancelled(control))goto done;previous=now;
        struct pollfd p={s,POLLIN,0};int rc=poll(&p,1,50);if(rc<0){if(errno==EINTR)continue;goto done;}
        if(p.revents&(POLLERR|POLLNVAL))goto done;
        if((p.revents&POLLHUP)&&!(p.revents&POLLIN))goto done;if(!(p.revents&POLLIN))continue;
        union{struct cmsghdr align;char bytes[CMSG_SPACE(16*sizeof(int))];}ancillary;
        struct iovec i={frame?second:response,4480};struct msghdr m={0};m.msg_iov=&i;m.msg_iovlen=1;m.msg_control=ancillary.bytes;m.msg_controllen=sizeof ancillary.bytes;
        ssize_t n=recvmsg(s,&m,MSG_DONTWAIT|MSG_CMSG_CLOEXEC);if(n<=384)goto done;int bad=!!(m.msg_flags&(MSG_TRUNC|MSG_CTRUNC));
        for(struct cmsghdr *c=CMSG_FIRSTHDR(&m);c;c=CMSG_NXTHDR(&m,c)){bad=1;
            if(c->cmsg_level==SOL_SOCKET&&c->cmsg_type==SCM_RIGHTS&&c->cmsg_len>=CMSG_LEN(0)){
                size_t count=(c->cmsg_len-CMSG_LEN(0))/sizeof(int);int *fds=(int*)CMSG_DATA(c);for(size_t j=0;j<count;j++)close(fds[j]);}}
        now=now_ns();if(bad||now<previous||now-started>=2000000000LL||p309_start_is_cancelled(control))goto done;
        if(!frame){*out=(size_t)n;if(second){frame=1;continue;}}else *second_out=(size_t)n;
        ok=1;break;
    }
done:close(s);return ok;
}
int p309_host_exchange(const struct p309_start_control *c,const unsigned char *r,size_t n,unsigned char out[4480],size_t *len){return exchange(c,r,n,out,len,NULL,NULL);}
int p309_host_reserve_exchange(const struct p309_start_control *c,const unsigned char *r,size_t n,unsigned char context[4480],size_t *clen,unsigned char ack[4480],size_t *alen){
    if(!ack||!alen)return 0;return exchange(c,r,n,context,clen,ack,alen);
}
