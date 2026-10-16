/* Pure-memory ownership fault injection. Never invoke source Entry().
 * All token/CNG calls below are synthetic function-pointer exports. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>

static unsigned assertions, cases;
static const char *case_name;
static void check(int value, const char *expression, int line) {
    ++assertions;
    if (!value) {
        fprintf(stderr,"FAIL %s line %d: %s\n",case_name,line,expression);
        exit(1);
    }
}
#define CHECK(expression) check(!!(expression),#expression,__LINE__)
#define LIB_HANDLE ((HMODULE)(ULONG_PTR)0x1000)
#define TOKEN_HANDLE ((HANDLE)(ULONG_PTR)0x2000)
#define ALG_HANDLE ((BCRYPT_ALG_HANDLE)(ULONG_PTR)0x3000)
#define HASH_HANDLE ((BCRYPT_HASH_HANDLE)(ULONG_PTR)0x4000)
#define POISON_TOKEN ((HANDLE)(ULONG_PTR)0xDEAD0001)
#define POISON_ALG ((BCRYPT_ALG_HANDLE)(ULONG_PTR)0xDEAD0002)
#define POISON_HASH ((BCRYPT_HASH_HANDLE)(ULONG_PTR)0xDEAD0003)
#define CURRENT_PROCESS ((HANDLE)(LONG_PTR)-1)
#define FAILURE_STATUS ((NTSTATUS)0xC0000001L)

enum Mode { ADMIN_MODE, HASH_MODE };
enum Mode mode;
static int fail_library, fail_token_open, fail_token_query;
static int elevated, fail_algorithm_open, fail_hash_create, fail_update, fail_finish;
static const char *missing_export;
static unsigned loads, exports, frees, token_opens, token_queries, token_closes;
static unsigned alg_opens, hash_creates, updates, finishes, hash_destroys, alg_closes;

static void reset(const char *name, enum Mode next_mode) {
    case_name=name; mode=next_mode; ++cases;
    fail_library=fail_token_open=fail_token_query=0;
    elevated=1; fail_algorithm_open=fail_hash_create=fail_update=fail_finish=0;
    missing_export=NULL;
    loads=exports=frees=token_opens=token_queries=token_closes=0;
    alg_opens=hash_creates=updates=finishes=hash_destroys=alg_closes=0;
}
static HMODULE WINAPI mock_load(LPCWSTR file,HANDLE reserved,DWORD flags) {
    ++loads; CHECK(reserved==NULL); CHECK(flags==LOAD_LIBRARY_SEARCH_SYSTEM32);
    CHECK(wcscmp(file,mode==ADMIN_MODE?L"advapi32.dll":L"bcrypt.dll")==0);
    return fail_library?NULL:LIB_HANDLE;
}
static BOOL WINAPI mock_free(HMODULE library) {
    CHECK(library==LIB_HANDLE); CHECK(++frees==1); return TRUE;
}
static HANDLE WINAPI mock_current(void) { return CURRENT_PROCESS; }
static BOOL WINAPI mock_token_open(HANDLE process,DWORD access,PHANDLE output) {
    ++token_opens; CHECK(process==CURRENT_PROCESS); CHECK(access==TOKEN_QUERY);
    CHECK(output!=NULL); CHECK(*output==NULL);
    *output=fail_token_open?POISON_TOKEN:TOKEN_HANDLE;
    return !fail_token_open;
}
static BOOL WINAPI mock_token_query(HANDLE token,TOKEN_INFORMATION_CLASS cls,
                                   LPVOID output,DWORD size,PDWORD returned) {
    ++token_queries; CHECK(token==TOKEN_HANDLE); CHECK(cls==TokenElevation);
    CHECK(size==sizeof(TOKEN_ELEVATION)); CHECK(output!=NULL && returned!=NULL);
    ((TOKEN_ELEVATION*)output)->TokenIsElevated=(DWORD)elevated;
    *returned=sizeof(TOKEN_ELEVATION);
    return !fail_token_query;
}
static BOOL WINAPI mock_close_handle(HANDLE handle) {
    /* A failed call's non-NULL poison output is never an owned handle. */
    CHECK(handle==TOKEN_HANDLE); CHECK(++token_closes==1); return TRUE;
}
static NTSTATUS WINAPI mock_algorithm_open(BCRYPT_ALG_HANDLE *output,LPCWSTR id,
                                           LPCWSTR provider,ULONG flags) {
    ++alg_opens; CHECK(output!=NULL); CHECK(*output==NULL);
    CHECK(wcscmp(id,L"SHA256")==0); CHECK(provider==NULL); CHECK(flags==0);
    *output=fail_algorithm_open?POISON_ALG:ALG_HANDLE;
    return fail_algorithm_open?FAILURE_STATUS:0;
}
static NTSTATUS WINAPI mock_hash_create(BCRYPT_ALG_HANDLE algorithm,
                                        BCRYPT_HASH_HANDLE *output,PUCHAR object,
                                        ULONG object_size,PUCHAR secret,
                                        ULONG secret_size,ULONG flags) {
    ++hash_creates; CHECK(algorithm==ALG_HANDLE); CHECK(output!=NULL); CHECK(*output==NULL);
    CHECK(object==NULL && object_size==0 && secret==NULL && secret_size==0 && flags==0);
    *output=fail_hash_create?POISON_HASH:HASH_HANDLE;
    return fail_hash_create?FAILURE_STATUS:0;
}
static NTSTATUS WINAPI mock_update(BCRYPT_HASH_HANDLE hash,PUCHAR bytes,ULONG size,ULONG flags) {
    ++updates; CHECK(hash==HASH_HANDLE); CHECK(size==3); CHECK(flags==0);
    CHECK(bytes!=NULL && bytes[0]==0 && bytes[1]==0x80 && bytes[2]==0xff);
    return fail_update?FAILURE_STATUS:0;
}
static NTSTATUS WINAPI mock_finish(BCRYPT_HASH_HANDLE hash,PUCHAR digest,ULONG size,ULONG flags) {
    unsigned i; ++finishes; CHECK(hash==HASH_HANDLE); CHECK(size==32); CHECK(flags==0);
    CHECK(digest!=NULL); for(i=0;i<32;++i)digest[i]=(BYTE)i;
    return fail_finish?FAILURE_STATUS:0;
}
static NTSTATUS WINAPI mock_destroy(BCRYPT_HASH_HANDLE hash) {
    CHECK(hash==HASH_HANDLE); CHECK(++hash_destroys==1); return 0;
}
static NTSTATUS WINAPI mock_algorithm_close(BCRYPT_ALG_HANDLE algorithm,ULONG flags) {
    CHECK(algorithm==ALG_HANDLE); CHECK(flags==0); CHECK(++alg_closes==1); return 0;
}
static FARPROC WINAPI mock_export(HMODULE library,LPCSTR name) {
    ++exports; CHECK(library==LIB_HANDLE);
    if(missing_export && strcmp(missing_export,name)==0)return NULL;
    if(mode==ADMIN_MODE) {
        if(strcmp(name,"OpenProcessToken")==0)return (FARPROC)mock_token_open;
        if(strcmp(name,"GetTokenInformation")==0)return (FARPROC)mock_token_query;
    } else {
        if(strcmp(name,"BCryptOpenAlgorithmProvider")==0)return (FARPROC)mock_algorithm_open;
        if(strcmp(name,"BCryptCreateHash")==0)return (FARPROC)mock_hash_create;
        if(strcmp(name,"BCryptHashData")==0)return (FARPROC)mock_update;
        if(strcmp(name,"BCryptFinishHash")==0)return (FARPROC)mock_finish;
        if(strcmp(name,"BCryptDestroyHash")==0)return (FARPROC)mock_destroy;
        if(strcmp(name,"BCryptCloseAlgorithmProvider")==0)return (FARPROC)mock_algorithm_close;
    }
    CHECK(0); return NULL;
}

