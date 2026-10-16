/* Prepared only. Native UAC entry: no CLR, no shell command parsing, no trace.
 * The caller MUST pin this file and its ancestors before requesting elevation.
 * No self-hash can replace the caller's pre-execution binding. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>

static const wchar_t templatePath[]=L"C:\\Users\\Lenovo\\P309-I2-root-build-20261016-v1\\Trusted-Entry.template.ps1";
static const char templateHash[]="86e660955938cc4015aa31c147ed43a6eb55faf7c0ac3e4c85eedaad0198d923";
static const char marker[]="__APPROVAL_RECORD_SHA256_AFTER_ACTUAL_HUMAN_APPROVAL__";
static const wchar_t winps[]=L"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe";
static const wchar_t environment[]=L"PATH=C:\\Windows\\System32\0PSModulePath=C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules\0SystemRoot=C:\\Windows\0TEMP=C:\\Windows\\Temp\0TMP=C:\\Windows\\Temp\0WINDIR=C:\\Windows\0\0";
static void zero(void* pointer,SIZE_T size) {volatile BYTE* p=(volatile BYTE*)pointer;while(size--)*p++=0;}
static SIZE_T length(const char* p) {SIZE_T n=0;while(p[n])n++;return n;}
static void copy(void* dst,const void* src,SIZE_T n) {BYTE* d=(BYTE*)dst;const BYTE* s=(const BYTE*)src;while(n--)*d++=*s++;}
static int equal(const char* a,const char* b,SIZE_T n) {while(n--)if(*a++!=*b++)return 0;return 1;}
static void* alloc(SIZE_T n) {void* p=HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,n);if(!p)ExitProcess(80);return p;}
static int admin(void) {
    HMODULE lib=LoadLibraryExW(L"advapi32.dll",NULL,LOAD_LIBRARY_SEARCH_SYSTEM32);
    HANDLE token=NULL;TOKEN_ELEVATION e;DWORD returned=0;BOOL ok=FALSE;
    typedef BOOL (WINAPI *OpenT)(HANDLE,DWORD,PHANDLE);
    typedef BOOL (WINAPI *GetT)(HANDLE,TOKEN_INFORMATION_CLASS,LPVOID,DWORD,PDWORD);
    OpenT open;GetT get;if(!lib)return 0;
    open=(OpenT)GetProcAddress(lib,"OpenProcessToken");get=(GetT)GetProcAddress(lib,"GetTokenInformation");
    if(open&&get&&open(GetCurrentProcess(),TOKEN_QUERY,&token))ok=get(token,TokenElevation,&e,sizeof(e),&returned)&&e.TokenIsElevated;
    if(token)CloseHandle(token);FreeLibrary(lib);return ok;
}
static int hash(const BYTE* bytes,DWORD size,char result[65]) {
    HMODULE lib=LoadLibraryExW(L"bcrypt.dll",NULL,LOAD_LIBRARY_SEARCH_SYSTEM32);
    BCRYPT_ALG_HANDLE algorithm=NULL;BCRYPT_HASH_HANDLE state=NULL;BYTE digest[32];int ok=0,i;
    typedef NTSTATUS (WINAPI *OpenA)(BCRYPT_ALG_HANDLE*,LPCWSTR,LPCWSTR,ULONG);
    typedef NTSTATUS (WINAPI *CreateH)(BCRYPT_ALG_HANDLE,BCRYPT_HASH_HANDLE*,PUCHAR,ULONG,PUCHAR,ULONG,ULONG);
    typedef NTSTATUS (WINAPI *HashD)(BCRYPT_HASH_HANDLE,PUCHAR,ULONG,ULONG);
    typedef NTSTATUS (WINAPI *FinishH)(BCRYPT_HASH_HANDLE,PUCHAR,ULONG,ULONG);
    typedef NTSTATUS (WINAPI *DestroyH)(BCRYPT_HASH_HANDLE);
    typedef NTSTATUS (WINAPI *CloseA)(BCRYPT_ALG_HANDLE,ULONG);
    OpenA open;CreateH create;HashD update;FinishH finish;DestroyH destroy;CloseA close;
    if(!lib)return 0;
    open=(OpenA)GetProcAddress(lib,"BCryptOpenAlgorithmProvider");create=(CreateH)GetProcAddress(lib,"BCryptCreateHash");
    update=(HashD)GetProcAddress(lib,"BCryptHashData");finish=(FinishH)GetProcAddress(lib,"BCryptFinishHash");
    destroy=(DestroyH)GetProcAddress(lib,"BCryptDestroyHash");close=(CloseA)GetProcAddress(lib,"BCryptCloseAlgorithmProvider");
    if(!open||!create||!update||!finish||!destroy||!close)goto done;
    if(open(&algorithm,L"SHA256",NULL,0)<0 || create(algorithm,&state,NULL,0,NULL,0,0)<0
       || update(state,(PUCHAR)bytes,size,0)<0 || finish(state,digest,32,0)<0)goto done;
    for(i=0;i<32;i++){result[i*2]="0123456789abcdef"[digest[i]>>4];result[i*2+1]="0123456789abcdef"[digest[i]&15];}
    result[64]=0;ok=1;
done:
    if(state)destroy(state);if(algorithm)close(algorithm,0);FreeLibrary(lib);return ok;
}
static wchar_t* base64(const BYTE* bytes,DWORD n) {
    const wchar_t alphabet[]=L"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    wchar_t* out=(wchar_t*)alloc(((n+2)/3*4+1)*sizeof(wchar_t));DWORD i=0,j=0;
    while(i<n){DWORD remain=n-i,a=bytes[i++],b=remain>1?bytes[i++]:0,c=remain>2?bytes[i++]:0;
        out[j++]=alphabet[a>>2];out[j++]=alphabet[((a&3)<<4)|(b>>4)];
        out[j++]=remain>1?alphabet[((b&15)<<2)|(c>>6)]:L'=';out[j++]=remain>2?alphabet[c&63]:L'=';}
    return out;
}
void WINAPI Entry(void) {
    wchar_t* cmd=GetCommandLineW();wchar_t* approval;DWORD size,got,rc=1;HANDLE file;
    BYTE* bytes;char actual[65],digest[65];SIZE_T i,at=(SIZE_T)-1,mlen=length(marker),newSize;
    char* rendered;wchar_t* wide;wchar_t* encoded;wchar_t* launch;int wn;STARTUPINFOW si;PROCESS_INFORMATION pi;
    if(!SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_SYSTEM32))ExitProcess(70);
    if(*cmd==L'"'){cmd++;while(*cmd&&*cmd!=L'"')cmd++;if(*cmd)cmd++;}
    else while(*cmd&&*cmd!=L' ')cmd++;
    while(*cmd==L' ')cmd++;approval=cmd;if(lstrlenW(approval)!=64)ExitProcess(64);
    for(i=0;i<64;i++){wchar_t c=approval[i];if(!((c>=L'0'&&c<=L'9')||(c>=L'a'&&c<=L'f')))ExitProcess(64);digest[i]=(char)c;}
    if(approval[64]!=0)ExitProcess(64);digest[64]=0;
    if(!admin())ExitProcess(71);
    file=CreateFileW(templatePath,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE)ExitProcess(72);
    size=GetFileSize(file,NULL);if(size==INVALID_FILE_SIZE||size>16384){CloseHandle(file);ExitProcess(73);}
    bytes=(BYTE*)alloc(size+1);
    if(!ReadFile(file,bytes,size,&got,NULL)||got!=size){CloseHandle(file);ExitProcess(74);}CloseHandle(file);
    if(!hash(bytes,size,actual)||length(templateHash)!=64||!equal(actual,templateHash,64))ExitProcess(75);
    for(i=0;i+mlen<=size;i++)if(equal((char*)bytes+i,marker,mlen)){if(at!=(SIZE_T)-1)ExitProcess(76);at=i;}
    if(at==(SIZE_T)-1)ExitProcess(76);
    newSize=size-mlen+64;rendered=(char*)alloc(newSize+1);copy(rendered,bytes,at);copy(rendered+at,digest,64);copy(rendered+at+64,bytes+at+mlen,size-at-mlen);
    wn=MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,rendered,(int)newSize,NULL,0);if(wn<=0)ExitProcess(77);
    wide=(wchar_t*)alloc((wn+1)*sizeof(wchar_t));if(MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,rendered,(int)newSize,wide,wn)!=wn)ExitProcess(77);
    encoded=base64((BYTE*)wide,wn*sizeof(wchar_t));
    if(lstrlenW(encoded)>24000)ExitProcess(78);
    launch=(wchar_t*)alloc(32768*sizeof(wchar_t));lstrcpyW(launch,L"\"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe\" -NoProfile -NonInteractive -EncodedCommand ");lstrcatW(launch,encoded);
    zero(&si,sizeof(si));zero(&pi,sizeof(pi));si.cb=sizeof(si);
    // Explicit environment BEFORE CLR/PowerShell initialization; no inherited
    // COMPLUS/COR/DOTNET profiler or PS module variables, no mutable shell.
    if(!CreateProcessW(winps,launch,NULL,NULL,FALSE,CREATE_UNICODE_ENVIRONMENT|CREATE_NO_WINDOW,(LPVOID)environment,L"C:\\Windows\\System32",&si,&pi))ExitProcess(79);
    CloseHandle(pi.hThread);
    if(WaitForSingleObject(pi.hProcess,240000)==WAIT_OBJECT_0)GetExitCodeProcess(pi.hProcess,&rc);
    else rc=81; // Do not kill an elevated controller with in-flight native work.
    CloseHandle(pi.hProcess);ExitProcess(rc);
}
