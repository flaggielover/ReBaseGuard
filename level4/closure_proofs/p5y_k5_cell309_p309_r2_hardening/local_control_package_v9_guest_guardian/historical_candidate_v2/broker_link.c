/* Linux broker-internal FD handoff and gate release. Not an executable. */
#define _GNU_SOURCE
#include "broker_link.h"
#include "protocol.h"
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <pwd.h>
#include <pthread.h>
#include <signal.h>
#include <stdint.h>
#include <stdatomic.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <time.h>
#include <unistd.h>
/* Immutable handles after publication. They and this one bounded object remain
 * alive until explicit destroy AFTER all broker threads have been joined.
 * Retirement never closes/recycles a descriptor that STOP may still use. */
struct p309_guardian_link {const struct p309_start_authority *authority;int socket,heartbeat,killfd,guardian_pidfd;
    atomic_int write_state,retire_attempted,retired,release_active;};
static int64_t now_ns(void){struct timespec t;if(clock_gettime(CLOCK_BOOTTIME,&t))return -1;return (int64_t)t.tv_sec*1000000000LL+t.tv_nsec;}
static int send_frame(int s,const char *verb,const char *g){char b[P309_PACKET_MAX];size_t n=p309_packet(b,verb,g);return n&&send(s,b,n,MSG_DONTWAIT|MSG_NOSIGNAL)==(ssize_t)n;}
static int receipt(int s,const char *verb,const char *g){int64_t start=now_ns();if(start<0)return 0;
    for(;;){int64_t now=now_ns();if(now<start||now-start>=2000000000LL)return 0;struct pollfd p={s,POLLIN,0};
        int rc=poll(&p,1,50);if(rc<0){if(errno==EINTR)continue;return 0;}if(p.revents&(POLLHUP|POLLERR|POLLNVAL))return 0;if(!(p.revents&POLLIN))continue;
        char buf[P309_PACKET_MAX],other[33];union{struct cmsghdr align;char raw[CMSG_SPACE(16*sizeof(int))];}c;
        struct iovec i={buf,sizeof buf};struct msghdr m={0};m.msg_iov=&i;m.msg_iovlen=1;m.msg_control=c.raw;m.msg_controllen=sizeof c.raw;
        ssize_t n=recvmsg(s,&m,MSG_DONTWAIT|MSG_CMSG_CLOEXEC);if(n<=0)return 0;int bad=!!(m.msg_flags&(MSG_TRUNC|MSG_CTRUNC));
        for(struct cmsghdr *h=CMSG_FIRSTHDR(&m);h;h=CMSG_NXTHDR(&m,h)){bad=1;if(h->cmsg_level==SOL_SOCKET&&h->cmsg_type==SCM_RIGHTS&&h->cmsg_len>=CMSG_LEN(0)){
            int *fds=(int*)CMSG_DATA(h);size_t count=(h->cmsg_len-CMSG_LEN(0))/sizeof(int);for(size_t k=0;k<count;k++)close(fds[k]);}}
        now=now_ns();return !bad&&now>=start&&now-start<2000000000LL&&p309_parse(buf,(size_t)n,verb,other)&&!strcmp(other,g);
    }
}
static int endpoint_ok(void){const char *paths[]={"/","/run","/run/rebaseguard-p309"};struct stat st;
    for(size_t i=0;i<3;i++)if(lstat(paths[i],&st)||!S_ISDIR(st.st_mode)||st.st_uid!=0||(st.st_mode&0022))return 0;
    return !lstat(P309_GUARD_SOCKET,&st)&&S_ISSOCK(st.st_mode)&&st.st_uid==0&&(st.st_mode&0777)==0600;}
