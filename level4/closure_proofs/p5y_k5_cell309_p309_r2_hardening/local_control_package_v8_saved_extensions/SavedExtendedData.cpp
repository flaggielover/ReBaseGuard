#define UNICODE
#define _UNICODE
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <evntrace.h>
#include <evntcons.h>
#include <bcrypt.h>
#include <stdint.h>
#include <stdio.h>
#include <stddef.h>
#include <string.h>
#include <algorithm>
#include <array>
#include <limits>
#include <locale>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// Offline consumer only. No controller, provider enablement, TDH payload decoding,
// live logger, PID lookup, service, VM, WSL, registry, or process-start operation.
namespace p309v8 {
static const wchar_t kInput[] = L"D:\\ReBaseGuard-309\\records\\p309-i2-root-v3-attempt-20261016-01\\capture\\capture.etl";
static const char kInputSha[] = "3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870";
static const uint64_t kInputSize = 308346880ULL;
static const GUID kLost = {0x6a399ae0,0x4bc6,0x4de9,{0x87,0x0b,0x36,0x57,0xf8,0x94,0x7e,0x7e}};
static_assert(sizeof(EVENT_HEADER_EXTENDED_DATA_ITEM) == 16, "SDK extended item ABI");
static_assert(sizeof(EVENT_EXTENDED_ITEM_PROCESS_START_KEY) == 8, "SDK PSK scalar ABI");
static_assert(EVENT_HEADER_EXT_TYPE_PROCESS_START_KEY == 13, "SDK PSK type");
static_assert(sizeof(void*) == 8, "This saved-file consumer is x64 only");

struct Error { const char* stage; DWORD code; };
static void Fail(const char* stage, DWORD code) { throw Error{stage, code}; }
static const char* B(bool value) { return value ? "true" : "false"; }
static std::string Guid(const GUID& g) {
 char b[40]; const int n = snprintf(b,sizeof(b),"%08lx-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x",
  g.Data1,g.Data2,g.Data3,g.Data4[0],g.Data4[1],g.Data4[2],g.Data4[3],g.Data4[4],g.Data4[5],g.Data4[6],g.Data4[7]);
 if(n != 36) Fail("GUID_FORMAT",ERROR_INVALID_DATA); return std::string(b,36);
}
static std::string Hex(const BYTE* p,size_t size) {
 static const char digits[]="0123456789abcdef"; std::string out; out.reserve(size*2);
 for(size_t i=0;i<size;++i){out.push_back(digits[p[i]>>4]);out.push_back(digits[p[i]&15]);}return out;
}
struct Handle {
 HANDLE h=INVALID_HANDLE_VALUE;
 Handle()=default; explicit Handle(HANDLE value):h(value){}
 Handle(const Handle&)=delete; Handle& operator=(const Handle&)=delete;
 Handle(Handle&& x) noexcept :h(x.h){x.h=INVALID_HANDLE_VALUE;}
 Handle& operator=(Handle&& x) noexcept {if(this!=&x){if(h!=INVALID_HANDLE_VALUE)CloseHandle(h);h=x.h;x.h=INVALID_HANDLE_VALUE;}return *this;}
 ~Handle(){if(h!=INVALID_HANDLE_VALUE)CloseHandle(h);}
 DWORD Close(){if(h==INVALID_HANDLE_VALUE)return ERROR_SUCCESS;HANDLE old=h;h=INVALID_HANDLE_VALUE;return CloseHandle(old)?ERROR_SUCCESS:GetLastError();}
};
static Handle OpenFile(const wchar_t* name,DWORD access,DWORD share,DWORD disposition,DWORD flags,const char* stage){
 HANDLE h=CreateFileW(name,access,share,nullptr,disposition,flags,nullptr);if(h==INVALID_HANDLE_VALUE)Fail(stage,GetLastError());return Handle(h);
}
static BY_HANDLE_FILE_INFORMATION Facts(HANDLE h,bool directory){
 BY_HANDLE_FILE_INFORMATION i{};if(!GetFileInformationByHandle(h,&i))Fail("INPUT_FILE_INFO",GetLastError());
 if((i.dwFileAttributes&FILE_ATTRIBUTE_REPARSE_POINT)||(((i.dwFileAttributes&FILE_ATTRIBUTE_DIRECTORY)!=0)!=directory))Fail("INPUT_REPARSE_OR_TYPE",ERROR_INVALID_DATA);
 if(!directory&&i.nNumberOfLinks!=1)Fail("INPUT_HARD_LINK",ERROR_INVALID_DATA);return i;
}
static bool SameFile(const BY_HANDLE_FILE_INFORMATION& a,const BY_HANDLE_FILE_INFORMATION& b){
 return a.dwVolumeSerialNumber==b.dwVolumeSerialNumber&&a.nFileIndexHigh==b.nFileIndexHigh&&a.nFileIndexLow==b.nFileIndexLow&&a.nFileSizeHigh==b.nFileSizeHigh&&a.nFileSizeLow==b.nFileSizeLow;
}
class Sha256 {
 BCRYPT_ALG_HANDLE algorithm=nullptr; BCRYPT_HASH_HANDLE hash=nullptr; std::vector<BYTE> object;
 void Check(NTSTATUS result){if(result<0)Fail("SHA256_API",static_cast<DWORD>(result));}
public:
 Sha256(){try{Check(BCryptOpenAlgorithmProvider(&algorithm,BCRYPT_SHA256_ALGORITHM,nullptr,0));DWORD n=0,got=0;Check(BCryptGetProperty(algorithm,BCRYPT_OBJECT_LENGTH,reinterpret_cast<BYTE*>(&n),sizeof(n),&got,0));if(got!=sizeof(n)||n==0||n>1048576)Fail("SHA256_OBJECT_BOUND",ERROR_INVALID_DATA);object.resize(n);Check(BCryptCreateHash(algorithm,&hash,object.data(),n,nullptr,0,0));}catch(...){if(hash)BCryptDestroyHash(hash);if(algorithm)BCryptCloseAlgorithmProvider(algorithm,0);throw;}}
 ~Sha256(){if(hash)BCryptDestroyHash(hash);if(algorithm)BCryptCloseAlgorithmProvider(algorithm,0);}
 Sha256(const Sha256&)=delete;Sha256& operator=(const Sha256&)=delete;
 void Add(const BYTE* p,ULONG n){Check(BCryptHashData(hash,const_cast<BYTE*>(p),n,0));}
 std::string Finish(){BYTE result[32]{};Check(BCryptFinishHash(hash,result,sizeof(result),0));return Hex(result,sizeof(result));}
};
static std::string HashBytes(const std::string& s){Sha256 hash;size_t at=0;while(at<s.size()){ULONG n=static_cast<ULONG>((std::min)(s.size()-at,static_cast<size_t>(1048576)));hash.Add(reinterpret_cast<const BYTE*>(s.data()+at),n);at+=n;}return hash.Finish();}
static std::string HashFile(HANDLE file){
 LARGE_INTEGER zero{};if(!SetFilePointerEx(file,zero,nullptr,FILE_BEGIN))Fail("INPUT_SEEK",GetLastError());Sha256 hash;std::vector<BYTE> data(1048576);uint64_t bytes=0;
 for(;;){DWORD n=0;if(!ReadFile(file,data.data(),static_cast<DWORD>(data.size()),&n,nullptr))Fail("INPUT_READ",GetLastError());if(n==0)break;bytes+=n;if(bytes>kInputSize)Fail("INPUT_HASH_SIZE",ERROR_INVALID_DATA);hash.Add(data.data(),n);}
 if(bytes!=kInputSize)Fail("INPUT_HASH_SIZE",ERROR_INVALID_DATA);return hash.Finish();
}
struct PinnedInput {
 std::vector<Handle> ancestors;Handle leaf;BY_HANDLE_FILE_INFORMATION original{};
 void Open(){
  std::wstring path(kInput);std::wstring current=path.substr(0,3);
  ancestors.push_back(OpenFile(current.c_str(),GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,OPEN_EXISTING,FILE_FLAG_BACKUP_SEMANTICS|FILE_FLAG_OPEN_REPARSE_POINT,"INPUT_ANCESTOR_OPEN"));Facts(ancestors.back().h,true);
  size_t start=3;for(size_t slash=path.find(L'\\',start);slash!=std::wstring::npos;slash=path.find(L'\\',start)){current=path.substr(0,slash);ancestors.push_back(OpenFile(current.c_str(),GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,OPEN_EXISTING,FILE_FLAG_BACKUP_SEMANTICS|FILE_FLAG_OPEN_REPARSE_POINT,"INPUT_ANCESTOR_OPEN"));Facts(ancestors.back().h,true);start=slash+1;}
  leaf=OpenFile(kInput,GENERIC_READ,FILE_SHARE_READ,OPEN_EXISTING,FILE_FLAG_OPEN_REPARSE_POINT|FILE_FLAG_SEQUENTIAL_SCAN,"INPUT_LEAF_OPEN");original=Facts(leaf.h,false);
  const uint64_t size=(static_cast<uint64_t>(original.nFileSizeHigh)<<32)|original.nFileSizeLow;if(size!=kInputSize)Fail("INPUT_FIXED_SIZE",ERROR_INVALID_DATA);
 }
 void CheckIdentity(){if(!SameFile(original,Facts(leaf.h,false)))Fail("INPUT_HELD_IDENTITY_DRIFT",ERROR_INVALID_DATA);}
 void Close(uint64_t& attempted,uint64_t& errors,DWORD& first_error){
  auto close=[&](Handle& h){if(h.h==INVALID_HANDLE_VALUE)return;++attempted;DWORD rc=h.Close();if(rc){++errors;if(first_error==0)first_error=rc;}};
  close(leaf);for(auto at=ancestors.rbegin();at!=ancestors.rend();++at)close(*at);
 }
};

struct EventKey {
 GUID provider{};USHORT id=0;BYTE version=0,opcode=0;
 bool operator<(const EventKey& other)const{const int g=memcmp(&provider,&other.provider,sizeof(GUID));if(g!=0)return g<0;if(id!=other.id)return id<other.id;if(version!=other.version)return version<other.version;return opcode<other.opcode;}
};
struct ExtStats {uint64_t items=0,events=0,duplicate_items=0,null_data=0,zero_size=0,reserved_nonzero=0,psk_wrong_size=0,psk_unreadable=0,malformed_items=0,last_ordinal=0;};
struct EventStats {
 uint64_t events=0,declared_items=0,inspected_items=0,no_extended_items=0,null_array=0,array_with_zero_count=0,unreadable_array=0,header_flag_mismatch=0,duplicate_type_events=0,duplicate_items=0,malformed_events=0;
 uint64_t psk_absent=0,psk_candidate=0,psk_unknown_duplicate=0,psk_unknown_malformed=0,psk_unknown_uninspectable=0;
 std::map<std::pair<USHORT,USHORT>,ExtStats> extended;
};
// The only descriptor payload read is an 8-byte PSK readability probe. Its value
// is neither stored in an aggregate nor compared, hashed, or serialized.
static bool CopyItem(const EVENT_HEADER_EXTENDED_DATA_ITEM* array,USHORT index,EVENT_HEADER_EXTENDED_DATA_ITEM* out){
 if(!array)return false;const uintptr_t at=reinterpret_cast<uintptr_t>(array);const size_t offset=static_cast<size_t>(index)*sizeof(*array);
 if(at>(std::numeric_limits<uintptr_t>::max)()-offset-sizeof(*array))return false;
 __try{memcpy(out,reinterpret_cast<const void*>(at+offset),sizeof(*out));return true;}__except(EXCEPTION_EXECUTE_HANDLER){return false;}
}
static bool ReadablePsk(ULONGLONG pointer){
 if(pointer==0||pointer>(std::numeric_limits<uintptr_t>::max)()-7)return false;
 __try{volatile ULONG64 value=*reinterpret_cast<const volatile ULONG64*>(static_cast<uintptr_t>(pointer));value=0;return true;}__except(EXCEPTION_EXECUTE_HANDLER){return false;}
}
struct Context {
 std::map<EventKey,EventStats> groups;std::vector<uint64_t> seen=std::vector<uint64_t>(65536,0);
 size_t max_groups=16384,max_extended_rows=65536,extended_rows=0;
 uint64_t callbacks=0,fully_inspected_events=0,callbacks_after_failure=0,null_callbacks=0,event_context_mismatches=0,buffer_context_mismatches=0;
 uint64_t lost_event_notifications=0,lost_buffer_notifications=0,lost_file_notifications=0;
 uint64_t buffer_callbacks=0,buffer_read_max=0,buffer_read_last=0,buffer_size_max=0,buffer_filled_max=0;
 ULONG callback_header_events_lost_max=0,callback_header_buffers_lost_max=0,callback_events_lost_unused_max=0;
 bool time_seen=false;LONGLONG min_qpc=0,max_qpc=0,previous_qpc=0;uint64_t backwards_delivery=0,equal_delivery=0,negative_timestamps=0;
 const char* fatal=nullptr;
 void Stop(const char* reason){if(!fatal)fatal=reason;}
 void Inspect(const EVENT_RECORD* record){
  if(callbacks==(std::numeric_limits<uint64_t>::max)()){Stop("CALLBACK_COUNTER_OVERFLOW");return;}++callbacks;
  if(fatal){++callbacks_after_failure;return;}if(!record){++null_callbacks;Stop("NULL_EVENT_RECORD");return;}
  EventKey key{record->EventHeader.ProviderId,record->EventHeader.EventDescriptor.Id,record->EventHeader.EventDescriptor.Version,record->EventHeader.EventDescriptor.Opcode};
  auto existing=groups.find(key);if(existing==groups.end()){if(groups.size()>=max_groups){Stop("EVENT_GROUP_BUDGET");return;}existing=groups.emplace(key,EventStats{}).first;}
  EventStats& stats=existing->second;++stats.events;
  const LONGLONG timestamp=record->EventHeader.TimeStamp.QuadPart;
  if(time_seen){if(timestamp<previous_qpc)++backwards_delivery;if(timestamp==previous_qpc)++equal_delivery;min_qpc=(std::min)(min_qpc,timestamp);max_qpc=(std::max)(max_qpc,timestamp);}else{time_seen=true;min_qpc=max_qpc=timestamp;}previous_qpc=timestamp;if(timestamp<0)++negative_timestamps;
  if(IsEqualGUID(key.provider,kLost)){if(key.opcode==32)++lost_event_notifications;else if(key.opcode==33)++lost_buffer_notifications;else if(key.opcode==34)++lost_file_notifications;}
  const USHORT count=record->ExtendedDataCount;stats.declared_items+=count;bool bad=false,duplicate=false,inspectable=true;unsigned psk_count=0;bool psk_bad=false;
  const bool flag=(record->EventHeader.Flags&EVENT_HEADER_FLAG_EXTENDED_INFO)!=0;
  if(flag!=(count!=0)){++stats.header_flag_mismatch;bad=true;}
  if(count==0){++stats.no_extended_items;if(record->ExtendedData){++stats.array_with_zero_count;bad=true;inspectable=false;}}
  else if(!record->ExtendedData){++stats.null_array;bad=true;inspectable=false;}
  if(inspectable){
   for(unsigned index=0;index<count;++index){
    EVENT_HEADER_EXTENDED_DATA_ITEM item{};if(!CopyItem(record->ExtendedData,static_cast<USHORT>(index),&item)){++stats.unreadable_array;bad=true;inspectable=false;break;}
    const auto ext_key=std::make_pair(item.ExtType,item.DataSize);auto ext=stats.extended.find(ext_key);
    if(ext==stats.extended.end()){if(extended_rows>=max_extended_rows){Stop("EXTENDED_ROW_BUDGET");return;}ext=stats.extended.emplace(ext_key,ExtStats{}).first;++extended_rows;}
    ExtStats& data=ext->second;++data.items;++stats.inspected_items;if(data.last_ordinal!=callbacks){++data.events;data.last_ordinal=callbacks;}
    if(seen[item.ExtType]==callbacks){++data.duplicate_items;++stats.duplicate_items;duplicate=true;}else seen[item.ExtType]=callbacks;
    bool malformed=false;if(item.DataPtr==0){++data.null_data;malformed=true;}if(item.DataSize==0){++data.zero_size;malformed=true;}
    const bool reserved=item.Reserved1!=0||item.Linkage!=0||item.Reserved2!=0;if(reserved){++data.reserved_nonzero;malformed=true;}
    if(item.ExtType==0)malformed=true;
    if(item.ExtType==EVENT_HEADER_EXT_TYPE_PROCESS_START_KEY){
     ++psk_count;if(item.DataSize!=sizeof(EVENT_EXTENDED_ITEM_PROCESS_START_KEY)){++data.psk_wrong_size;malformed=true;}
     if(item.DataSize==sizeof(EVENT_EXTENDED_ITEM_PROCESS_START_KEY)&&item.DataPtr!=0&&!ReadablePsk(item.DataPtr)){++data.psk_unreadable;malformed=true;}
     if(malformed)psk_bad=true;
    }
    if(malformed){++data.malformed_items;bad=true;}
   }
  }
  if(duplicate)++stats.duplicate_type_events;if(bad)++stats.malformed_events;
  if(!inspectable)++stats.psk_unknown_uninspectable;
  else if(psk_count>1)++stats.psk_unknown_duplicate;
  else if(psk_count==1){if(psk_bad||bad)++stats.psk_unknown_malformed;else ++stats.psk_candidate;}
  else if(bad)++stats.psk_unknown_malformed;else ++stats.psk_absent;
  ++fully_inspected_events;
 }
 void Buffer(const EVENT_TRACE_LOGFILEW* log){
  ++buffer_callbacks;if(!log){Stop("NULL_BUFFER_RECORD");return;}buffer_read_last=log->BuffersRead;buffer_read_max=(std::max)(buffer_read_max,static_cast<uint64_t>(log->BuffersRead));
  buffer_size_max=(std::max)(buffer_size_max,static_cast<uint64_t>(log->BufferSize));buffer_filled_max=(std::max)(buffer_filled_max,static_cast<uint64_t>(log->Filled));
  callback_header_events_lost_max=(std::max)(callback_header_events_lost_max,log->LogfileHeader.EventsLost);callback_header_buffers_lost_max=(std::max)(callback_header_buffers_lost_max,log->LogfileHeader.BuffersLost);callback_events_lost_unused_max=(std::max)(callback_events_lost_unused_max,log->EventsLost);
 }
 bool DescriptorCoverage()const{for(const auto& group:groups){const EventStats& s=group.second;if(s.null_array||s.array_with_zero_count||s.unreadable_array||s.declared_items!=s.inspected_items)return false;}return fatal==nullptr;}
 bool Conservation()const{uint64_t events=0;for(const auto& group:groups){const EventStats& s=group.second;events+=s.events;if(s.events!=s.psk_absent+s.psk_candidate+s.psk_unknown_duplicate+s.psk_unknown_malformed+s.psk_unknown_uninspectable)return false;uint64_t items=0;for(const auto& ext:s.extended){items+=ext.second.items;if(ext.second.events>ext.second.items||ext.second.duplicate_items>ext.second.items)return false;}if(items!=s.inspected_items)return false;}return events==fully_inspected_events&&fully_inspected_events==callbacks;}
};
static Context* active=nullptr;
static void WINAPI Receive(EVENT_RECORD* record) noexcept {
 if(!active)return;try{if(record&&record->UserContext!=active){++active->event_context_mismatches;active->Stop("EVENT_CONTEXT_MISMATCH");active->Inspect(nullptr);return;}active->Inspect(record);}catch(const std::bad_alloc&){active->Stop("CALLBACK_ALLOCATION_FAILURE");}catch(...){active->Stop("CALLBACK_CPP_FAILURE");}
}
static ULONG WINAPI Buffer(EVENT_TRACE_LOGFILEW* log) noexcept {
 if(!active)return FALSE;try{if(log&&log->Context!=active){++active->buffer_context_mismatches;active->Stop("BUFFER_CONTEXT_MISMATCH");active->Buffer(nullptr);}else active->Buffer(log);}catch(...){active->Stop("BUFFER_CPP_FAILURE");}return active->fatal?FALSE:TRUE;
}
struct ScanStatus {
 bool input_opened=false,pre_hash_match=false,post_hash_match=false,held_identity_match=false,open_called=false,opened=false,clock_supported=false,process_called=false,close_called=false,conservation=false;
 bool input_close_called=false;uint64_t input_close_attempted=0,input_close_errors=0;DWORD input_close_first_error=0;
 DWORD open_error=0,process_rc=0,close_rc=0;const char* failure=nullptr;DWORD failure_code=0;TRACE_LOGFILE_HEADER header{};
 bool Complete(const Context& context)const{return !failure&&input_opened&&pre_hash_match&&post_hash_match&&held_identity_match&&input_close_called&&input_close_errors==0&&opened&&clock_supported&&process_called&&process_rc==0&&close_called&&close_rc==0&&!context.fatal&&conservation&&context.DescriptorCoverage();}
};
static void EventJson(std::ostringstream& out,const EventStats& s){
#define FIELD(name) out<<"\"" #name "\":"<<s.name<<",";
 FIELD(events) FIELD(declared_items) FIELD(inspected_items) FIELD(no_extended_items) FIELD(null_array) FIELD(array_with_zero_count) FIELD(unreadable_array) FIELD(header_flag_mismatch) FIELD(duplicate_type_events) FIELD(duplicate_items) FIELD(malformed_events)
 FIELD(psk_absent) FIELD(psk_candidate) FIELD(psk_unknown_duplicate) FIELD(psk_unknown_malformed) FIELD(psk_unknown_uninspectable)
#undef FIELD
 out<<"\"extended\":[";bool comma=false;for(const auto& row:s.extended){if(comma)out<<",";comma=true;const ExtStats& x=row.second;out<<"{\"ext_type\":"<<row.first.first<<",\"data_size\":"<<row.first.second<<",";
#define FIELD(name) out<<"\"" #name "\":"<<x.name<<",";
 FIELD(items) FIELD(events) FIELD(duplicate_items) FIELD(null_data) FIELD(zero_size) FIELD(reserved_nonzero) FIELD(psk_wrong_size) FIELD(psk_unreadable)
#undef FIELD
 out<<"\"malformed_items\":"<<x.malformed_items<<"}";}out<<"]";
}
static std::string AggregateJson(const Context& c,const ScanStatus& s,bool memory=false){
 std::ostringstream out;out.imbue(std::locale::classic());out<<"{\"schema\":\"P309_SAVED_EXTENDED_V8\",\"version\":1,\"scope\":\""<<(memory?"MEMORY_ONLY":"FIXED_SAVED_ETL_AGGREGATES_ONLY")<<"\",\"admission\":\"BLOCKED\",\"identity_inference\":\"UNKNOWN\",\"psk_semantics\":\"EVENT_HEADER_EMITTER_ONLY;NEVER_PAYLOAD_CHILD_IDENTITY;VALUES_NOT_RETAINED\",\"expected_input_sha256\":\""<<kInputSha<<"\",\"expected_input_bytes\":"<<kInputSize;
 out<<",\"status\":{\"scan_complete\":"<<B(s.Complete(c))<<",\"input_opened\":"<<B(s.input_opened)<<",\"input_pre_hash_match\":"<<B(s.pre_hash_match)<<",\"input_post_hash_match\":"<<B(s.post_hash_match)<<",\"held_input_identity_match\":"<<B(s.held_identity_match)<<",\"open_trace_called\":"<<B(s.open_called)<<",\"open_trace_succeeded\":"<<B(s.opened)<<",\"open_trace_error\":"<<s.open_error<<",\"process_trace_called\":"<<B(s.process_called)<<",\"process_rc\":";if(s.process_called)out<<s.process_rc;else out<<"null";
 out<<",\"close_trace_called\":"<<B(s.close_called)<<",\"close_rc\":";if(s.close_called)out<<s.close_rc;else out<<"null";
 out<<",\"input_close_called\":"<<B(s.input_close_called)<<",\"input_close_attempted\":"<<s.input_close_attempted<<",\"input_close_errors\":"<<s.input_close_errors<<",\"input_close_first_error\":"<<s.input_close_first_error;
 out<<",\"conservation_valid\":"<<B(s.conservation)<<",\"descriptor_coverage_complete\":"<<B(c.DescriptorCoverage())<<",\"failure_stage\":";if(s.failure)out<<"\""<<s.failure<<"\"";else out<<"null";out<<",\"failure_code\":"<<s.failure_code<<",\"callback_failure\":";if(c.fatal)out<<"\""<<c.fatal<<"\"";else out<<"null";out<<"}";
 out<<",\"clock\":{\"raw_timestamp_mode\":true,\"clock_type\":"<<s.header.ReservedFlags<<",\"qpc_frequency\":"<<s.header.PerfFreq.QuadPart<<",\"supported_qpc_clock\":"<<B(s.clock_supported)<<",\"header_start_filetime\":"<<s.header.StartTime.QuadPart<<",\"header_end_filetime\":"<<s.header.EndTime.QuadPart<<",\"header_boot_filetime\":"<<s.header.BootTime.QuadPart<<",\"header_pointer_size\":"<<s.header.PointerSize<<",\"header_processors\":"<<s.header.NumberOfProcessors<<",\"first_observed_min_qpc\":";if(c.time_seen)out<<c.min_qpc;else out<<"null";out<<",\"last_observed_max_qpc\":";if(c.time_seen)out<<c.max_qpc;else out<<"null";out<<",\"delivery_backwards_count\":"<<c.backwards_delivery<<",\"delivery_equal_timestamp_count\":"<<c.equal_delivery<<",\"negative_timestamp_events\":"<<c.negative_timestamps<<",\"delivery_order_is_identity_proof\":false}";
 out<<",\"loss\":{\"open_header_events_lost\":"<<s.header.EventsLost<<",\"open_header_buffers_lost\":"<<s.header.BuffersLost<<",\"callback_header_events_lost_max\":"<<c.callback_header_events_lost_max<<",\"callback_header_buffers_lost_max\":"<<c.callback_header_buffers_lost_max<<",\"event_trace_logfile_events_lost_unused_raw_max\":"<<c.callback_events_lost_unused_max<<",\"event_trace_logfile_events_lost_is_valid_loss_counter\":false,\"documented_lost_event_notifications\":"<<c.lost_event_notifications<<",\"documented_lost_buffer_notifications\":"<<c.lost_buffer_notifications<<",\"documented_lost_file_notifications\":"<<c.lost_file_notifications<<",\"zero_observations_certify_capture_completeness\":false}";
 out<<",\"counts\":{\"event_callbacks\":"<<c.callbacks<<",\"fully_inspected_events\":"<<c.fully_inspected_events<<",\"callbacks_after_failure\":"<<c.callbacks_after_failure<<",\"null_event_callbacks\":"<<c.null_callbacks<<",\"event_context_mismatches\":"<<c.event_context_mismatches<<",\"buffer_context_mismatches\":"<<c.buffer_context_mismatches<<",\"event_groups\":"<<c.groups.size()<<",\"extended_rows\":"<<c.extended_rows<<",\"buffer_callbacks\":"<<c.buffer_callbacks<<",\"buffers_read_last\":"<<c.buffer_read_last<<",\"buffers_read_max\":"<<c.buffer_read_max<<",\"buffer_size_max\":"<<c.buffer_size_max<<",\"buffer_filled_max\":"<<c.buffer_filled_max<<"},\"budgets\":{\"max_event_groups\":"<<c.max_groups<<",\"max_extended_rows\":"<<c.max_extended_rows<<"},\"events\":[";
 bool comma=false;for(const auto& group:c.groups){if(comma)out<<",";comma=true;out<<"{\"provider\":\""<<Guid(group.first.provider)<<"\",\"id\":"<<group.first.id<<",\"version\":"<<static_cast<unsigned>(group.first.version)<<",\"opcode\":"<<static_cast<unsigned>(group.first.opcode)<<",";EventJson(out,group.second);out<<"}";}out<<"]}\n";return out.str();
}
struct IoStatus {DWORD write_error=0,flush_error=0,close_error=0;uint64_t bytes=0;bool Ok()const{return write_error==0&&flush_error==0&&close_error==0;}};
static IoStatus WriteAndClose(Handle& h,const std::string& data){
 IoStatus status;size_t at=0;while(at<data.size()){const DWORD n=static_cast<DWORD>((std::min)(data.size()-at,static_cast<size_t>(1048576)));DWORD written=0;if(!WriteFile(h.h,data.data()+at,n,&written,nullptr)){status.write_error=GetLastError();break;}if(written==0||written>n){status.write_error=ERROR_WRITE_FAULT;break;}at+=written;status.bytes+=written;}
 if(!FlushFileBuffers(h.h))status.flush_error=GetLastError();status.close_error=h.Close();return status;
}
static std::wstring ExecutableDirectory(){std::vector<wchar_t> path(32768);DWORD n=GetModuleFileNameW(nullptr,path.data(),static_cast<DWORD>(path.size()));if(n==0||n>=path.size())Fail("SELF_IMAGE_PATH",ERROR_INVALID_DATA);std::wstring s(path.data(),n);const size_t slash=s.find_last_of(L'\\');if(slash==std::wstring::npos)Fail("SELF_IMAGE_PATH",ERROR_INVALID_DATA);return s.substr(0,slash);}
static bool ValidAttempt(const wchar_t* value){const size_t n=wcslen(value);if(n==0||n>64)return false;for(size_t i=0;i<n;++i)if(!(value[i]>=L'a'&&value[i]<=L'z')&&!(value[i]>=L'A'&&value[i]<=L'Z')&&!(value[i]>=L'0'&&value[i]<=L'9')&&value[i]!=L'-')return false;return true;}
static int ScanSaved(const wchar_t* attempt){
 if(!ValidAttempt(attempt)){fputs("INVALID_FRESH_ATTEMPT_NAME; no input opened\n",stderr);return 64;}
 Handle aggregate,completion,directory_pin;PinnedInput input;bool directory_created=false;Context context;ScanStatus status;TRACEHANDLE trace=INVALID_PROCESSTRACE_HANDLE;
 try{
  const std::wstring directory=ExecutableDirectory()+L"\\scan-"+attempt;if(!CreateDirectoryW(directory.c_str(),nullptr))Fail("CREATE_NEW_ATTEMPT_DIRECTORY",GetLastError());directory_created=true;
  directory_pin=OpenFile(directory.c_str(),GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,OPEN_EXISTING,FILE_FLAG_BACKUP_SEMANTICS|FILE_FLAG_OPEN_REPARSE_POINT,"PIN_NEW_OUTPUT_DIRECTORY");Facts(directory_pin.h,true);
  Handle marker=OpenFile((directory+L"\\STARTED.txt").c_str(),GENERIC_WRITE,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,"CREATE_NEW_MARKER");IoStatus marker_io=WriteAndClose(marker,"FIXED_SAVED_EXTENDED_AGGREGATION_STARTED\nPARTIAL_UNLESS_COMPLETION_JSON_IS_COMPLETE_AND_EXIT_CODE_IS_ZERO\nNO_AUTOMATIC_RETRY_OR_OUTPUT_REPLACEMENT\n");if(!marker_io.Ok())Fail("START_MARKER_IO",marker_io.write_error?marker_io.write_error:(marker_io.flush_error?marker_io.flush_error:marker_io.close_error));
  aggregate=OpenFile((directory+L"\\aggregate.json").c_str(),GENERIC_WRITE,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,"CREATE_NEW_AGGREGATE");completion=OpenFile((directory+L"\\completion.json").c_str(),GENERIC_WRITE,0,CREATE_NEW,FILE_FLAG_WRITE_THROUGH,"CREATE_NEW_COMPLETION");
  input.Open();status.input_opened=true;if(HashFile(input.leaf.h)!=kInputSha)Fail("INPUT_PRE_HASH_MISMATCH",ERROR_INVALID_DATA);status.pre_hash_match=true;input.CheckIdentity();
  EVENT_TRACE_LOGFILEW log{};log.LogFileName=const_cast<wchar_t*>(kInput);log.LoggerName=nullptr;log.ProcessTraceMode=PROCESS_TRACE_MODE_EVENT_RECORD|PROCESS_TRACE_MODE_RAW_TIMESTAMP;log.EventRecordCallback=Receive;log.BufferCallback=Buffer;log.Context=&context;
  status.open_called=true;trace=OpenTraceW(&log);if(trace==INVALID_PROCESSTRACE_HANDLE){status.open_error=GetLastError();Fail("OPEN_TRACE",status.open_error);}status.opened=true;status.header=log.LogfileHeader;
  status.clock_supported=status.header.ReservedFlags==1&&status.header.PerfFreq.QuadPart>0;if(!status.clock_supported)Fail("UNSUPPORTED_RAW_CLOCK",ERROR_INVALID_DATA);
  active=&context;status.process_called=true;status.process_rc=ProcessTrace(&trace,1,nullptr,nullptr);active=nullptr;status.close_called=true;status.close_rc=CloseTrace(trace);trace=INVALID_PROCESSTRACE_HANDLE;
  input.CheckIdentity();status.held_identity_match=true;if(HashFile(input.leaf.h)!=kInputSha)Fail("INPUT_POST_HASH_MISMATCH",ERROR_INVALID_DATA);status.post_hash_match=true;status.conservation=context.Conservation();
 }catch(const Error& error){status.failure=error.stage;status.failure_code=error.code;}catch(const std::bad_alloc&){status.failure="ALLOCATION_FAILURE";status.failure_code=ERROR_NOT_ENOUGH_MEMORY;}catch(...){status.failure="CPP_FAILURE";status.failure_code=ERROR_INVALID_DATA;}
 active=nullptr;if(trace!=INVALID_PROCESSTRACE_HANDLE){status.close_called=true;status.close_rc=CloseTrace(trace);trace=INVALID_PROCESSTRACE_HANDLE;}
 status.input_close_called=true;input.Close(status.input_close_attempted,status.input_close_errors,status.input_close_first_error);
 try{
  const bool scan_complete=status.Complete(context);if(aggregate.h==INVALID_HANDLE_VALUE||completion.h==INVALID_HANDLE_VALUE){fprintf(stderr,"RESULT PARTIAL stage=%s code=%lu attempt_directory_created=%u; preserve any created files; no retry\n",status.failure?status.failure:"OUTPUT_NOT_OPEN",status.failure_code,directory_created?1U:0U);return 2;}
  const std::string report=AggregateJson(context,status);const std::string report_sha=HashBytes(report);const IoStatus report_io=WriteAndClose(aggregate,report);const bool complete=scan_complete&&report_io.Ok();
  std::ostringstream receipt;receipt.imbue(std::locale::classic());receipt<<"{\"schema\":\"P309_SAVED_EXTENDED_V8_COMPLETION\",\"version\":1,\"complete\":"<<B(complete)<<",\"scan_complete\":"<<B(scan_complete)<<",\"aggregate_sha256\":\""<<report_sha<<"\",\"aggregate_bytes\":"<<report.size()<<",\"aggregate_written_bytes\":"<<report_io.bytes<<",\"aggregate_write_error\":"<<report_io.write_error<<",\"aggregate_flush_error\":"<<report_io.flush_error<<",\"aggregate_close_error\":"<<report_io.close_error<<",\"admission\":\"BLOCKED\",\"identity_inference\":\"UNKNOWN\",\"valid_only_with_zero_process_exit_and_successful_completion_io\":true}\n";
  const IoStatus completion_io=WriteAndClose(completion,receipt.str());const DWORD directory_close_error=directory_pin.Close();const bool succeeded=complete&&completion_io.Ok()&&directory_close_error==0;printf("{\"result\":\"%s\",\"event_callbacks\":%llu,\"fully_inspected_events\":%llu,\"aggregate_io_ok\":%s,\"completion_write_error\":%lu,\"completion_flush_error\":%lu,\"completion_close_error\":%lu,\"output_directory_close_error\":%lu,\"exit_code\":%u,\"admission\":\"BLOCKED\"}\n",succeeded?"COMPLETE":"PARTIAL",context.callbacks,context.fully_inspected_events,B(report_io.Ok()),completion_io.write_error,completion_io.flush_error,completion_io.close_error,directory_close_error,succeeded?0U:2U);return succeeded?0:2;
 }catch(...){fputs("RESULT PARTIAL SERIALIZATION_OR_OUTPUT_FAILURE; preserve attempt; no retry\n",stderr);return 2;}
}

static void Require(bool condition,const char* label){if(!condition)Fail(label,ERROR_INVALID_DATA);}
static EVENT_RECORD Record(EVENT_HEADER_EXTENDED_DATA_ITEM* items=nullptr,USHORT count=0){EVENT_RECORD e{};e.EventHeader.Size=sizeof(EVENT_HEADER);e.EventHeader.ProviderId=GUID{0x12345678,0x1122,0x3344,{1,2,3,4,5,6,7,8}};e.EventHeader.EventDescriptor.Id=5;e.EventHeader.EventDescriptor.Version=3;e.EventHeader.EventDescriptor.Opcode=1;e.EventHeader.TimeStamp.QuadPart=100;e.ExtendedData=items;e.ExtendedDataCount=count;if(count)e.EventHeader.Flags|=EVENT_HEADER_FLAG_EXTENDED_INFO;return e;}
static EVENT_HEADER_EXTENDED_DATA_ITEM Item(USHORT type,USHORT size,const void* pointer){EVENT_HEADER_EXTENDED_DATA_ITEM item{};item.ExtType=type;item.DataSize=size;item.DataPtr=reinterpret_cast<ULONGLONG>(pointer);return item;}
static const EventStats& Only(const Context& c){Require(c.groups.size()==1,"SELFTEST_ONE_GROUP");return c.groups.begin()->second;}
static int SelfTest(){
 unsigned passed=0;auto test=[&passed](const char* label,auto work){work();++passed;printf("PASS %s\n",label);};
 try{
  test("absent-is-not-key",[]{Context c;auto e=Record();c.Inspect(&e);Require(Only(c).psk_absent==1&&c.Conservation()&&c.DescriptorCoverage(),"ABSENT");});
  test("nonnull-zero-count-array-unknown",[]{Context c;auto item=Item(3,4,nullptr);auto e=Record(&item,0);c.Inspect(&e);Require(Only(c).array_with_zero_count==1&&Only(c).psk_unknown_uninspectable==1&&!c.DescriptorCoverage(),"ZERO_ARRAY");});
  test("positive-count-null-array-unknown",[]{Context c;auto e=Record(nullptr,1);c.Inspect(&e);Require(Only(c).null_array==1&&Only(c).psk_unknown_uninspectable==1&&!c.DescriptorCoverage(),"NULL_ARRAY");});
  test("psk-eight-readable-bytes-only-candidate",[]{Context c;ULONG64 key=17;auto item=Item(13,8,&key);auto e=Record(&item,1);c.Inspect(&e);Require(Only(c).psk_candidate==1&&c.Conservation(),"VALID_PSK");});
  test("psk-wrong-size-unknown",[]{Context c;ULONG64 key=17;auto item=Item(13,7,&key);auto e=Record(&item,1);c.Inspect(&e);Require(Only(c).psk_unknown_malformed==1&&Only(c).extended.begin()->second.psk_wrong_size==1,"SHORT_PSK");});
  test("psk-null-data-unknown",[]{Context c;auto item=Item(13,8,nullptr);auto e=Record(&item,1);c.Inspect(&e);Require(Only(c).psk_unknown_malformed==1&&Only(c).extended.begin()->second.null_data==1,"NULL_PSK");});
  test("psk-unreadable-data-unknown",[]{Context c;auto item=Item(13,8,reinterpret_cast<void*>(1));auto e=Record(&item,1);c.Inspect(&e);Require(Only(c).extended.begin()->second.psk_unreadable==1&&Only(c).psk_unknown_malformed==1,"UNREADABLE_PSK");});
  test("duplicate-psk-even-same-bytes-unknown",[]{Context c;ULONG64 key=17;EVENT_HEADER_EXTENDED_DATA_ITEM items[]={Item(13,8,&key),Item(13,8,&key)};auto e=Record(items,2);c.Inspect(&e);Require(Only(c).psk_unknown_duplicate==1&&Only(c).duplicate_items==1&&Only(c).extended.begin()->second.events==1&&c.Conservation(),"DUPLICATE_PSK");});
  test("same-type-different-size-counts-duplicate",[]{Context c;ULONG64 key=17;EVENT_HEADER_EXTENDED_DATA_ITEM items[]={Item(13,8,&key),Item(13,4,&key)};auto e=Record(items,2);c.Inspect(&e);Require(Only(c).extended.size()==2&&Only(c).duplicate_type_events==1&&Only(c).psk_unknown_duplicate==1,"DIFFERENT_SIZE");});
  test("reserved-bits-are-not-adopted",[]{Context c;ULONG64 key=17;auto item=Item(13,8,&key);item.Reserved1=1;auto e=Record(&item,1);c.Inspect(&e);Require(Only(c).psk_unknown_malformed==1&&Only(c).extended.begin()->second.reserved_nonzero==1,"RESERVED");});
  test("unrecognized-type-retained-as-numeric-aggregate",[]{Context c;auto item=Item(65535,65535,nullptr);auto e=Record(&item,1);c.Inspect(&e);Require(Only(c).extended.begin()->first.first==65535&&Only(c).extended.begin()->first.second==65535&&Only(c).psk_unknown_malformed==1,"UNKNOWN_TYPE");});
  test("all-items-visited-no-first-item-shortcut",[]{Context c;ULONG64 data=17;EVENT_HEADER_EXTENDED_DATA_ITEM items[]={Item(3,4,&data),Item(13,8,&data),Item(2,8,&data)};auto e=Record(items,3);c.Inspect(&e);Require(Only(c).inspected_items==3&&Only(c).extended.size()==3&&Only(c).psk_candidate==1&&c.Conservation(),"ALL_ITEMS");});
  test("provider-id-version-opcode-are-distinct",[]{Context c;auto e=Record();c.Inspect(&e);++e.EventHeader.EventDescriptor.Id;c.Inspect(&e);++e.EventHeader.EventDescriptor.Version;c.Inspect(&e);++e.EventHeader.EventDescriptor.Opcode;c.Inspect(&e);++e.EventHeader.ProviderId.Data1;c.Inspect(&e);Require(c.groups.size()==5&&c.Conservation(),"GROUP_KEYS");});
  test("documented-loss-provider-required",[]{Context c;auto e=Record();e.EventHeader.EventDescriptor.Opcode=32;c.Inspect(&e);e.EventHeader.ProviderId=kLost;c.Inspect(&e);e.EventHeader.EventDescriptor.Opcode=33;c.Inspect(&e);e.EventHeader.EventDescriptor.Opcode=34;c.Inspect(&e);Require(c.lost_event_notifications==1&&c.lost_buffer_notifications==1&&c.lost_file_notifications==1,"LOSS_GUID");});
  test("raw-clock-order-reported-never-causal",[]{Context c;auto e=Record();e.EventHeader.TimeStamp.QuadPart=5;c.Inspect(&e);e.EventHeader.TimeStamp.QuadPart=-3;c.Inspect(&e);c.Inspect(&e);Require(c.backwards_delivery==1&&c.equal_delivery==1&&c.negative_timestamps==2&&c.min_qpc==-3&&c.max_qpc==5,"CLOCK_COUNTS");});
  test("invalid-descriptor-array-is-partial-not-crash",[]{Context c;auto e=Record(reinterpret_cast<EVENT_HEADER_EXTENDED_DATA_ITEM*>(1),1);c.Inspect(&e);Require(Only(c).unreadable_array==1&&Only(c).psk_unknown_uninspectable==1&&!c.DescriptorCoverage(),"UNREADABLE_ARRAY");});
  test("header-flag-mismatch-does-not-certify-key",[]{Context c;ULONG64 key=17;auto item=Item(13,8,&key);auto e=Record(&item,1);e.EventHeader.Flags=0;c.Inspect(&e);Require(Only(c).header_flag_mismatch==1&&Only(c).psk_unknown_malformed==1,"FLAG_MISMATCH");});
  test("budget-refusal-preserves-partial-state",[]{Context c;c.max_groups=1;auto e=Record();c.Inspect(&e);++e.EventHeader.EventDescriptor.Id;c.Inspect(&e);c.Inspect(&e);Require(c.fatal&&c.callbacks==3&&c.fully_inspected_events==1&&c.callbacks_after_failure==1&&!c.Conservation(),"GROUP_BUDGET");Context x;x.max_extended_rows=0;ULONG64 key=17;auto item=Item(13,8,&key);e=Record(&item,1);x.Inspect(&e);Require(x.fatal&&x.extended_rows==0&&!x.Conservation(),"EXT_BUDGET");});
  test("pid-path-key-values-never-affect-serialization",[]{Context a,b;ULONG64 first=0x1122334455667788ULL,second=0x8877665544332211ULL;auto one=Item(13,8,&first),two=Item(13,8,&second);auto e=Record(&one,1),f=Record(&two,1);e.EventHeader.ProcessId=123456789;e.EventHeader.ThreadId=223456789;f.EventHeader.ProcessId=987654321;f.EventHeader.ThreadId=887654321;const char secret[]="PRIVATE_PATH_SENTINEL";e.UserData=const_cast<char*>(secret);e.UserDataLength=sizeof(secret);a.Inspect(&e);b.Inspect(&f);ScanStatus s;Require(AggregateJson(a,s,true)==AggregateJson(b,s,true),"NO_RAW_IDENTITY_VALUES");Require(AggregateJson(a,s,true).find(secret)==std::string::npos,"NO_PAYLOAD_PATH");});
  test("completion-requires-api-input-clock-and-coverage",[]{Context c;auto e=Record();c.Inspect(&e);ScanStatus s;Require(!s.Complete(c),"NO_FAKE_COMPLETION");s.input_opened=s.pre_hash_match=s.post_hash_match=s.held_identity_match=s.input_close_called=s.opened=s.clock_supported=s.process_called=s.close_called=s.conservation=true;Require(s.Complete(c),"COMPLETE_PREDICATE");s.close_rc=ERROR_INVALID_HANDLE;Require(!s.Complete(c),"CLOSE_REFUSAL");s.close_rc=0;s.input_close_errors=1;Require(!s.Complete(c),"INPUT_CLOSE_REFUSAL");});
  test("buffer-loss-counters-not-summed-as-cumulative",[]{Context c;EVENT_TRACE_LOGFILEW log{};log.BuffersRead=2;log.LogfileHeader.EventsLost=7;log.LogfileHeader.BuffersLost=3;log.EventsLost=99;c.Buffer(&log);log.BuffersRead=3;c.Buffer(&log);Require(c.buffer_callbacks==2&&c.buffer_read_last==3&&c.callback_header_events_lost_max==7&&c.callback_events_lost_unused_max==99,"BUFFER_COUNTS");});
  printf("{\"result\":\"PASS\",\"memory_checks\":%u,\"scope\":\"SYNTHETIC_EVENT_RECORDS_ONLY\",\"actual_etl_reads\":0,\"open_trace_calls\":0,\"host_queries\":0,\"admission\":\"BLOCKED\"}\n",passed);return 0;
 }catch(const Error& error){fprintf(stderr,"SELF_TEST_FAIL stage=%s code=%lu passed=%u\n",error.stage,error.code,passed);return 1;}catch(...){fprintf(stderr,"SELF_TEST_FAIL CPP_FAILURE passed=%u\n",passed);return 1;}
}
} // namespace p309v8
int wmain(int argc,wchar_t** argv){
 try{
  if(argc==2&&wcscmp(argv[1],L"--self-test")==0)return p309v8::SelfTest();
  if(argc==3&&wcscmp(argv[1],L"--scan-saved")==0)return p309v8::ScanSaved(argv[2]);
  fputs("USAGE: --self-test OR --scan-saved <fresh-alphanumeric-hyphen-attempt>; fixed saved ETL only; no automatic scan\n",stderr);return 64;
 }catch(...){fputs("RESULT PARTIAL INITIALIZATION_FAILURE; no automatic retry; preserve any created files\n",stderr);return 2;}
}
