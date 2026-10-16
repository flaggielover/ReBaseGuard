// Offline ETL reader only. No StartTrace/ControlTrace/EnableTrace/session APIs.
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <evntrace.h>
#include <evntcons.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
static FILE* sink;
static unsigned long long total, switches, unknown;
static const GUID threadGuid={0x3d6fa8d1,0xfe05,0x11d0,{0x9d,0xda,0x00,0xc0,0x4f,0xd7,0xba,0x7c}};
static void WINAPI Receive(PEVENT_RECORD e) {
    ++total;
    if(memcmp(&e->EventHeader.ProviderId,&threadGuid,sizeof(GUID))!=0 ||
       e->EventHeader.EventDescriptor.Opcode!=36) return;
    const BYTE version=e->EventHeader.EventDescriptor.Version;
    if(!((version==2 && e->UserDataLength==24)||(version==5 && e->UserDataLength==28))) {++unknown;return;}
    uint32_t incoming=0,outgoing=0;
    memcpy(&incoming,e->UserData,4);memcpy(&outgoing,(BYTE*)e->UserData+4,4);
    // First two fields follow Microsoft TraceEvent's CSwitch decoder.
    // Unknown versions/lengths remain unparsed; never infer full CPU accounting.
    fprintf(sink,"%lld,%u,%u,%u,%u,%u\n",e->EventHeader.TimeStamp.QuadPart,
        e->BufferContext.ProcessorNumber,incoming,outgoing,version,e->UserDataLength);
    ++switches;
}
int wmain(int argc,wchar_t** argv) {
    if(argc!=3) return 64;
    if(_wfopen_s(&sink,argv[2],L"wx")!=0 || !sink) return 65;
    setvbuf(sink,NULL,_IOFBF,1048576);
    fprintf(sink,"clock_100ns,cpu,new_tid,old_tid,version,length\n");
    EVENT_TRACE_LOGFILEW input={0};
    input.LogFileName=argv[1];
    input.ProcessTraceMode=PROCESS_TRACE_MODE_EVENT_RECORD; // NOT REAL_TIME
    input.EventRecordCallback=Receive;
    TRACEHANDLE trace=OpenTraceW(&input);
    if(trace==INVALID_PROCESSTRACE_HANDLE){fprintf(stderr,"OpenTrace=%lu\n",GetLastError());fclose(sink);return 66;}
    unsigned long lost=input.LogfileHeader.EventsLost;
    unsigned long processors=input.LogfileHeader.NumberOfProcessors;
    ULONG rc=ProcessTrace(&trace,1,NULL,NULL);
    ULONG closeRc=CloseTrace(trace);
    int io=ferror(sink);
    if(fclose(sink)!=0)io=1;
    printf("{\"scope\":\"OFFLINE_ETL_CSWITCH_PREFIX_ONLY\",\"process_trace_rc\":%lu,\"close_trace_rc\":%lu,\"events\":%llu,\"decoded_cswitch\":%llu,\"unknown_cswitch\":%llu,\"header_events_lost\":%lu,\"processors\":%lu,\"output_error\":%d,\"admission\":\"BLOCKED\"}\n",
        rc,closeRc,total,switches,unknown,lost,processors,io);
    return rc==0 && closeRc==0 && io==0 && unknown==0?0:1;
}
