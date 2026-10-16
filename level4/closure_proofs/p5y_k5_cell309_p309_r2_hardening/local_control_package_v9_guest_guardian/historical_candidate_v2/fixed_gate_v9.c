/* Linux-only fixed idle gate. No workload argument, shell, arbitrary path,
 * D2 object or formal run authority. Authority requires the completed fixed manager start transaction. */
#define _GNU_SOURCE
#include "protocol.h"
#include "authority_binding.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
static int64_t clock_ns(void){struct timespec t;if(clock_gettime(CLOCK_BOOTTIME,&t))return -1;
    return (int64_t)t.tv_sec*1000000000LL+t.tv_nsec;}
static int parent_ok(void){int fd=open("/",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);if(fd<0)return 0;
    const char *parts[]={"run","rebaseguard-p309"};struct stat st;
    for(size_t i=0;i<2;i++){
        if(fstat(fd,&st)||!S_ISDIR(st.st_mode)||st.st_uid!=0||(st.st_mode&0022)){close(fd);return 0;}
        int next=openat(fd,parts[i],O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);close(fd);fd=next;if(fd<0)return 0;
    }
    int ok=!fstat(fd,&st)&&S_ISDIR(st.st_mode)&&st.st_uid==0&&!(st.st_mode&0022);
    ok=ok&&!fstatat(fd,"launch-gate-v9.sock",&st,AT_SYMLINK_NOFOLLOW)&&S_ISSOCK(st.st_mode)
       &&st.st_uid==0&&st.st_gid==getegid()&&(st.st_mode&0777)==0660;close(fd);return ok;
}
/* No ancillary descriptor or truncated frame may enter the unprivileged gate. */
static ssize_t receive(int sock,char raw[P309_PACKET_MAX]){
    union{struct cmsghdr align;char bytes[CMSG_SPACE(16*sizeof(int))];} control;
    struct iovec iov={raw,P309_PACKET_MAX};struct msghdr m={0};m.msg_iov=&iov;m.msg_iovlen=1;
    m.msg_control=control.bytes;m.msg_controllen=sizeof control.bytes;
    ssize_t n=recvmsg(sock,&m,MSG_CMSG_CLOEXEC|MSG_DONTWAIT);if(n<=0)return n;
    int bad=!!(m.msg_flags&(MSG_TRUNC|MSG_CTRUNC));
    for(struct cmsghdr *c=CMSG_FIRSTHDR(&m);c;c=CMSG_NXTHDR(&m,c)){
        bad=1;
        if(c->cmsg_level==SOL_SOCKET&&c->cmsg_type==SCM_RIGHTS&&c->cmsg_len>=CMSG_LEN(0)){
            size_t count=(c->cmsg_len-CMSG_LEN(0))/sizeof(int);int *fds=(int*)CMSG_DATA(c);
            for(size_t i=0;i<count;i++)close(fds[i]);
        }
    }
    if(bad){errno=EPROTO;return -1;}return n;
}
int main(int argc,char **argv){
    (void)argv;if(argc!=1||geteuid()==0)return 64;
    /* No broker/guardian/heartbeat/listener FD can survive into this process. */
    if(close_range(3,UINT_MAX,0)||!parent_ok())return 65;
    int64_t started=clock_ns();if(started<0)return 65;
    int sock=socket(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC|SOCK_NONBLOCK,0);if(sock<0)return 65;
    struct sockaddr_un a={0};a.sun_family=AF_UNIX;memcpy(a.sun_path,P309_GATE_SOCKET,sizeof P309_GATE_SOCKET);
    if(connect(sock,(struct sockaddr*)&a,offsetof(struct sockaddr_un,sun_path)+sizeof P309_GATE_SOCKET))return 66;
    struct ucred peer={0};socklen_t len=sizeof peer;
    if(getsockopt(sock,SOL_SOCKET,SO_PEERCRED,&peer,&len)||len!=sizeof peer||peer.uid!=0||peer.pid<1)return 66;
    /* UID0 and protected endpoint are necessary but not start authority. */
    char raw[P309_PACKET_MAX],g[33]={0},other[33];int bound=0;int64_t previous=started;
    for(;;){
        int64_t now=clock_ns();if(now<previous||now<0||now-started>=10000000000LL)return 70;previous=now;
        struct pollfd p={sock,POLLIN,0};int rc=poll(&p,1,50);
        if(rc<0){if(errno==EINTR)continue;return 71;}
        if(p.revents&(POLLHUP|POLLERR|POLLNVAL))return 71;
        if(!(p.revents&POLLIN))continue;
        ssize_t n=receive(sock,raw);if(n<=0)return 71;
        if(!bound){
            if(!p309_parse(raw,(size_t)n,"BIND",g))return 72;
            const struct p309_start_authority *authority=p309_authorize_gate(peer.pid);
            if(!authority||strcmp(p309_authority_generation(authority),g))return 78;
            size_t size=p309_packet(raw,"GATE_READY",g);
            if(send(sock,raw,size,MSG_NOSIGNAL|MSG_DONTWAIT)!=(ssize_t)size)return 72;
            bound=1;continue;
        }
        if(p309_parse(raw,(size_t)n,"CANCEL",other)&&!strcmp(g,other))return 73;
        if(!p309_parse(raw,(size_t)n,"RELEASE",other)||strcmp(g,other))return 72;
        now=clock_ns();if(now<previous||now<0||now-started>=10000000000LL)return 70;
        close(sock);if(close_range(3,UINT_MAX,0))return 74;
        char *const args[]={P309_IDLE,NULL};char *const env[]={"PATH=/usr/bin:/bin","LC_ALL=C","LANG=C",NULL};
        execve(P309_IDLE,args,env);return 75;
    }
}