/* Header declarations were consumed before substitution. These macros ensure
 * admin/hash cannot perform a real loader, token query, CNG call, or handle close.
 * Unused source entry is renamed and is never selected by this console binary. */
#define LoadLibraryExW mock_load
#define GetProcAddress mock_export
#define FreeLibrary mock_free
#define CloseHandle mock_close_handle
#define GetCurrentProcess mock_current
#define Entry SourceEntry_NeverInvoked
#include "../package/NativeEntry.c"
#undef Entry
#undef LoadLibraryExW
#undef GetProcAddress
#undef FreeLibrary
#undef CloseHandle
#undef GetCurrentProcess

static void admin_counts(unsigned expected_open,unsigned expected_query,unsigned expected_close,
                         unsigned expected_exports,unsigned expected_free) {
    CHECK(loads==1); CHECK(exports==expected_exports); CHECK(frees==expected_free);
    CHECK(token_opens==expected_open); CHECK(token_queries==expected_query); CHECK(token_closes==expected_close);
    CHECK(alg_opens==0 && hash_creates==0 && updates==0 && finishes==0 && hash_destroys==0 && alg_closes==0);
}
static void test_admin(void) {
    reset("admin library failure",ADMIN_MODE); fail_library=1;
    CHECK(admin()==0); admin_counts(0,0,0,0,0);
    reset("admin missing open export",ADMIN_MODE); missing_export="OpenProcessToken";
    CHECK(admin()==0); admin_counts(0,0,0,2,1);
    reset("admin missing query export",ADMIN_MODE); missing_export="GetTokenInformation";
    CHECK(admin()==0); admin_counts(0,0,0,2,1);
    reset("admin failed open writes poison token",ADMIN_MODE); fail_token_open=1;
    CHECK(admin()==0); admin_counts(1,0,0,2,1);
    reset("admin query fails with populated output",ADMIN_MODE); fail_token_query=1;
    CHECK(admin()==0); admin_counts(1,1,1,2,1);
    reset("admin not elevated",ADMIN_MODE); elevated=0;
    CHECK(admin()==0); admin_counts(1,1,1,2,1);
    reset("admin success",ADMIN_MODE);
    CHECK(admin()!=0); admin_counts(1,1,1,2,1);
}
static const BYTE input_bytes[3]={0,0x80,0xff};
static void hash_counts(unsigned open_count,unsigned create_count,unsigned update_count,
                        unsigned finish_count,unsigned destroy_count,unsigned close_count,
                        unsigned export_count,unsigned free_count) {
    CHECK(loads==1); CHECK(exports==export_count); CHECK(frees==free_count);
    CHECK(alg_opens==open_count); CHECK(hash_creates==create_count);
    CHECK(updates==update_count); CHECK(finishes==finish_count);
    CHECK(hash_destroys==destroy_count); CHECK(alg_closes==close_count);
    CHECK(token_opens==0 && token_queries==0 && token_closes==0);
}
static void hash_fail(char result[65]) {
    unsigned i; memset(result,0x7e,65);
    CHECK(hash(input_bytes,sizeof(input_bytes),result)==0);
    for(i=0;i<65;++i)CHECK(result[i]==0x7e);
}
static void test_hash(void) {
    char result[65]; unsigned i;
    const char *names[]={"BCryptOpenAlgorithmProvider","BCryptCreateHash","BCryptHashData",
                         "BCryptFinishHash","BCryptDestroyHash","BCryptCloseAlgorithmProvider"};
    reset("hash library failure",HASH_MODE); fail_library=1;
    hash_fail(result); hash_counts(0,0,0,0,0,0,0,0);
    for(i=0;i<6;++i) {
        reset(names[i],HASH_MODE); missing_export=names[i];
        hash_fail(result); hash_counts(0,0,0,0,0,0,6,1);
    }
    reset("hash failed algorithm open writes poison",HASH_MODE); fail_algorithm_open=1;
    hash_fail(result); hash_counts(1,0,0,0,0,0,6,1);
    reset("hash failed create writes poison",HASH_MODE); fail_hash_create=1;
    hash_fail(result); hash_counts(1,1,0,0,0,1,6,1);
    reset("hash update failure",HASH_MODE); fail_update=1;
    hash_fail(result); hash_counts(1,1,1,0,1,1,6,1);
    reset("hash finish failure",HASH_MODE); fail_finish=1;
    hash_fail(result); hash_counts(1,1,1,1,1,1,6,1);
    reset("hash success formatting and exactly once cleanup",HASH_MODE);
    memset(result,0x7e,65); CHECK(hash(input_bytes,sizeof(input_bytes),result)!=0);
    CHECK(strcmp(result,"000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")==0);
    hash_counts(1,1,1,1,1,1,6,1);
}
int main(void) {
    test_admin(); test_hash();
    printf("{\"cases\":%u,\"assertions\":%u,\"passed\":true,\"scope\":\"PURE_MEMORY_SYNTHETIC_OWNERSHIP_ONLY\",\"entry_invocations\":0,\"real_token_cng_queries\":0,\"uac\":0,\"admission\":\"BLOCKED\"}\n",cases,assertions);
    return 0;
}
