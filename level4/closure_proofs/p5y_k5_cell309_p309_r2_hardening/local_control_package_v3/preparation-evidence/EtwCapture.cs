// Preparation only. Native capture/stop entry points require separate consent.
// No signing, classification, admission, services or policy. Fixture timeout
// termination uses only its own retained Process handle, never a supplied PID.
using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;
using System.Threading;
using System.Collections.Generic;
using System.ComponentModel;
using System.Security.Cryptography;
using System.Web.Script.Serialization;
[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.System32)]

internal static class EtwCapture {
    internal const string Name = "ReBaseGuard-P309-I2-RootDiagnostic-v3";
    internal static Guid Owner = Guid.Empty;
    internal const string Root = @"C:\ProgramData\ReBaseGuardP309-I2-RootDiagnostic-v3";
    [StructLayout(LayoutKind.Sequential)] internal struct Wnode {
        internal uint Size, Provider; internal ulong Historical;
        internal long Timestamp; internal Guid Guid; internal uint Clock, Flags;
    }
    [StructLayout(LayoutKind.Sequential)] internal struct Props {
        internal Wnode Wnode;
        internal uint BufferKB, MinBuffers, MaxBuffers, MaxFileMB, Mode, FlushSeconds, EnableFlags;
        internal int Age;
        internal uint Buffers, Free, Lost, Written, LogLost, RealLost;
        internal IntPtr ThreadId; internal uint FileOffset, NameOffset;
    }
    [DllImport("advapi32.dll", CharSet=CharSet.Unicode, ExactSpelling=true)]
    internal static extern uint StartTraceW(out ulong handle, string name, IntPtr properties);
    [DllImport("advapi32.dll", CharSet=CharSet.Unicode, ExactSpelling=true)]
    internal static extern uint ControlTraceW(ulong handle, string name, IntPtr properties, uint code);
    [StructLayout(LayoutKind.Sequential)] internal struct TokenPrivilege {
        internal uint Count, Low;internal int High;internal uint Attributes;
    }
    [StructLayout(LayoutKind.Sequential)] internal struct Luid { internal uint Low;internal int High; }
    [DllImport("kernel32.dll")] static extern IntPtr GetCurrentProcess();
    [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr handle);
    [DllImport("advapi32.dll",SetLastError=true)] static extern bool OpenProcessToken(IntPtr process,uint access,out IntPtr token);
    [DllImport("advapi32.dll",CharSet=CharSet.Unicode,ExactSpelling=true,SetLastError=true)] static extern bool LookupPrivilegeValueW(string system,string name,out Luid luid);
    [DllImport("advapi32.dll",SetLastError=true)] static extern bool AdjustTokenPrivileges(IntPtr token,bool disableAll,ref TokenPrivilege state,uint bytes,out TokenPrivilege previous,out uint returned);
    sealed class ProfilePrivilege : IDisposable {
        IntPtr token=IntPtr.Zero;TokenPrivilege previous;bool changed=false;
        internal ProfilePrivilege() {
            try {
                Luid luid;
                if(!OpenProcessToken(GetCurrentProcess(),0x28,out token)
                    || !LookupPrivilegeValueW(null,"SeSystemProfilePrivilege",out luid))
                    throw new InvalidOperationException("profile token access failed: "+Marshal.GetLastWin32Error());
                TokenPrivilege requested=new TokenPrivilege();requested.Count=1;requested.Low=luid.Low;requested.High=luid.High;requested.Attributes=2;
                uint size;
                if(!AdjustTokenPrivileges(token,false,ref requested,16,out previous,out size))
                    throw new InvalidOperationException("profile token enable failed: "+Marshal.GetLastWin32Error());
                int error=Marshal.GetLastWin32Error();
                if(error!=0) throw new InvalidOperationException("profile privilege not assigned: "+error+"; no policy fallback");
                changed=true;
            } catch {if(token!=IntPtr.Zero){CloseHandle(token);token=IntPtr.Zero;}throw;}
        }
        public void Dispose() {
            try {
                if(changed) {
                    TokenPrivilege ignored;uint size;
                    if(!AdjustTokenPrivileges(token,false,ref previous,16,out ignored,out size) || Marshal.GetLastWin32Error()!=0)
                        throw new InvalidOperationException("profile token restore failed; process exit drops this token");
                }
            } finally {if(token!=IntPtr.Zero){CloseHandle(token);token=IntPtr.Zero;}}
        }
    }

