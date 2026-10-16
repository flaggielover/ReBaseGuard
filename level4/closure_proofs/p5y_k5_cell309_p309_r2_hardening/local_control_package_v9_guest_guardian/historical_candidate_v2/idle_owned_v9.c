/* Fixed native idle payload only. No process spawning or target entrypoint. */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <poll.h>
#include <time.h>
#include <unistd.h>
static int64_t now_ms(void){struct timespec t;if(clock_gettime(CLOCK_BOOTTIME,&t))return -1;return (int64_t)t.tv_sec*1000+t.tv_nsec/1000000;}
int main(int argc,char **argv){(void)argv;if(argc!=1||geteuid()==0)return 64;
    int64_t start=now_ms(),last=start;if(start<0)return 65;
    for(;;){int64_t now=now_ms();if(now<0||now<last)return 65;if(now-start>=120000)return 0;last=now;
        if(poll(0,0,100)<0&&errno!=EINTR)return 66;
    }
}
