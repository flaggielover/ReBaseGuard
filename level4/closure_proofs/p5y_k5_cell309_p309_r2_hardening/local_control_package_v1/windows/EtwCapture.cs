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
using System.Web.Script.Serialization;
[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.System32)]

internal static class EtwCapture {
    internal const string Name = "ReBaseGuard-P309-I2-Feasibility-v1";
    internal static readonly Guid Owner = new Guid("b65ec272-436b-45e5-a4e3-87fddbc73a80");
    internal const string Root = @"C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v1";
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
                p.MaxFileMB=256; p.Mode=0x02000001; p.FlushSeconds=1;
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
    static string HypervisorSample() {
        var rows=new List<object>();
        foreach(string category in new [] {"Hyper-V Hypervisor Logical Processor", "Hyper-V Hypervisor Root Virtual Processor", "Hyper-V Hypervisor Virtual Processor"}) {
            string[] instances=new PerformanceCounterCategory(category).GetInstanceNames();
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
            scope="RAW_PROVIDER_ACCESS_ONLY_NOT_ATTRIBUTION_OR_COVERAGE", rows=rows });
    }
    static string Fixture() {
        var psi=new ProcessStartInfo(Path.Combine(Root,"EtwCapture.exe"),"--fixture-child-approved");
        psi.UseShellExecute=false;psi.CreateNoWindow=true;psi.WorkingDirectory=Root;
        using(Process p=Process.Start(psi)) {
            IntPtr held=p.Handle;
            int pid=p.Id;long creation=p.StartTime.ToUniversalTime().ToFileTimeUtc();
            if(!p.WaitForExit(3000)) {
                p.Kill();p.WaitForExit(3000);
                throw new InvalidOperationException("owned fixture timeout; no retry");
            }
            if(p.ExitCode!=0) throw new InvalidOperationException("owned fixture failed");
            return new JavaScriptSerializer().Serialize(new { scope="OWNED_SHORT_LIFETIME_CPU_FIXTURE_ONLY",
                pid=pid,creation_filetime=creation,exit_filetime=p.ExitTime.ToUniversalTime().ToFileTimeUtc(),
                cpu_ticks=p.TotalProcessorTime.Ticks,exit_code=p.ExitCode });
        }
    }
    static Props Query(ulong handle) {
        using(Buffer b=new Buffer(false)) {
            uint rc=ControlTraceW(handle,handle==0?Name:null,b.Ptr,0);
            if(rc!=0) throw new InvalidOperationException("query failed: "+rc);
            Props p=b.Read(); if(p.Wnode.Guid!=Owner) throw new InvalidOperationException("foreign session identity");
            return p;
        }
    }
    static string Stop(ulong handle) {
        // Never stop a session selected by a supplied name, PID or arbitrary GUID.
        Query(handle);
        using(Buffer b=new Buffer(false)) {
            uint rc=ControlTraceW(handle,handle==0?Name:null,b.Ptr,1);
            string result=Stats("stop",rc,b.Read());
            if(rc!=0) throw new InvalidOperationException(result);
            return result;
        }
    }
    static int Capture() {
        Admin(); Parents();
        // Same trusted operator/admin boundary as V4. This is not a privileged
        // broker accepting untrusted paths or a persistent installation.
        string log=Path.Combine(Root,"controller.jsonl");
        if(File.Exists(Path.Combine(Root,"capture.etl"))) throw new IOException("ETL collision");
        string[] ready=File.ReadAllLines(Path.Combine(Root,"watchdog.ready"));
        if(ready.Length!=2) throw new IOException("watchdog readiness malformed");
        int guardPid=Int32.Parse(ready[0],System.Globalization.CultureInfo.InvariantCulture);
        long guardStart=Int64.Parse(ready[1],System.Globalization.CultureInfo.InvariantCulture);
        using(Process guard=Process.GetProcessById(guardPid)) {
            if(guard.HasExited || guard.StartTime.ToUniversalTime().Ticks!=guardStart
                || DateTime.UtcNow.Ticks-guardStart<0
                || DateTime.UtcNow.Ticks-guardStart>TimeSpan.FromSeconds(5).Ticks)
                throw new IOException("watchdog not fresh/alive");
        }
        using(ProfilePrivilege privilege=new ProfilePrivilege())
        using(FileStream fs=new FileStream(log,FileMode.CreateNew,FileAccess.Write,FileShare.Read))
        using(StreamWriter output=new StreamWriter(fs,new UTF8Encoding(false)))
        using(FileStream counters=new FileStream(Path.Combine(Root,"hypervisor-raw.jsonl"),FileMode.CreateNew,FileAccess.Write,FileShare.Read))
        using(StreamWriter counterOutput=new StreamWriter(counters,new UTF8Encoding(false))) {
            ulong handle=0; bool started=false; bool clean=false;
            Stopwatch elapsed=Stopwatch.StartNew();
            try {
                using(Buffer b=new Buffer(true)) {
                    uint rc=StartTraceW(out handle,Name,b.Ptr);
                    started=rc==0;
                    output.WriteLine(Stats("start",rc,b.Read()));output.Flush();fs.Flush(true);
                    if(rc!=0) throw new InvalidOperationException("StartTrace failed: "+rc+"; no retry/adoption");
                }
                counterOutput.WriteLine(HypervisorSample());counterOutput.Flush();
                long sampleStart=elapsed.ElapsedMilliseconds;
                for(int i=1;i<=60;i++) {
                    long due=sampleStart+i*1000;
                    while(elapsed.ElapsedMilliseconds<due) Thread.Sleep(10);
                    Props p=Query(handle);
                    output.WriteLine(Stats("query",0,p));output.Flush();
                    counterOutput.WriteLine(HypervisorSample());counterOutput.Flush();
                    if(i==3 || i==6 || i==9) {output.WriteLine(Fixture());output.Flush();}
                    if(counters.Length>16777216) throw new InvalidOperationException("counter evidence budget exceeded");
                    if(p.Lost!=0 || p.LogLost!=0 || p.RealLost!=0 || elapsed.ElapsedMilliseconds>65000)
                        throw new InvalidOperationException("trace loss or capture deadline");
                }
            } finally {
                // Native stop happens before evidence flushing. A separate
                // approved watchdog is still REQUIRED for controller failure.
                if(started) {
                    string stopped=Stop(handle); clean=true;
                    output.WriteLine(stopped);output.Flush();fs.Flush(true);
                    var end=new JavaScriptSerializer().Deserialize<Dictionary<string,object>>(stopped);
                    if(Convert.ToUInt64(end["events_lost"])!=0 || Convert.ToUInt64(end["log_buffers_lost"])!=0
                        || Convert.ToUInt64(end["realtime_buffers_lost"])!=0)
                        throw new InvalidOperationException("final trace loss");
                }
            }
            return clean?0:2;
        }
    }
    static int Watchdog() {
        Admin(); Parents();
        // Separate process: an ordinary controller exception or process exit
        // does not cancel this timeout. This is not a real-time OS guarantee.
        using(FileStream log=new FileStream(Path.Combine(Root,"watchdog.jsonl"),FileMode.CreateNew,FileAccess.Write,FileShare.Read))
        using(StreamWriter output=new StreamWriter(log,new UTF8Encoding(false))) {
            Stopwatch timer=Stopwatch.StartNew();
            using(FileStream ready=new FileStream(Path.Combine(Root,"watchdog.pending"),FileMode.CreateNew,FileAccess.Write,FileShare.None))
            using(StreamWriter w=new StreamWriter(ready,new UTF8Encoding(false))) {
                using(Process me=Process.GetCurrentProcess()) {
                    w.WriteLine(me.Id);w.WriteLine(me.StartTime.ToUniversalTime().Ticks);
                    w.Flush();ready.Flush(true);
                }
            }
            File.Move(Path.Combine(Root,"watchdog.pending"),Path.Combine(Root,"watchdog.ready"));
            while(timer.ElapsedMilliseconds<75000) Thread.Sleep(50);
            using(Buffer b=new Buffer(false)) {
                uint rc=ControlTraceW(0,Name,b.Ptr,0);
                if(rc==4201) {output.WriteLine(Stats("watchdog_session_absent",rc,b.Read()));output.Flush();log.Flush(true);return 0;}
                if(rc!=0 || b.Read().Wnode.Guid!=Owner) throw new InvalidOperationException("watchdog refuses unknown session: "+rc);
            }
            output.WriteLine(Stop(0));output.Flush();log.Flush(true);
            return 2; // Successful emergency stop is still capture FAILURE.
        }
    }
    static int Layout() {
        if(IntPtr.Size!=8 || Marshal.SizeOf(typeof(Wnode))!=48 || Marshal.SizeOf(typeof(Props))!=120
            || Marshal.SizeOf(typeof(TokenPrivilege))!=16 || Marshal.SizeOf(typeof(Luid))!=8
            || Marshal.OffsetOf(typeof(Props),"ThreadId").ToInt32()!=104
            || Marshal.OffsetOf(typeof(Props),"FileOffset").ToInt32()!=112)
            throw new InvalidOperationException("native ABI mismatch");
        using(Buffer b=new Buffer(true)) {
            Props p=b.Read();
            if(p.EnableFlags!=0x77 || p.Mode!=0x02000001 || p.MaxFileMB!=256 || p.Wnode.Guid!=Owner)
                throw new InvalidOperationException("fixed properties mismatch");
        }
        Console.WriteLine("ABI_AND_FIXED_CONFIGURATION_ONLY; NO_TRACE_STARTED");return 0;
    }
    static int Main(string[] args) {
        try {
            if(args.Length!=1) return 64;
            if(args[0]=="--layout-check") return Layout();
            if(args[0]=="--capture-approved") {Layout();return Capture();}
            if(args[0]=="--watchdog-approved") {Layout();return Watchdog();}
            if(args[0]=="--fixture-child-approved") {
                // Only the reviewed capture invokes this fixed 200-ms fixture.
                Stopwatch spin=Stopwatch.StartNew();long value=1;
                while(spin.ElapsedMilliseconds<200) value=unchecked(value*6364136223846793005L+1);
                GC.KeepAlive(value);return 0;
            }
            if(args[0]=="--query-own") {
                Admin();
                using(Buffer b=new Buffer(false)) {
                    uint rc=ControlTraceW(0,Name,b.Ptr,0);
                    Console.WriteLine(Stats("final_query",rc,b.Read()));
                    if(rc==4201) return 0;
                    if(rc!=0 || b.Read().Wnode.Guid!=Owner) return 1;
                    return 3;
                }
            }
            if(args[0]=="--stop-own-approved") {
                Admin();Console.WriteLine(Stop(0));return 0;
            }
            return 64;
        } catch(Exception ex){Console.Error.WriteLine(ex.ToString());return 1;}
    }
}