    internal sealed class Buffer : IDisposable {
        internal IntPtr Ptr;
        internal Buffer(bool capture) {
            int size=Marshal.SizeOf(typeof(Props)), total=size+2048+2048;
            Ptr=Marshal.AllocHGlobal(total);
            Marshal.Copy(new byte[total],0,Ptr,total);
            Props p=new Props(); p.Wnode.Size=(uint)total;
            p.Wnode.Guid=Owner; p.Wnode.Clock=1; p.Wnode.Flags=0x00020000;
            p.NameOffset=(uint)size; p.FileOffset=(uint)(size+2048);
            if(capture) {
                p.BufferKB=64; p.MinBuffers=64; p.MaxBuffers=256;
                p.MaxFileMB=1024; p.Mode=0x02000001; p.FlushSeconds=1;
                // PROCESS | THREAD | IMAGE_LOAD | CSWITCH | DPC | INTERRUPT.
                // No sampled-profile, file/network payload or stack collection.
                p.EnableFlags=0x77;
            }
            Marshal.StructureToPtr(p,Ptr,false);
            byte[] file=Encoding.Unicode.GetBytes(Path.Combine(Root,"capture.etl")+"\0");
            if(file.Length>2048) throw new InvalidOperationException("ETL path too long");
            Marshal.Copy(file,0,IntPtr.Add(Ptr,(int)p.FileOffset),file.Length);
        }
        internal Props Read(){return (Props)Marshal.PtrToStructure(Ptr,typeof(Props));}
        public void Dispose(){if(Ptr!=IntPtr.Zero){Marshal.FreeHGlobal(Ptr);Ptr=IntPtr.Zero;}}
    }

    static void Admin() {
        using(WindowsIdentity id=WindowsIdentity.GetCurrent())
            if(!new WindowsPrincipal(id).IsInRole(WindowsBuiltInRole.Administrator))
                throw new InvalidOperationException("elevated capture approval required; no automatic elevation");
    }
    static void Parents() {
        DirectoryInfo d=new DirectoryInfo(Root);
        while(d!=null) {
            if(!d.Exists || (d.Attributes&FileAttributes.ReparsePoint)!=0)
                throw new InvalidOperationException("missing/reparse record parent");
            d=d.Parent;
        }
    }
    static string Stats(string stage,uint status,Props p) {
        return String.Format(System.Globalization.CultureInfo.InvariantCulture,
            "{{\"stage\":\"{0}\",\"utc\":\"{1:o}\",\"status\":{2},\"guid\":\"{3}\",\"events_lost\":{4},\"log_buffers_lost\":{5},\"realtime_buffers_lost\":{6},\"buffers_written\":{7},\"buffers\":{8},\"buffer_kb\":{9},\"enable_flags\":{10},\"mode\":{11}}}",
            stage,DateTime.UtcNow,status,p.Wnode.Guid,p.Lost,p.LogLost,p.RealLost,p.Written,p.Buffers,p.BufferKB,p.EnableFlags,p.Mode);
    }
    internal static string HypervisorSample() {
        var rows=new List<object>();
        var availability=new List<object>();
        foreach(string category in new [] {"Hyper-V Hypervisor Logical Processor", "Hyper-V Hypervisor Root Virtual Processor", "Hyper-V Hypervisor Virtual Processor"}) {
            string[] instances;
            try {instances=new PerformanceCounterCategory(category).GetInstanceNames();}
            catch(Exception ex) {availability.Add(new { category=category,status="ERROR",error=ex.Message });continue;}
            availability.Add(new {category=category,status=instances.Length==0?"UNAVAILABLE":"INSTANCES_PRESENT_NOT_VALIDATED",count=instances.Length});
            if(instances.Length>256) throw new InvalidOperationException("counter instance budget exceeded");
            foreach(string instance in instances)
                foreach(string counter in new [] {"% Total Run Time", "% Guest Run Time", "% Hypervisor Run Time"})
                    using(PerformanceCounter pc=new PerformanceCounter(category,counter,instance,true)) {
                        CounterSample s=pc.NextSample();
                        rows.Add(new { category=category, instance=instance, counter=counter,
                            raw=s.RawValue, basis=s.BaseValue, timestamp=s.TimeStamp,
                            timestamp100ns=s.TimeStamp100nSec, counterTimestamp=s.CounterTimeStamp,
                            frequency=s.SystemFrequency, counterFrequency=s.CounterFrequency,
                            type=(int)s.CounterType });
                    }
        }
        return new JavaScriptSerializer().Serialize(new { utc=DateTime.UtcNow.ToString("o"),
            scope="RAW_PROVIDER_ACCESS_ONLY_NOT_ATTRIBUTION_OR_COVERAGE",availability=availability,
            rows=rows,coverage_complete=false,admission="BLOCKED" });
    }

