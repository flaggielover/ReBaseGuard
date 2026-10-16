// PREPARED DIAGNOSTIC ONLY. --probe-approved creates ONE real WHP partition.
// --layout-check only checks compile-time structures; it does not load WHP.
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <WinHvPlatform.h>
#include <stdio.h>
#include <string.h>
#include <io.h>

struct Api {
    decltype(&WHvCreatePartition) create;
    decltype(&WHvSetPartitionProperty) property;
    decltype(&WHvSetupPartition) setup;
    decltype(&WHvMapGpaRange) map;
    decltype(&WHvUnmapGpaRange) unmap;
    decltype(&WHvCreateVirtualProcessor) createVp;
    decltype(&WHvSetVirtualProcessorRegisters) registers;
    decltype(&WHvGetVirtualProcessorCounters) counters;
    decltype(&WHvRunVirtualProcessor) run;
    decltype(&WHvCancelRunVirtualProcessor) cancel;
    decltype(&WHvDeleteVirtualProcessor) deleteVp;
    decltype(&WHvDeletePartition) destroy;
};
static Api api;
static WHV_PARTITION_HANDLE partition;
static bool partitionOwned;
static HRESULT AcquirePartition() {
    if(partitionOwned || partition) return E_UNEXPECTED;
    WHV_PARTITION_HANDLE candidate=NULL;
    HRESULT hr=api.create(&candidate);
    if(hr!=S_OK) return hr; // failure output is never adopted or destroyed
    if(!candidate) return E_UNEXPECTED;
    partition=candidate;partitionOwned=true;return S_OK;
}
static HRESULT fakeResult;
static WHV_PARTITION_HANDLE fakeOutput;
static HRESULT WINAPI FakeCreate(WHV_PARTITION_HANDLE* out) {*out=fakeOutput;return fakeResult;}
static int OwnershipMemoryChecks() {
    api.create=FakeCreate;
    const HRESULT codes[]={E_FAIL,E_FAIL,S_FALSE,S_OK};
    const WHV_PARTITION_HANDLE outputs[]={(WHV_PARTITION_HANDLE)(ULONG_PTR)123,NULL,(WHV_PARTITION_HANDLE)(ULONG_PTR)123,NULL};
    for(int i=0;i<4;i++) {
        fakeResult=codes[i];fakeOutput=outputs[i];
        if(AcquirePartition()==S_OK || partitionOwned || partition) return 71;
    }
    fakeResult=S_OK;fakeOutput=(WHV_PARTITION_HANDLE)(ULONG_PTR)456;
    if(AcquirePartition()!=S_OK || !partitionOwned || partition!=fakeOutput) return 72;
    fakeOutput=(WHV_PARTITION_HANDLE)(ULONG_PTR)789;
    if(AcquirePartition()!=E_UNEXPECTED || partition!=(WHV_PARTITION_HANDLE)(ULONG_PTR)456) return 73;
    partition=NULL;partitionOwned=false;api.create=NULL;
    puts("SIX_OWNERSHIP_MEMORY_CHECKS_NO_DLL_LOAD_OR_WHP_API");return 0;
}
static HANDLE ready, go;
static DWORD runTid;
static HRESULT runRc=E_PENDING;
static WHV_RUN_VP_EXIT_CONTEXT context;
static LARGE_INTEGER runStart, runEnd;
static FILETIME runWallStart,runWallEnd;
static DWORD WINAPI Run(void*) {
    runTid=GetCurrentThreadId();
    SetEvent(ready);
    if(WaitForSingleObject(go,2000)!=WAIT_OBJECT_0) return 91;
    QueryPerformanceCounter(&runStart);
    GetSystemTimePreciseAsFileTime(&runWallStart);
    runRc=api.run(partition,0,&context,sizeof(context));
    GetSystemTimePreciseAsFileTime(&runWallEnd);
    QueryPerformanceCounter(&runEnd);
    return 0;
}
static void Require(HRESULT hr,const char* stage) {
    if(hr!=S_OK) {fprintf(stderr,"%s HRESULT=0x%08lx\n",stage,(unsigned long)hr);throw 1;}
}
static WHV_PROCESSOR_RUNTIME_COUNTERS Counters() {
    WHV_PROCESSOR_RUNTIME_COUNTERS c={};UINT32 written=0;
    Require(api.counters(partition,0,WHvProcessorCounterSetRuntime,&c,sizeof(c),&written),"counters");
    if(written!=sizeof(c)) {fprintf(stderr,"counter byte size=%u\n",written);throw 1;}
    return c;
}
static unsigned long long Tick(FILETIME t) {return ((unsigned long long)t.dwHighDateTime<<32)|t.dwLowDateTime;}
int wmain(int argc,wchar_t** argv) {
    if(argc!=2) return 64;
    if(wcscmp(argv[1],L"--ownership-memory-check")==0) return OwnershipMemoryChecks();
    if(wcscmp(argv[1],L"--layout-check")==0) {
        if(sizeof(WHV_REGISTER_VALUE)!=16 || sizeof(WHV_PROCESSOR_RUNTIME_COUNTERS)!=16 ||
           WHvPartitionPropertyCodeProcessorCount!=0x1fff || WHvRunVpExitReasonCanceled!=0x2001) return 65;
        puts("WHP_ABI_ONLY_NO_API_LOAD_PARTITION_OR_THREAD");return 0;
    }
    if(wcscmp(argv[1],L"--probe-approved")!=0) return 64;
    // Caller must have atomically placed this exact binary in its private Job.
    // This entry has no generic image, guest code, address, PID or command input.
    BOOL inJob=FALSE;
    if(!IsProcessInJob(GetCurrentProcess(),NULL,&inJob)||!inJob) return 66;
    FILE* ownedOut=NULL;FILE* ownedErr=NULL;
    if(_wfreopen_s(&ownedOut,L"C:\\ProgramData\\ReBaseGuardP309-I2-RootDiagnostic-v3\\whp-probe.stdout.jsonl",L"wx",stdout)!=0) return 69;
    if(_wfreopen_s(&ownedErr,L"C:\\ProgramData\\ReBaseGuardP309-I2-RootDiagnostic-v3\\whp-probe.stderr.txt",L"wx",stderr)!=0) return 69;
    HANDLE thread=NULL;void* memory=NULL;bool vp=false,mapped=false;int result=1;
    HMODULE library=LoadLibraryExW(L"WinHvPlatform.dll",NULL,LOAD_LIBRARY_SEARCH_SYSTEM32);
    if(!library) return 67;
#define BIND(field,name) api.field=(decltype(api.field))GetProcAddress(library,#name);if(!api.field){fprintf(stderr,"missing " #name "\n");FreeLibrary(library);return 68;}
    BIND(create,WHvCreatePartition) BIND(property,WHvSetPartitionProperty)
    BIND(setup,WHvSetupPartition) BIND(map,WHvMapGpaRange) BIND(unmap,WHvUnmapGpaRange)
    BIND(createVp,WHvCreateVirtualProcessor) BIND(registers,WHvSetVirtualProcessorRegisters)
    BIND(counters,WHvGetVirtualProcessorCounters) BIND(run,WHvRunVirtualProcessor)
    BIND(cancel,WHvCancelRunVirtualProcessor) BIND(deleteVp,WHvDeleteVirtualProcessor) BIND(destroy,WHvDeletePartition)
#undef BIND
    FILETIME creation,exit,kernelBefore,userBefore,kernelAfter,userAfter;
    LARGE_INTEGER frequency,begin,end;
    QueryPerformanceFrequency(&frequency);QueryPerformanceCounter(&begin);
    try {
        if(!GetProcessTimes(GetCurrentProcess(),&creation,&exit,&kernelBefore,&userBefore)) throw 1;
        Require(AcquirePartition(),"create");
        UINT32 count=1;Require(api.property(partition,WHvPartitionPropertyCodeProcessorCount,&count,sizeof(count)),"one VP");
        Require(api.setup(partition),"setup");
        memory=VirtualAlloc(NULL,2*1024*1024,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
        if(!memory) throw 1;
        ((BYTE*)memory)[0x1000]=0xeb;((BYTE*)memory)[0x1001]=0xfe;
        Require(api.map(partition,memory,0,2*1024*1024,(WHV_MAP_GPA_RANGE_FLAGS)(WHvMapGpaRangeFlagRead|WHvMapGpaRangeFlagExecute)),"map fixed two-byte loop");mapped=true;
        Require(api.createVp(partition,0,0),"create VP");vp=true;
        WHV_REGISTER_NAME names[]={WHvX64RegisterCs,WHvX64RegisterRip,WHvX64RegisterRflags,WHvX64RegisterCr0};
        WHV_REGISTER_VALUE values[4]={};
        values[0].Segment.Base=0;values[0].Segment.Limit=0xffff;
        values[0].Segment.Selector=0;values[0].Segment.Attributes=0x9b;
        values[1].Reg64=0x1000;values[2].Reg64=2;values[3].Reg64=0x60000010;
        Require(api.registers(partition,0,names,4,values),"fixed real-mode registers");
        WHV_PROCESSOR_RUNTIME_COUNTERS before=Counters();
        ready=CreateEventW(NULL,TRUE,FALSE,NULL);go=CreateEventW(NULL,TRUE,FALSE,NULL);
        if(!ready||!go) throw 1;
        thread=CreateThread(NULL,0,Run,NULL,0,NULL);if(!thread) throw 1;
        if(WaitForSingleObject(ready,2000)!=WAIT_OBJECT_0) throw 1;
        SetEvent(go);
        Sleep(1000);
        HRESULT cancelRc=api.cancel(partition,0,0);
        // A delayed run thread may race cancellation. Do not assume a pending
        // cancel is retained: bounded join/outer Job stop handles UNKNOWN.
        if(WaitForSingleObject(thread,2000)!=WAIT_OBJECT_0) {
            fprintf(stderr,"run thread exit UNKNOWN; caller Job deadline retained\n");
            ExitProcess(92); // never free mapped/partition state under a running VP
        }
        Require(cancelRc,"cancel");Require(runRc,"run");
        if(context.ExitReason!=WHvRunVpExitReasonCanceled) throw 1;
        WHV_PROCESSOR_RUNTIME_COUNTERS after=Counters();
        if(after.TotalRuntime100ns<before.TotalRuntime100ns || after.HypervisorRuntime100ns<before.HypervisorRuntime100ns) throw 1;
        if(!GetProcessTimes(GetCurrentProcess(),&creation,&exit,&kernelAfter,&userAfter)) throw 1;
        QueryPerformanceCounter(&end);
        printf("{\"scope\":\"ONE_OWNED_WHP_COUNTER_COMPARISON_NOT_QEMU_OR_FULL_COVERAGE\",\"pid\":%lu,\"run_tid\":%lu,\"creation_filetime\":%llu,\"qpc_frequency\":%lld,\"begin_qpc\":%lld,\"end_qpc\":%lld,\"run_begin_qpc\":%lld,\"run_end_qpc\":%lld,\"vp_total_before_100ns\":%llu,\"vp_total_after_100ns\":%llu,\"vp_hypervisor_before_100ns\":%llu,\"vp_hypervisor_after_100ns\":%llu,\"process_cpu_before_100ns\":%llu,\"process_cpu_after_100ns\":%llu,\"cancel_hr\":%ld,\"run_hr\":%ld,\"exit_reason\":%u,\"admission\":\"BLOCKED\"}\n",
            GetCurrentProcessId(),runTid,Tick(creation),frequency.QuadPart,begin.QuadPart,end.QuadPart,runStart.QuadPart,runEnd.QuadPart,
            before.TotalRuntime100ns,after.TotalRuntime100ns,before.HypervisorRuntime100ns,after.HypervisorRuntime100ns,
            Tick(kernelBefore)+Tick(userBefore),Tick(kernelAfter)+Tick(userAfter),(long)cancelRc,(long)runRc,(unsigned)context.ExitReason);
        fflush(stdout);result=0;
        printf("{\"stage\":\"run_wall_anchors\",\"begin_filetime\":%llu,\"end_filetime\":%llu,\"scope\":\"SEQUENTIAL_CLOCK_READS_NOT_ATOMIC_EQUALITY\"}\n",Tick(runWallStart),Tick(runWallEnd));
    } catch(...) {fprintf(stderr,"WHP probe FAILED; no second partition or retry\n");}
    // Exception before normal join: cancel and confirm exit before destroying state.
    if(thread && WaitForSingleObject(thread,0)!=WAIT_OBJECT_0) {
        api.cancel(partition,0,0);SetEvent(go);
        if(WaitForSingleObject(thread,2000)!=WAIT_OBJECT_0) ExitProcess(93);
    }
    if(vp && api.deleteVp(partition,0)!=S_OK) result=1;
    if(mapped && api.unmap(partition,0,2*1024*1024)!=S_OK) result=1;
    if(partitionOwned && api.destroy(partition)!=S_OK) result=1;
    if(memory && !VirtualFree(memory,0,MEM_RELEASE)) result=1;
    if(thread)CloseHandle(thread);if(go)CloseHandle(go);if(ready)CloseHandle(ready);
    FreeLibrary(library);
    printf("{\"stage\":\"whp_cleanup\",\"api_cleanup_succeeded\":%s,\"admission\":\"BLOCKED\"}\n",result==0?"true":"false");
    if(fflush(stdout)!=0 || _commit(_fileno(stdout))!=0) result=1;
    if(fflush(stderr)!=0 || _commit(_fileno(stderr))!=0) result=1;
    // Parent additionally requires retained process exit and its exact Job empty.
    return result;
}
