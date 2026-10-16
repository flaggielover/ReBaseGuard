#define UNICODE
#define _UNICODE
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <evntrace.h>
#include <evntcons.h>
#include <stdio.h>
#include <stdint.h>
#include <limits.h>
#include <string.h>

// Fixed reference: Microsoft PerfView 65026df... KernelTraceEventParser.cs
// SHA256 2245ccc62b0d933190068a18344bc64749a2893bd9740a79706ba7fe5e86c778
// CSwitch OldThreadState = byte 0xe. This is a prefix extractor, not TDH or
// a claim that the full event payload/CPU topology has been validated.
static const GUID threadGuid={0x3d6fa8d1,0xfe05,0x11d0,{0x9d,0xda,0,0xc0,0x4f,0xd7,0xba,0x7c}};
static FILE* sink=nullptr;
static uint64_t total=0,cswitch=0,threadEvents=0,unknownCswitch=0,unknownThread=0;
static uint64_t stateCounts[256]={0},opCounts[5]={0},version2=0,version5=0,headerPayloadMismatch[5]={0};
static uint64_t indexEvents=0,numberEvents=0,outputErrors=0;
static LONGLONG firstQpc=LLONG_MAX,lastQpc=0;
static unsigned maxEffectiveCpu=0;
static uint32_t U32(const BYTE* data){uint32_t out;memcpy(&out,data,sizeof(out));return out;}

static void WINAPI Receive(EVENT_RECORD* record){
 ++total;
 const auto& h=record->EventHeader;
 const auto qpc=h.TimeStamp.QuadPart;
 if(qpc<firstQpc)firstQpc=qpc;if(qpc>lastQpc)lastQpc=qpc;
 if(!IsEqualGUID(h.ProviderId,threadGuid))return;
 const unsigned op=h.EventDescriptor.Opcode,v=h.EventDescriptor.Version,n=record->UserDataLength;
 const BYTE* p=(const BYTE*)record->UserData;
 unsigned kind=0,newTid=0,oldTid=0,payloadPid=0,payloadTid=0;int oldState=-1;
 if(op==36){
  if(!p||!((v==2&&n==24)||(v==5&&n==28))){++unknownCswitch;return;}
  kind=1;newTid=U32(p);oldTid=U32(p+4);oldState=p[0xe];++stateCounts[oldState];
  ++cswitch;if(v==2)++version2;else ++version5;
 }else if(op>=1&&op<=4){
  if(!p||v!=3||n<8){++unknownThread;return;}
  kind=2;payloadPid=U32(p);payloadTid=U32(p+4);++threadEvents;++opCounts[op];
  if(payloadPid!=h.ProcessId||payloadTid!=h.ThreadId)++headerPayloadMismatch[op];
 }else return;
 const bool index=(h.Flags&EVENT_HEADER_FLAG_PROCESSOR_INDEX)!=0;
 const unsigned effective=index?record->BufferContext.ProcessorIndex:record->BufferContext.ProcessorNumber;
 if(index)++indexEvents;else ++numberEvents;if(effective>maxEffectiveCpu)maxEffectiveCpu=effective;
 // Retain both raw union interpretations and the discriminator, never infer
 // equality between processor-number and processor-index namespaces.
 if(fprintf(sink,"%u,%llu,%lld,%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%d,%u,%u,%lu,%lu\n",
     kind,total,qpc,index?1:0,effective,record->BufferContext.ProcessorIndex,
     record->BufferContext.ProcessorNumber,h.Flags,op,v,n,newTid,oldTid,oldState,
     payloadPid,payloadTid,h.ProcessId,h.ThreadId)<0)++outputErrors;
}

int wmain(int argc,wchar_t** argv){
 if(argc!=3)return 64;
 if(_wfopen_s(&sink,argv[2],L"wx")!=0||!sink)return 65;
 setvbuf(sink,nullptr,_IOFBF,1048576);
 if(fprintf(sink,"kind,event_sequence,qpc,cpu_index_flag,cpu_effective,cpu_processor_index,cpu_processor_number,event_header_flags,opcode,version,payload_bytes,new_tid,old_tid,old_state_byte,payload_pid,payload_tid,header_pid,header_tid\n")<0){fclose(sink);return 66;}
 EVENT_TRACE_LOGFILEW log={};log.LogFileName=argv[1];
 log.ProcessTraceMode=PROCESS_TRACE_MODE_EVENT_RECORD|PROCESS_TRACE_MODE_RAW_TIMESTAMP;
 log.EventRecordCallback=Receive;
 TRACEHANDLE handle=OpenTraceW(&log);
 if(handle==INVALID_PROCESSTRACE_HANDLE){fprintf(stderr,"OpenTrace=%lu\n",GetLastError());fclose(sink);return 67;}
 const TRACE_LOGFILE_HEADER h=log.LogfileHeader;
 if(h.ReservedFlags!=1||h.PerfFreq.QuadPart<=0){ULONG close=CloseTrace(handle);fclose(sink);fprintf(stderr,"unsupported clock; CloseTrace=%lu\n",close);return 68;}
 ULONG processRc=ProcessTrace(&handle,1,nullptr,nullptr),closeRc=CloseTrace(handle);
 int io=ferror(sink);if(fclose(sink)!=0)io=1;
 printf("{\"scope\":\"SAVED_ETL_CSWITCH_STATE_THREAD_DUAL_IDENTITY_PREFIX_ONLY\",\"events\":%llu,\"cswitch_rows\":%llu,\"thread_rows\":%llu,\"decoded_rows\":%llu,\"unknown_cswitch_prefix\":%llu,\"unknown_thread_prefix\":%llu,\"cswitch_v2_rows\":%llu,\"cswitch_v5_rows\":%llu,\"clock_type\":%lu,\"qpc_frequency\":%lld,\"first_qpc\":%lld,\"last_qpc\":%lld,\"header_start_filetime\":%lld,\"header_end_filetime\":%lld,\"header_events_lost\":%lu,\"header_buffers_lost\":%lu,\"processors\":%lu,\"cpu_index_events\":%llu,\"cpu_number_events\":%llu,\"max_effective_cpu\":%u,\"process_rc\":%lu,\"close_rc\":%lu,\"output_error\":%d,\"output_write_failures\":%llu,\"thread_header_payload_mismatch_by_opcode\":[%llu,%llu,%llu,%llu],\"old_state_byte_counts\":[",
  total,cswitch,threadEvents,cswitch+threadEvents,unknownCswitch,unknownThread,version2,version5,
  h.ReservedFlags,h.PerfFreq.QuadPart,firstQpc,lastQpc,h.StartTime.QuadPart,h.EndTime.QuadPart,
  h.EventsLost,h.BuffersLost,h.NumberOfProcessors,indexEvents,numberEvents,maxEffectiveCpu,
  processRc,closeRc,io,outputErrors,headerPayloadMismatch[1],headerPayloadMismatch[2],headerPayloadMismatch[3],headerPayloadMismatch[4]);
 for(unsigned i=0;i<256;i++)printf("%s%llu",i?",":"",stateCounts[i]);
 printf("],\"thread_prefix_only\":true,\"cpu_topology_proven\":false,\"ownership_extended\":false,\"admission\":\"BLOCKED\"}\n");
 return processRc==0&&closeRc==0&&io==0&&outputErrors==0&&unknownCswitch==0&&unknownThread==0?0:1;
}
