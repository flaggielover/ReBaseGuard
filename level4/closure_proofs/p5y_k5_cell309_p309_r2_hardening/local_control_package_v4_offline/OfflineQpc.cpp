#define UNICODE
#define _UNICODE
#include <windows.h>
#include <evntrace.h>
#include <evntcons.h>
#include <stdio.h>
#include <stdint.h>
#include <limits.h>
#include <string.h>
static const GUID threadGuid={0x3d6fa8d1,0xfe05,0x11d0,{0x9d,0xda,0,0xc0,0x4f,0xd7,0xba,0x7c}};
static const GUID processGuid={0x3d6fa8d0,0xfe05,0x11d0,{0x9d,0xda,0,0xc0,0x4f,0xd7,0xba,0x7c}};
static const GUID perfGuid={0xce1dbfb4,0x137e,0x4da6,{0x87,0xb0,0x3f,0x59,0xaa,0x10,0x2c,0xbc}};
struct Row {unsigned kind=0; uint64_t a=0,b=0,c=0;};
static uint32_t U32(const BYTE*p){uint32_t x;memcpy(&x,p,4);return x;}
static uint64_t U64(const BYTE*p){uint64_t x;memcpy(&x,p,8);return x;}
// 0 irrelevant, 1 supported finite prefix, -1 unsupported/malformed required prefix.
static int Decode(const EVENT_RECORD& e,Row& r){
 const auto& h=e.EventHeader;const BYTE* p=(const BYTE*)e.UserData;
 const unsigned op=h.EventDescriptor.Opcode,v=h.EventDescriptor.Version,n=e.UserDataLength;
 const bool is32=(h.Flags&EVENT_HEADER_FLAG_32_BIT_HEADER)!=0;
 const bool is64=(h.Flags&EVENT_HEADER_FLAG_64_BIT_HEADER)!=0;
 if(IsEqualGUID(h.ProviderId,threadGuid)&&op==36){
  if(!p||!((v==2&&n==24)||(v==5&&n==28)))return -1;
  r={1,U32(p),U32(p+4),0};return 1;
 }
 if(IsEqualGUID(h.ProviderId,threadGuid)&&op>=1&&op<=4){
  if(!p||v!=3||n<8)return -1;r={3,U32(p),U32(p+4),0};return 1;
 }
 if(IsEqualGUID(h.ProviderId,processGuid)&&op>=1&&op<=4){
  if(!p||v!=4||is32==is64)return -1;
  const unsigned ptr=is64?8:4,flagAt=24+2*(ptr-4);
  if(n<flagAt+4)return -1;
  r={4,is64?U64(p):U32(p),U32(p+ptr),U32(p+flagAt)};return 1;
 }
 if(IsEqualGUID(h.ProviderId,perfGuid)&&(op==50||op==66||op==67||op==68||op==69)){
  if(!p||v!=2||is32==is64)return -1;
  const unsigned ptr=is64?8:4,min=(op==50||op==67)?12+ptr:8+ptr;
  if(n<min)return -1;
  r={op==66?5u:2u,U64(p),0,0};return 1;
 }
 return 0;
}
static FILE* sink;static uint64_t total=0,decoded=0,unknown=0,indexEvents=0,numberEvents=0;
static LONGLONG low=LLONG_MAX,high=0;static unsigned maxCpu=0;
static void WINAPI Receive(EVENT_RECORD* e){
 ++total;if(e->EventHeader.TimeStamp.QuadPart<low)low=e->EventHeader.TimeStamp.QuadPart;
 if(e->EventHeader.TimeStamp.QuadPart>high)high=e->EventHeader.TimeStamp.QuadPart;
 Row r;int result=Decode(*e,r);if(result==0)return;if(result<0){++unknown;return;}
 bool idx=(e->EventHeader.Flags&EVENT_HEADER_FLAG_PROCESSOR_INDEX)!=0;
 unsigned cpu=idx?e->BufferContext.ProcessorIndex:e->BufferContext.ProcessorNumber;
 if(idx)++indexEvents;else ++numberEvents;if(cpu>maxCpu)maxCpu=cpu;
 fprintf(sink,"%u,%lld,%u,%u,%llu,%llu,%llu,%u\n",r.kind,e->EventHeader.TimeStamp.QuadPart,cpu,e->EventHeader.EventDescriptor.Opcode,r.a,r.b,r.c,idx?1:0);++decoded;
}
static int Check(){
 BYTE data[80]={0};data[0]=7;data[4]=9;EVENT_RECORD e={};e.UserData=data;e.EventHeader.ProviderId=threadGuid;e.EventHeader.EventDescriptor.Opcode=36;e.EventHeader.EventDescriptor.Version=5;e.UserDataLength=28;
 Row r;if(Decode(e,r)!=1||r.a!=7||r.b!=9)return 1;
 e.UserDataLength=7;if(Decode(e,r)!=-1)return 2;
 e.UserDataLength=28;e.EventHeader.EventDescriptor.Version=6;if(Decode(e,r)!=-1)return 3;
 e.EventHeader.EventDescriptor.Opcode=1;e.EventHeader.EventDescriptor.Version=3;e.UserDataLength=8;if(Decode(e,r)!=1||r.kind!=3)return 4;
 e.UserData=nullptr;if(Decode(e,r)!=-1)return 5;e.UserData=data;
 e.EventHeader.ProviderId=processGuid;e.EventHeader.EventDescriptor.Version=4;e.EventHeader.Flags=EVENT_HEADER_FLAG_64_BIT_HEADER;e.UserDataLength=36;if(Decode(e,r)!=1||r.kind!=4)return 6;
 e.UserDataLength=35;if(Decode(e,r)!=-1)return 7;
 e.EventHeader.Flags|=EVENT_HEADER_FLAG_32_BIT_HEADER;e.UserDataLength=36;if(Decode(e,r)!=-1)return 8;
 e.EventHeader.ProviderId=perfGuid;e.EventHeader.Flags=EVENT_HEADER_FLAG_64_BIT_HEADER;e.EventHeader.EventDescriptor.Version=2;e.EventHeader.EventDescriptor.Opcode=68;e.UserDataLength=16;if(Decode(e,r)!=1||r.kind!=2)return 9;
 e.UserDataLength=15;if(Decode(e,r)!=-1)return 10;
 e.UserDataLength=16;e.EventHeader.EventDescriptor.Opcode=66;if(Decode(e,r)!=1||r.kind!=5)return 11;
 e.EventHeader.EventDescriptor.Opcode=255;if(Decode(e,r)!=0)return 12;
 puts("12_PREFIX_MEMORY_CHECKS_NO_ETL_OR_HOST_API");return 0;
}
int wmain(int argc,wchar_t**argv){
 if(argc==2&&wcscmp(argv[1],L"--memory-check")==0)return Check();
 if(argc!=3)return 64;
 if(_wfopen_s(&sink,argv[2],L"wx")!=0||!sink)return 65;
 setvbuf(sink,NULL,_IOFBF,1048576);fprintf(sink,"kind,qpc,cpu,opcode,a,b,c,cpu_index_flag\n");
 EVENT_TRACE_LOGFILEW log={};log.LogFileName=argv[1];log.ProcessTraceMode=PROCESS_TRACE_MODE_EVENT_RECORD|PROCESS_TRACE_MODE_RAW_TIMESTAMP;log.EventRecordCallback=Receive;
 TRACEHANDLE handle=OpenTraceW(&log);
 if(handle==INVALID_PROCESSTRACE_HANDLE){fprintf(stderr,"OpenTrace=%lu\n",GetLastError());fclose(sink);return 66;}
 const TRACE_LOGFILE_HEADER h=log.LogfileHeader;
 if(h.ReservedFlags!=1||h.PerfFreq.QuadPart<=0){CloseTrace(handle);fclose(sink);fprintf(stderr,"unsupported raw clock\n");return 67;}
 ULONG rc=ProcessTrace(&handle,1,NULL,NULL),close=CloseTrace(handle);int io=ferror(sink);if(fclose(sink)!=0)io=1;
 printf("{\"scope\":\"OFFLINE_QPC_PREFIX_ONLY\",\"events\":%llu,\"decoded\":%llu,\"unknown_required_prefix\":%llu,\"clock_type\":%lu,\"qpc_frequency\":%lld,\"first_qpc\":%lld,\"last_qpc\":%lld,\"header_start_filetime\":%lld,\"header_end_filetime\":%lld,\"header_events_lost\":%lu,\"header_buffers_lost\":%lu,\"processors\":%lu,\"cpu_index_events\":%llu,\"cpu_number_events\":%llu,\"max_cpu\":%u,\"process_rc\":%lu,\"close_rc\":%lu,\"output_error\":%d,\"admission\":\"BLOCKED\"}\n",total,decoded,unknown,h.ReservedFlags,h.PerfFreq.QuadPart,low,high,h.StartTime.QuadPart,h.EndTime.QuadPart,h.EventsLost,h.BuffersLost,h.NumberOfProcessors,indexEvents,numberEvents,maxCpu,rc,close,io);
 return rc==0&&close==0&&io==0&&unknown==0?0:1;
}