    // No name-based stop API exists in this executable. Only the creator uses
    // its successful StartTrace handle. A collision never produces a receipt.
    static Props Query(ulong handle,StreamWriter evidence=null,FileStream durable=null) {
        if(handle==0 || Owner==Guid.Empty) throw new IOException("unowned query");
        using(Buffer b=new Buffer(false)) {
            uint rc=ControlTraceW(handle,null,b.Ptr,0);
            Props p=b.Read();
            // Persist the triggering status/loss before rejecting it. A failed
            // query's output fields are NOT trustworthy kernel statistics.
            if(evidence!=null) {evidence.WriteLine(Json(new {query=Stats("query",rc,p),
                expected_guid=Owner.ToString(),statistics_valid=rc==0&&p.Wnode.Guid==Owner}));
                evidence.Flush();durable.Flush(true);}
            if(rc!=0 || p.Wnode.Guid!=Owner) throw new IOException("owned query failed: "+rc);
            return p;
        }
    }
    static string Stop(ulong handle) {
        Query(handle);
        using(Buffer b=new Buffer(false)) {
            uint rc=ControlTraceW(handle,null,b.Ptr,1);
            if(rc!=0) throw new IOException("owned stop failed: "+rc);
            return Stats("stop",rc,b.Read());
        }
    }
    internal static void Publish(string name,string value) {
        using(var f=new FileStream(Path.Combine(Root,name+".pending"),FileMode.CreateNew,FileAccess.Write,FileShare.None))
        using(var w=new StreamWriter(f,new UTF8Encoding(false))) {w.Write(value);w.Flush();f.Flush(true);}
        File.Move(Path.Combine(Root,name+".pending"),Path.Combine(Root,name));
    }
    static string Json(object value) {return new JavaScriptSerializer().Serialize(value);}
    internal static void Check(bool ok,string reason) {if(!ok) throw new Win32Exception(Marshal.GetLastWin32Error(),reason);}
    sealed class TraceLease {
        readonly ulong handle; readonly Thread timer;
        int state; internal bool Emergency; internal string Result; internal Exception Failure;
        internal TraceLease(ulong owned,Stopwatch elapsed) {
            handle=owned;
            timer=new Thread(delegate() {
                while(Volatile.Read(ref state)==0 && elapsed.ElapsedMilliseconds<75000) Thread.Sleep(25);
                if(Volatile.Read(ref state)==0) StopOnce(true);
            });
            timer.IsBackground=true;timer.Start();
        }
        void StopOnce(bool emergency) {
            if(Interlocked.CompareExchange(ref state,1,0)!=0) return;
            Emergency=emergency;
            try {Result=Stop(handle);} catch(Exception ex){Failure=ex;}
            finally {Volatile.Write(ref state,2);}
        }
        internal string Finish() {
            StopOnce(false);
            if(!timer.Join(5000) || Volatile.Read(ref state)!=2) throw new IOException("trace stop in flight; UNKNOWN");
            if(Failure!=null) throw new IOException("owned trace stop failed",Failure);
            if(Emergency) throw new IOException("75-second independent timer fired; capture FAILED");
            return Result;
        }
    }
    static int Guard() {
        Admin();Parents();
        Owner=Guid.NewGuid();
        ulong handle=0;bool started=false;bool sampleDone=false;string stop=null;TraceLease lease=null;
        // Guard owns the ETW session. The counter sampler can fail or disappear
        // without cancelling this process's deadline. Abrupt loss of the guard
        // itself is UNKNOWN, not permission to adopt a same-name session.
        Stopwatch elapsed=Stopwatch.StartNew();
        using(ProfilePrivilege privilege=new ProfilePrivilege())
        using(var log=new FileStream(Path.Combine(Root,"guard.jsonl"),FileMode.CreateNew,FileAccess.Write,FileShare.Read))
        using(var writer=new StreamWriter(log,new UTF8Encoding(false))) {
            try {
                if(File.Exists(Path.Combine(Root,"capture.etl"))) throw new IOException("ETL collision");
                using(Buffer b=new Buffer(true)) {
                    uint rc=StartTraceW(out handle,Name,b.Ptr);
                    started=rc==0;
                    if(!started) throw new IOException("StartTrace failed: "+rc+"; no adoption or retry");
                    if(handle==0) throw new IOException("successful start with invalid handle");
                    lease=new TraceLease(handle,elapsed);
                    writer.WriteLine(Stats("start",rc,b.Read()));writer.Flush();
                }
                using(Process me=Process.GetCurrentProcess()) {
                    Publish("session-created.json",Json(new { guid=Owner.ToString(),handle=handle.ToString(),
                        guard_pid=me.Id,guard_creation=me.StartTime.ToUniversalTime().ToFileTimeUtc(),
                        utc=DateTime.UtcNow.ToString("o"),start_succeeded=true }));
                }
                int fixture=0;bool whpDone=false;
                while(elapsed.ElapsedMilliseconds<75000) {
                    if(fixture<3 && elapsed.ElapsedMilliseconds>=(fixture+1)*3000) {
                        writer.WriteLine(OwnedFixture.Run(false));writer.Flush();fixture++;
                    }
                    if(!whpDone && elapsed.ElapsedMilliseconds>=15000) {
                        writer.WriteLine(OwnedFixture.Run(true));writer.Flush();whpDone=true;
                    }
                    if(File.Exists(Path.Combine(Root,"sampler-done.json"))) {sampleDone=true;break;}
                    if(File.Exists(Path.Combine(Root,"sampler-failed.json"))) throw new IOException("sampler failed");
                    Thread.Sleep(50);
                }
                if(!sampleDone || fixture!=3 || !whpDone) throw new IOException("sampler deadline or incomplete fixture batch");
            } finally {
                if(started && handle!=0) {
                    try {stop=lease==null?Stop(handle):lease.Finish();} // stop before evidence output
                    catch(Exception ex) {writer.WriteLine(Json(new {stage="creator_stop_failed",error=ex.ToString(),
                        successful_stop=false,admission="BLOCKED"}));writer.Flush();log.Flush(true);throw;}
                    writer.WriteLine(stop);writer.Flush();log.Flush(true);
                    var end=new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(stop);
                    if(Convert.ToUInt64(end["events_lost"])!=0 || Convert.ToUInt64(end["log_buffers_lost"])!=0
                       || Convert.ToUInt64(end["realtime_buffers_lost"])!=0) throw new IOException("final trace loss");
                }
            }
        }
        Publish("guard-clean.json",Json(new { guid=Owner.ToString(),successful_stop=stop!=null,
            sampler_done=sampleDone,scope="ETW_THREE_NATIVE_AND_ONE_WHP_FIXTURE_ONLY",admission="BLOCKED" }));
        return 0;
    }
    static int Sampler() {
        Admin();Parents();
        var receipt=new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(File.ReadAllText(Path.Combine(Root,"session-created.json")));
        Owner=Guid.Parse((string)receipt["guid"]);
        ulong handle=UInt64.Parse((string)receipt["handle"]);
        if(!Convert.ToBoolean(receipt["start_succeeded"])) throw new IOException("start not acknowledged");
        using(Process guard=Process.GetProcessById(Convert.ToInt32(receipt["guard_pid"]))) {
            if(guard.HasExited || guard.StartTime.ToUniversalTime().ToFileTimeUtc()!=Convert.ToInt64(receipt["guard_creation"]))
                throw new IOException("creator identity differs");
            using(var file=new FileStream(Path.Combine(Root,"hypervisor-raw.jsonl"),FileMode.CreateNew,FileAccess.Write,FileShare.Read))
            using(var writer=new StreamWriter(file,new UTF8Encoding(false))) {
                Stopwatch clock=Stopwatch.StartNew();
                for(int i=0;i<=60;i++) {
                    while(clock.ElapsedMilliseconds<i*1000) Thread.Sleep(10);
                    if(guard.HasExited) throw new IOException("creator exited");
                    Props p=Query(handle,writer,file);
                    if(p.Lost!=0 || p.LogLost!=0 || p.RealLost!=0 || clock.ElapsedMilliseconds>65000)
                        throw new IOException("loss or sampler deadline");
                    writer.WriteLine(Json(new {session=Owner.ToString(),sample=HypervisorSample()}));writer.Flush();
                    if(file.Length>16777216) throw new IOException("counter evidence budget exceeded");
                }
                writer.Flush();file.Flush(true);
            }
        }
        Publish("sampler-done.json",Json(new {guid=Owner.ToString(),admission="BLOCKED"}));return 0;
    }
    static int QueryName() {
        // Read only. Name/GUID cannot authorize any stop.
        Admin();
        using(Buffer b=new Buffer(false)) {
            uint rc=ControlTraceW(0,Name,b.Ptr,0);
            Console.WriteLine(Stats("name_query_read_only",rc,b.Read()));
            return rc==4201?0:(rc==0?3:1);
        }
    }
    static int Layout() {
        if(IntPtr.Size!=8 || Marshal.SizeOf(typeof(Wnode))!=48 || Marshal.SizeOf(typeof(Props))!=120
            || Marshal.SizeOf(typeof(TokenPrivilege))!=16 || Marshal.SizeOf(typeof(Luid))!=8
            || Marshal.OffsetOf(typeof(Props),"ThreadId").ToInt32()!=104
            || Marshal.OffsetOf(typeof(Props),"FileOffset").ToInt32()!=112
            || Marshal.SizeOf(typeof(Native.Limits))!=144 || Marshal.SizeOf(typeof(Native.StartupEx))!=112)
            throw new IOException("native ABI mismatch");
        using(Buffer b=new Buffer(true)) {
            Props p=b.Read();
            if(p.EnableFlags!=0x77 || p.Mode!=0x02000001 || p.MaxFileMB!=1024) throw new IOException("fixed config differs");
        }
        Console.WriteLine("ABI_AND_FIXED_CONFIGURATION_ONLY; NO_TRACE_JOB_OR_FIXTURE_STARTED");return 0;
    }
    static int Main(string[] args) {
        try {
            if(args.Length!=1) return 64;
            if(args[0]=="--layout-check") return Layout();
            if(args[0]=="--guard-approved") {Layout();return Guard();}
            if(args[0]=="--sample-approved") {
                try {return Sampler();}
                catch {Publish("sampler-failed.json","{}\n");throw;}
            }
            if(args[0]=="--fixture-child-approved") {
                Stopwatch spin=Stopwatch.StartNew();long value=1;
                while(spin.ElapsedMilliseconds<200) value=unchecked(value*6364136223846793005L+1);
                GC.KeepAlive(value);return 0;
            }
            if(args[0]=="--query-name-readonly") return QueryName();
            return 64;
        } catch(Exception ex){Console.Error.WriteLine(ex.ToString());return 1;}
    }
}
    internal static class Native {
        [StructLayout(LayoutKind.Sequential)] internal struct Startup {
            internal int cb; internal IntPtr reserved, desktop, title;
            internal uint x, y, xSize, ySize, xCount, yCount, fill, flags;
            internal ushort show, reserved2; internal IntPtr reservedPtr, stdin, stdout, stderr;
        }
        [StructLayout(LayoutKind.Sequential)] internal struct ProcessInfo {
            internal IntPtr process, thread; internal uint pid, tid;
        }
        [StructLayout(LayoutKind.Sequential)] internal struct BasicLimits {
            internal long processTime, jobTime; internal uint flags;
            internal UIntPtr minWorkingSet, maxWorkingSet; internal uint activeLimit;
            internal UIntPtr affinity; internal uint priority, scheduling;
        }
        [StructLayout(LayoutKind.Sequential)] internal struct IoCounters {
            internal ulong readOps, writeOps, otherOps, readBytes, writeBytes, otherBytes;
        }
        [StructLayout(LayoutKind.Sequential)] internal struct Limits {
            internal BasicLimits basic; internal IoCounters io;
            internal UIntPtr processMemory, jobMemory, peakProcessMemory, peakJobMemory;
        }
        [StructLayout(LayoutKind.Sequential)] internal struct Accounting {
            internal long userTime, kernelTime, periodUser, periodKernel;
            internal uint pageFaults, totalProcesses, activeProcesses, terminatedProcesses;
        }
        [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
        internal static extern IntPtr CreateJobObject(IntPtr attributes, string name);
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool SetInformationJobObject(IntPtr job, int kind, ref Limits limits, uint bytes);
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool QueryInformationJobObject(IntPtr job, int kind, out Accounting data, uint bytes, IntPtr returned);
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool IsProcessInJob(IntPtr process, IntPtr job, out bool result);
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool TerminateJobObject(IntPtr job, uint code);
        [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
        internal static extern bool CreateProcess(string application, StringBuilder command,
            IntPtr processAttributes, IntPtr threadAttributes, bool inheritHandles,
            uint flags, IntPtr environment, string directory, ref StartupEx startup, out ProcessInfo info);
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool GetProcessTimes(IntPtr process, out long creation, out long exit, out long kernel, out long user);
        [DllImport("kernel32.dll", SetLastError=true)] internal static extern uint ResumeThread(IntPtr thread);
        [DllImport("kernel32.dll", SetLastError=true)] internal static extern bool TerminateProcess(IntPtr process, uint code);
        [DllImport("kernel32.dll", SetLastError=true)] internal static extern uint WaitForSingleObject(IntPtr handle, uint ms);
        [DllImport("kernel32.dll", SetLastError=true)] internal static extern bool GetExitCodeProcess(IntPtr process, out uint code);
        [DllImport("kernel32.dll")] internal static extern bool CloseHandle(IntPtr handle);
        [DllImport("kernel32.dll")] internal static extern ulong GetTickCount64();
        [DllImport("kernel32.dll")] internal static extern void ExitProcess(uint code);
        [DllImport("kernel32.dll")] internal static extern uint SetErrorMode(uint mode);

        [StructLayout(LayoutKind.Sequential)] internal struct StartupEx {
            internal Startup startup; internal IntPtr attributes;
        }
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool InitializeProcThreadAttributeList(IntPtr list, int count, uint flags, ref UIntPtr bytes);
        [DllImport("kernel32.dll", SetLastError=true)]
        internal static extern bool UpdateProcThreadAttribute(IntPtr list, uint flags, UIntPtr attribute, IntPtr value, UIntPtr bytes, IntPtr previous, IntPtr returned);
        [DllImport("kernel32.dll")] internal static extern void DeleteProcThreadAttributeList(IntPtr list);
        [DllImport("kernel32.dll", EntryPoint="QueryInformationJobObject", SetLastError=true)]
        internal static extern bool QueryLimits(IntPtr job, int kind, out Limits data, uint bytes, IntPtr returned);
        [DllImport("kernel32.dll", EntryPoint="QueryInformationJobObject", SetLastError=true)]
        internal static extern bool QueryPids(IntPtr job, int kind, IntPtr data, uint bytes, out uint returned);
        [DllImport("kernel32.dll", SetLastError=true)] internal static extern IntPtr OpenProcess(uint rights, bool inherit, uint pid);
        [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
        internal static extern bool QueryFullProcessImageName(IntPtr process, uint flags, StringBuilder text, ref uint length);

    }



internal static class OwnedFixture {
    internal static string Run(bool whp) {
        IntPtr job=IntPtr.Zero,attributes=IntPtr.Zero,jobValue=IntPtr.Zero,environment=IntPtr.Zero;
        Native.ProcessInfo child=new Native.ProcessInfo();bool attributesReady=false;
        try {
            job=Native.CreateJobObject(IntPtr.Zero,null);EtwCapture.Check(job!=IntPtr.Zero,"fixture job");
            Native.Limits limits=new Native.Limits();limits.basic.flags=0x2000|0x100|0x200|0x8;
            limits.basic.activeLimit=1;limits.processMemory=new UIntPtr(256UL*1024*1024);limits.jobMemory=limits.processMemory;
            EtwCapture.Check(Native.SetInformationJobObject(job,9,ref limits,(uint)Marshal.SizeOf(typeof(Native.Limits))),"fixture limits");
            Native.Limits effective;
            EtwCapture.Check(Native.QueryLimits(job,9,out effective,(uint)Marshal.SizeOf(typeof(Native.Limits)),IntPtr.Zero),"fixture effective limits");
            if(effective.basic.flags!=limits.basic.flags || effective.basic.activeLimit!=1 || effective.jobMemory!=limits.jobMemory
                || effective.processMemory!=limits.processMemory) throw new IOException("fixture limits differ");
            UIntPtr bytes=UIntPtr.Zero;Native.InitializeProcThreadAttributeList(IntPtr.Zero,1,0,ref bytes);
            if(bytes.ToUInt64()==0 || bytes.ToUInt64()>65536) throw new IOException("attribute size");
            attributes=Marshal.AllocHGlobal((int)bytes.ToUInt64());
            EtwCapture.Check(Native.InitializeProcThreadAttributeList(attributes,1,0,ref bytes),"fixture attributes");attributesReady=true;
            jobValue=Marshal.AllocHGlobal(IntPtr.Size);Marshal.WriteIntPtr(jobValue,job);
            EtwCapture.Check(Native.UpdateProcThreadAttribute(attributes,0,new UIntPtr(0x2000d),jobValue,new UIntPtr((uint)IntPtr.Size),IntPtr.Zero,IntPtr.Zero),"atomic fixture job");
            Native.StartupEx startup=new Native.StartupEx();startup.startup.cb=Marshal.SizeOf(typeof(Native.StartupEx));startup.attributes=attributes;
            // Fixed clean environment: no inherited CLR/profiler/plugin variables.
            string env="PATH=C:\\Windows\\System32\0SystemRoot=C:\\Windows\0TEMP="+EtwCapture.Root+"\0TMP="+EtwCapture.Root+"\0WINDIR=C:\\Windows\0\0";
            environment=Marshal.StringToHGlobalUni(env);
            string exe=Path.Combine(EtwCapture.Root,whp?"WhpCounterProbe.exe":"EtwCapture.exe");
            EtwCapture.Check(Native.CreateProcess(exe,new StringBuilder("\""+exe+"\" "+(whp?"--probe-approved":"--fixture-child-approved")),IntPtr.Zero,IntPtr.Zero,false,
                0x80000|0x400|0x8|0x4,environment,EtwCapture.Root,ref startup,out child),"create fixed detached fixture");
            bool inside;EtwCapture.Check(Native.IsProcessInJob(child.process,job,out inside)&&inside,"fixture membership");
            long creation,exit,kernel,user;EtwCapture.Check(Native.GetProcessTimes(child.process,out creation,out exit,out kernel,out user),"fixture identity");
            string prefix="fixture-"+child.pid.ToString(System.Globalization.CultureInfo.InvariantCulture);
            EtwCapture.Publish(prefix+"-created.json",new JavaScriptSerializer().Serialize(new {pid=child.pid,
                creation_filetime=creation,image=Path.GetFileName(exe),atomic_job_assignment=true,
                effective_flags=effective.basic.flags,job_memory_bytes=effective.jobMemory.ToUInt64(),
                process_memory_bytes=effective.processMemory.ToUInt64(),max_members=effective.basic.activeLimit}));
            if(Native.ResumeThread(child.thread)==UInt32.MaxValue) throw new Win32Exception();
            uint wait=Native.WaitForSingleObject(child.process,whp?8000u:3000u);
            if(wait!=0) {
                bool terminated=Native.TerminateJobObject(job,0x309);
                uint cleanup=Native.WaitForSingleObject(child.process,3000);
                EtwCapture.Publish(prefix+"-timeout.json",new JavaScriptSerializer().Serialize(new {pid=child.pid,
                    creation_filetime=creation,wait=wait,terminate_job_return=terminated,cleanup_wait=cleanup,
                    disposition="FAILED_OR_UNKNOWN",admission="BLOCKED"}));
                throw new IOException("fixture timeout/failure; wait="+wait+" cleanup="+cleanup);
            }
            uint code;EtwCapture.Check(Native.GetExitCodeProcess(child.process,out code),"fixture exit");
            EtwCapture.Check(Native.GetProcessTimes(child.process,out creation,out exit,out kernel,out user),"fixture times");
            Native.Accounting a;EtwCapture.Check(Native.QueryInformationJobObject(job,1,out a,(uint)Marshal.SizeOf(typeof(Native.Accounting)),IntPtr.Zero),"fixture final accounting");
            if(code!=0 || a.activeProcesses!=0 || a.totalProcesses!=1) throw new IOException("fixture cleanup not proven");
            return new JavaScriptSerializer().Serialize(new {scope=whp?"OWNED_WHP_COUNTER_FIXTURE_ONLY":"OWNED_SHORT_LIFETIME_CPU_FIXTURE_ONLY",pid=child.pid,
                creation_filetime=creation,exit_filetime=exit,cpu_ticks=kernel+user,exit_code=code,job_active=a.activeProcesses,
                job_total=a.totalProcesses,atomic_job_assignment=true,kill_on_close=true,handle_inheritance=false});
        } finally {
            // Closing the only non-inherited Job handle also covers creator exit.
            if(job!=IntPtr.Zero) Native.CloseHandle(job);
            if(child.thread!=IntPtr.Zero) Native.CloseHandle(child.thread);
            if(child.process!=IntPtr.Zero) Native.CloseHandle(child.process);
            if(attributesReady) Native.DeleteProcThreadAttributeList(attributes);
            if(attributes!=IntPtr.Zero) Marshal.FreeHGlobal(attributes);
            if(jobValue!=IntPtr.Zero) Marshal.FreeHGlobal(jobValue);
            if(environment!=IntPtr.Zero) Marshal.FreeHGlobal(environment);
        }
    }
}