int p309_guardian_request_stop(struct p309_guardian_link *l){if(!l)return -EINVAL;
    p309_authority_stop(l->authority); /* atomic latch BEFORE any syscall */
    int expected=0;if(!atomic_compare_exchange_strong(&l->write_state,&expected,1))
        return expected==2?0:expected==1?-EINPROGRESS:-EIO;
    int ok=write(l->killfd,"1\n",2)==2;atomic_store(&l->write_state,ok?2:3);
    (void)send_frame(l->socket,"STOP",p309_authority_generation(l->authority));return ok?0:-EIO;
}
int p309_guardian_bind(const struct p309_start_authority *a,struct p309_guardian_link **out){*out=NULL;int fds[5],pipes[2]={-1,-1};
    if(geteuid()!=0||p309_authority_fds(a,fds)||!p309_authority_current(a)||!endpoint_ok()||!p309_authority_claim_handoff(a))return -EPERM;
    if(pipe2(pipes,O_CLOEXEC|O_NONBLOCK))return -errno;fds[4]=pipes[0];
    int s=socket(AF_UNIX,SOCK_SEQPACKET|SOCK_NONBLOCK|SOCK_CLOEXEC,0);if(s<0){close(pipes[0]);close(pipes[1]);return -errno;}
    struct sockaddr_un addr={0};addr.sun_family=AF_UNIX;memcpy(addr.sun_path,P309_GUARD_SOCKET,sizeof P309_GUARD_SOCKET);
    if(connect(s,(struct sockaddr*)&addr,offsetof(struct sockaddr_un,sun_path)+sizeof P309_GUARD_SOCKET))goto fail;
    struct ucred peer={0};socklen_t len=sizeof peer;
    /* Socket activation peer may be PID1; require protected root endpoint, not
     * the mistaken assumption that SO_PEERCRED reports final guardian PID. */
    if(getsockopt(s,SOL_SOCKET,SO_PEERCRED,&peer,&len)||len!=sizeof peer||peer.uid!=0)goto fail;
    char raw[P309_PACKET_MAX];size_t n=p309_packet(raw,"BIND",p309_authority_generation(a));
    union{struct cmsghdr align;char bytes[CMSG_SPACE(sizeof fds)];}control={0};struct iovec i={raw,n};struct msghdr m={0};
    m.msg_iov=&i;m.msg_iovlen=1;m.msg_control=control.bytes;m.msg_controllen=sizeof control.bytes;struct cmsghdr *c=CMSG_FIRSTHDR(&m);
    c->cmsg_level=SOL_SOCKET;c->cmsg_type=SCM_RIGHTS;c->cmsg_len=CMSG_LEN(sizeof fds);memcpy(CMSG_DATA(c),fds,sizeof fds);
    if(sendmsg(s,&m,MSG_DONTWAIT|MSG_NOSIGNAL)!=(ssize_t)n)goto fail;
    close(pipes[0]);pipes[0]=-1;
    if(!receipt(s,"READY",p309_authority_generation(a))||!p309_authority_current(a))goto fail;
    struct p309_guardian_link *l=calloc(1,sizeof *l);if(!l)goto fail;
    l->guardian_pidfd=p309_guardian_pidfd();if(l->guardian_pidfd<0){free(l);goto fail;}
    if(!p309_authority_note_guardian_ready(a,l->guardian_pidfd)){close(l->guardian_pidfd);p309_guardian_release_reference();free(l);goto fail;}
    l->authority=a;l->socket=s;l->heartbeat=pipes[1];l->killfd=fds[3];
    atomic_init(&l->write_state,0);atomic_init(&l->retire_attempted,0);atomic_init(&l->retired,0);atomic_init(&l->release_active,0);
    *out=l;if(p309_authority_stopped(a)){(void)p309_guardian_request_stop(l);return -ECANCELED;}return 0;
fail:
    if(pipes[0]>=0)close(pipes[0]);if(pipes[1]>=0)close(pipes[1]);close(s);
    /* Actual owned start already exists: held killFD is legitimate fallback.
     * No pathname reopen or name-based kill; caller records cleanup UNKNOWN. */
    p309_authority_stop(a);(void)write(fds[3],"1\n",2);return -EIO;
}
int p309_release_fixed_gate(struct p309_guardian_link *l,int gate){
    if(!l){if(gate>=0)close(gate);return -EPERM;}
    if(atomic_exchange(&l->release_active,1)){if(gate>=0)close(gate);(void)p309_guardian_request_stop(l);return -EPERM;}
    if(!p309_authority_release_begin(l->authority)){if(gate>=0)close(gate);(void)p309_guardian_request_stop(l);atomic_store(&l->release_active,0);return -EPERM;}
    if(!p309_authority_current(l->authority)||!p309_authority_release_pending(l->authority))goto fail;
    struct ucred peer={0};socklen_t len=sizeof peer;struct passwd pw,*found=NULL;char buf[16384];
    if(getpwnam_r("p309-runner",&pw,buf,sizeof buf,&found)||!found||pw.pw_uid==0
       ||getsockopt(gate,SOL_SOCKET,SO_PEERCRED,&peer,&len)||len!=sizeof peer
       ||peer.uid!=pw.pw_uid||peer.pid!=p309_authority_worker_pid(l->authority))goto fail;
    const char *g=p309_authority_generation(l->authority);
    if(!p309_authority_release_pending(l->authority)||!send_frame(gate,"BIND",g)||!receipt(gate,"GATE_READY",g)
       ||!p309_authority_release_pending(l->authority)||!p309_authority_current(l->authority)
       ||!p309_authority_release_pending(l->authority))goto fail;
    /* REQUIRED host final consume-ACK verification is wired below. Never
     * substitute the local permit or READY transport frame for host authority. */
    if(!p309_authority_host_ack_consume(l->authority)||!p309_authority_release_pending(l->authority))goto fail;
    /* Dispatch CAS is the linearization point, not a success claim. STOP before
     * this CAS forbids send. STOP after it is an in-flight release: retained
     * killFD still stops the generation, and this call reports cancellation.
     * No manager, disk, ACK or blocking syscall occurs between CAS and send. */
    if(!p309_authority_release_commit(l->authority))goto fail;
    if(!send_frame(gate,"RELEASE",g))goto fail;close(gate);atomic_store(&l->release_active,0);
    return p309_authority_stopped(l->authority)?-ECANCELED:0;
fail:
    if(gate>=0)close(gate);(void)p309_guardian_request_stop(l);atomic_store(&l->release_active,0);return -EIO;
}
static ssize_t heartbeat_write(int fd){
    sigset_t block,old,pending;sigemptyset(&block);sigaddset(&block,SIGPIPE);
    if(pthread_sigmask(SIG_BLOCK,&block,&old))return -1;
    if(sigpending(&pending)){pthread_sigmask(SIG_SETMASK,&old,NULL);return -1;}
    int already=sigismember(&pending,SIGPIPE);ssize_t n=write(fd,"H",1);int saved=errno;
    if(n<0&&saved==EPIPE&&!already){struct timespec zero={0};while(sigtimedwait(&block,NULL,&zero)<0&&errno==EINTR){}}
    pthread_sigmask(SIG_SETMASK,&old,NULL);errno=saved;return n;
}
int p309_guardian_heartbeat(struct p309_guardian_link *l){
    if(!l||p309_authority_stopped(l->authority)||atomic_load(&l->retired))return -EPERM;
    /* Caller must only call after current monitor/host safety checks. This is
     * not an unconditional timer and does not create continuation authority. */
    if(heartbeat_write(l->heartbeat)!=1){(void)p309_guardian_request_stop(l);return -EIO;}return p309_authority_stopped(l->authority)?-ECANCELED:0;
}

int p309_guardian_retire(struct p309_guardian_link *l){
    if(!l||!p309_authority_stopped(l->authority)||atomic_load(&l->write_state)!=2||atomic_load(&l->release_active)
       ||atomic_exchange(&l->retire_attempted,1))return -EPERM;
    const char *g=p309_authority_generation(l->authority);
    /* One bounded attempt; errors leave all ownership/stop fences intact.
     * Full broker must not turn lost receipts into a retry or STOPPED claim. */
    if(!receipt(l->socket,"STOP_REQUESTED",g)||!receipt(l->socket,"LOCAL_QUIESCENT",g)
       ||!p309_authority_cleanup_observed(l->authority)||!send_frame(l->socket,"RETIRE",g)
       ||!receipt(l->socket,"RETIRING",g))return -EIO;
    int64_t start=now_ns();if(start<0)return -EIO;
    for(;;){struct pollfd p={l->guardian_pidfd,POLLIN,0};int n=poll(&p,1,50);
        if(n<0&&errno!=EINTR)return -EIO;if(n==1){if(p.revents!=POLLIN)return -EIO;break;}
        int64_t now=now_ns();if(now<start||now-start>=2000000000LL)return -ETIMEDOUT;
    }
    if(!p309_guardian_cleanup_observed(l->guardian_pidfd))return -EIO;
    p309_guardian_release_reference();
    atomic_store(&l->retired,1);return 0;
}
int p309_guardian_destroy_after_join(struct p309_guardian_link *l){
    /* Only the broker owner, AFTER joining every user of this pointer and the
     * start control. This is explicit object destruction, never the STOP path. */
    if(!l||!atomic_load(&l->retired))return -EPERM;
    close(l->heartbeat);close(l->socket);close(l->guardian_pidfd);free(l);return 0;
}
