// Preparation/feasibility probe ONLY. No P309 launcher or grant interface.
// --diagnostic-unit-tests performs no native calls. Single real diagnosis requires NEW approval.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
[assembly: DefaultDllImportSearchPaths(DllImportSearchPath.System32)]

namespace P309.LocalVm {
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


    public static class OwnedVmProbe {
        // No caller-supplied QEMU switches, disks, network, commands, PID or job name.
        // Paused 128 MiB hardware probe; NOT the formal 8 GB capacity acceptance.
        const string FixedArgs = " -no-user-config -nodefaults -machine q35 -accel whpx,ssd=on" +
            " -smp 4 -m 128 -S -display none -serial none -monitor none -nic none";
        static int stopRequested, terminateSucceeded, nativeStopError;
        static long stopTick;

        public static string Quote(string value) {
            if (value.IndexOf('\0') >= 0 || value.IndexOf('\r') >= 0 || value.IndexOf('\n') >= 0)
                throw new ArgumentException("invalid path");
            StringBuilder result = new StringBuilder("\""); int slashes = 0;
            foreach(char c in value) {
                if (c == '\\') { slashes++; continue; }
                if (c == '"') { result.Append('\\', slashes * 2 + 1); result.Append(c); }
                else { result.Append('\\', slashes); result.Append(c); }
                slashes = 0;
            }
            result.Append('\\', slashes * 2); result.Append('"'); return result.ToString();
        }

        static void Check(bool value, string label) {
            if (!value) throw new Win32Exception(Marshal.GetLastWin32Error(), label);
        }
        static void NoReparse(string path) {
            for (string p = Path.GetFullPath(path); !String.IsNullOrEmpty(p); p = Path.GetDirectoryName(p))
                if ((File.GetAttributes(p) & FileAttributes.ReparsePoint) != 0)
                    throw new IOException("reparse point: " + p);
        }
        static string Hash(Stream stream) {
            using (SHA256 h = SHA256.Create())
                return BitConverter.ToString(h.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
        static List<FileStream> LockRuntime(string root, string list, string expectedListHash) {
            NoReparse(root); NoReparse(list);
            List<FileStream> held = new List<FileStream>();
            HashSet<string> names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            try {
                FileStream listFile = new FileStream(list, FileMode.Open, FileAccess.Read, FileShare.Read);
                held.Add(listFile);
                if (Hash(listFile) != expectedListHash) throw new IOException("approved hash list differs");
                listFile.Position = 0;
                string listText;
                using (StreamReader reader = new StreamReader(listFile, Encoding.UTF8, true, 4096, true)) listText = reader.ReadToEnd();
                foreach (string line in listText.Split(new char[] {'\r', '\n'}, StringSplitOptions.RemoveEmptyEntries)) {
                    if (line.Length < 67 || line.Substring(64, 2) != "  ") throw new IOException("invalid hash row");
                    string relative = line.Substring(66);
                    if (relative.IndexOf(':') >= 0 || Path.IsPathRooted(relative)) throw new IOException("invalid relative path");
                    string path = Path.GetFullPath(Path.Combine(root, relative.Replace('/', Path.DirectorySeparatorChar)));
                    string prefix = Path.GetFullPath(root).TrimEnd('\\') + "\\";
                    if (!path.StartsWith(prefix, StringComparison.OrdinalIgnoreCase) || !names.Add(path))
                        throw new IOException("path escape or duplicate");
                    NoReparse(path);
                    FileStream file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
                    held.Add(file);
                    if (Hash(file) != line.Substring(0, 64)) throw new IOException("runtime digest mismatch: " + relative);
                }
                string exe = Path.Combine(root, "ucrt64", "bin", "qemu-system-x86_64.exe");
                if (!names.Contains(Path.GetFullPath(exe))) throw new IOException("QEMU executable not bound");
                // Additional DLLs/modules could be loaded even if not in the hash list.
                foreach(string path in FilesWithoutReparse(root))
                    if (!names.Contains(Path.GetFullPath(path))) throw new IOException("unlisted runtime file: " + path);
                return held;
            } catch { foreach(FileStream f in held) f.Dispose(); throw; }
        }

        static IEnumerable<string> FilesWithoutReparse(string root) {
            foreach(string path in Directory.GetFileSystemEntries(root)) {
                FileAttributes attributes = File.GetAttributes(path);
                if ((attributes & FileAttributes.ReparsePoint) != 0) throw new IOException("reparse point: " + path);
                if ((attributes & FileAttributes.Directory) != 0) {
                    foreach(string nested in FilesWithoutReparse(path)) yield return nested;
                } else yield return path;
            }
        }

        internal static SortedDictionary<string,string> EnvironmentValues(string root,string scratch,string windows) {
            string drive=Path.GetPathRoot(windows).TrimEnd('\\');
            if(drive.Length!=2 || drive[1]!=':') throw new ArgumentException("local Windows drive required");
            SortedDictionary<string,string> env=new SortedDictionary<string,string>(StringComparer.OrdinalIgnoreCase);
            env.Add("PATH",Path.Combine(root,"ucrt64","bin")+";"+Path.Combine(windows,"System32"));
            env.Add("SystemRoot",windows);env.Add("windir",windows);env.Add("SystemDrive",drive);
            env.Add("TEMP",scratch);env.Add("TMP",scratch);
            env.Add("USERPROFILE",Path.Combine(scratch,"profile"));
            env.Add("APPDATA",Path.Combine(scratch,"profile","AppData","Roaming"));
            env.Add("LOCALAPPDATA",Path.Combine(scratch,"profile","AppData","Local"));
            env.Add("ProgramData",Path.Combine(scratch,"program-data"));
            env.Add("QEMU_MODULE_DIR",Path.Combine(root,"ucrt64","lib","qemu"));
            env.Add("QEMU_DATA_DIR",Path.Combine(root,"ucrt64","share","qemu"));
            return env;
        }
        static IntPtr EnvironmentBlock(string root,string scratch) {
            var env=EnvironmentValues(root,scratch,Environment.GetFolderPath(Environment.SpecialFolder.Windows));
            foreach(string name in new string[]{"TEMP","USERPROFILE","APPDATA","LOCALAPPDATA","ProgramData"})
                Directory.CreateDirectory(env[name]);
            StringBuilder block=new StringBuilder();
            foreach(KeyValuePair<string,string> item in env)block.Append(item.Key).Append('=').Append(item.Value).Append('\0');
            block.Append('\0');return Marshal.StringToHGlobalUni(block.ToString());
        }

        static uint Active(IntPtr job) {
            Native.Accounting data;
            Check(Native.QueryInformationJobObject(job, 1, out data,
                  (uint)Marshal.SizeOf(typeof(Native.Accounting)), IntPtr.Zero), "query job accounting");
            return data.activeProcesses;
        }

        static string Json(string value) {
            StringBuilder b = new StringBuilder("\"");
            foreach(char c in value) {
                if(c == '\\' || c == '"') b.Append('\\').Append(c);
                else if(c < 32) b.Append("\\u").Append(((int)c).ToString("x4"));
                else b.Append(c);
            }
            return b.Append('"').ToString();
        }
        // Fixed bounded buffer: partial/overflow/duplicate/invalid IDs are UNKNOWN, never PASS.
        internal static ulong[] ParsePids(byte[] raw, int returned) {
            if(returned < 8 || returned > raw.Length) throw new IOException("invalid PID list length");
            uint assigned = BitConverter.ToUInt32(raw,0), listed = BitConverter.ToUInt32(raw,4);
            if(assigned != listed || listed > 16 || returned < 8 + listed * 8)
                throw new IOException("incomplete PID list");
            ulong[] pids = new ulong[listed]; HashSet<ulong> seen = new HashSet<ulong>();
            for(int i=0;i<pids.Length;i++) {
                pids[i]=BitConverter.ToUInt64(raw,8+i*8);
                if(pids[i]==0 || pids[i]>UInt32.MaxValue || !seen.Add(pids[i])) throw new IOException("invalid PID");
            }
            return pids;
        }
        static string Member(IntPtr job, uint pid) {
            IntPtr p=Native.OpenProcess(0x00101000,false,pid); // query-limited + synchronize only
            if(p==IntPtr.Zero) return "{\"pid\":"+pid+",\"identity\":\"UNKNOWN\",\"open_error\":"+Marshal.GetLastWin32Error()+"}";
            try {
                bool inside;
                if(!Native.IsProcessInJob(p,job,out inside) || !inside)
                    return "{\"pid\":"+pid+",\"identity\":\"UNKNOWN\",\"reason\":\"membership_unbound\"}";
                long c,e,k,u;
                if(!Native.GetProcessTimes(p,out c,out e,out k,out u))
                    return "{\"pid\":"+pid+",\"identity\":\"UNKNOWN\",\"times_error\":"+Marshal.GetLastWin32Error()+"}";
                StringBuilder image=new StringBuilder(32768); uint length=32768;
                bool imageOk=Native.QueryFullProcessImageName(p,0,image,ref length);
                int imageError=imageOk ? 0 : Marshal.GetLastWin32Error();
                return "{\"pid\":"+pid+",\"creation_filetime\":"+c+",\"job_membership\":true,\"wait\":"+
                    Native.WaitForSingleObject(p,0)+",\"image\":"+(imageOk?Json(image.ToString()):"null")+
                    ",\"image_error\":"+imageError+"}";
            } finally {Native.CloseHandle(p);}
        }
        static void Snapshot(StreamWriter writer, IntPtr job, string stage) {
            Native.Accounting data;
            Check(Native.QueryInformationJobObject(job,1,out data,(uint)Marshal.SizeOf(typeof(Native.Accounting)),IntPtr.Zero),"accounting snapshot");
            const int size=8+16*8; IntPtr buffer=Marshal.AllocHGlobal(size);
            try {
                byte[] raw=new byte[size]; Marshal.Copy(raw,0,buffer,size);
                uint returned;
                bool ok=Native.QueryPids(job,3,buffer,size,out returned);
                int error=ok?0:Marshal.GetLastWin32Error(); string members="[]"; string parseError="null";
                Marshal.Copy(buffer,raw,0,size);
                if(ok) {
                    try {
                        ulong[] pids=ParsePids(raw,checked((int)returned)); StringBuilder b=new StringBuilder("[");
                        for(int i=0;i<pids.Length;i++){if(i>0)b.Append(',');b.Append(Member(job,(uint)pids[i]));}
                        members=b.Append(']').ToString();
                    } catch(Exception ex){parseError=Json(ex.Message);}
                }
                writer.WriteLine("{\"event\":\"job_snapshot\",\"stage\":"+Json(stage)+",\"tick_ms\":"+Native.GetTickCount64()+
                    ",\"active\":"+data.activeProcesses+",\"total\":"+data.totalProcesses+",\"terminated\":"+data.terminatedProcesses+
                    ",\"pid_query_error\":"+error+",\"pid_returned_bytes\":"+returned+
                    ",\"pid_buffer_base64\":"+Json(Convert.ToBase64String(raw))+
                    ",\"pid_parse_error\":"+parseError+",\"members\":"+members+"}");
            } finally {Marshal.FreeHGlobal(buffer);}
        }
        static void VerifyLimits(StreamWriter writer, IntPtr job, string stage) {
            Native.Limits data;
            Check(Native.QueryLimits(job,9,out data,(uint)Marshal.SizeOf(typeof(Native.Limits)),IntPtr.Zero),"read effective job limits");
            bool match=data.basic.flags==0x2308 && data.basic.activeLimit==1 &&
                data.processMemory.ToUInt64()==805306368 && data.jobMemory.ToUInt64()==805306368;
            writer.WriteLine("{\"event\":\"limits_readback\",\"stage\":"+Json(stage)+",\"flags\":"+data.basic.flags+
                ",\"active_limit\":"+data.basic.activeLimit+",\"process_memory\":"+data.processMemory.ToUInt64()+
                ",\"job_memory\":"+data.jobMemory.ToUInt64()+",\"match\":"+match.ToString().ToLowerInvariant()+"}");
            if(!match) throw new IOException("effective limits differ; no fallback");
        }

        static void Stop(IntPtr job) {
            // Native stop precedes every diagnostic/file operation. No shared
            // session lock, signer, logger, endpoint or guest response involved.
            if (Interlocked.Exchange(ref stopRequested, 1) == 0) {
                Interlocked.Exchange(ref stopTick, (long)Native.GetTickCount64());
                if (Native.TerminateJobObject(job, 0x309)) Interlocked.Exchange(ref terminateSucceeded, 1);
                else Interlocked.Exchange(ref nativeStopError, Marshal.GetLastWin32Error());
            }
        }

        static int Probe(string root, string hashList, string expectedListHash, string output) {
            if (Environment.Is64BitProcess == false) throw new InvalidOperationException("x64 required");
            if (!Path.GetFullPath(output).StartsWith(@"D:\ReBaseGuard-309\records\",StringComparison.OrdinalIgnoreCase))
                throw new IOException("diagnostic evidence must be under records");
            NoReparse(Path.GetDirectoryName(Path.GetFullPath(output)));
            if (File.Exists(output)) throw new IOException("evidence exists; no overwrite");
            // New evidence file is opened before VM creation. No app policies changed.
            using (FileStream record = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.Read))
            using (StreamWriter writer = new StreamWriter(record, new UTF8Encoding(false))) {
                writer.AutoFlush = true;
                List<FileStream> held = LockRuntime(root, hashList, expectedListHash);
                IntPtr job = IntPtr.Zero; Native.ProcessInfo process = new Native.ProcessInfo();
                Thread watchdog = null; bool assigned = false; IntPtr environment = IntPtr.Zero;
                IntPtr attributes=IntPtr.Zero, jobValue=IntPtr.Zero; bool attributesReady=false;
                try {
                    Native.SetErrorMode(0x0001 | 0x0002 | 0x8000); // Only this process / child, no system setting.
                    job = Native.CreateJobObject(IntPtr.Zero, null); Check(job != IntPtr.Zero, "create unnamed job");
                    Native.Limits limits = new Native.Limits();
                    limits.basic.flags = 0x2000 | 0x100 | 0x200 | 0x8; // kill-on-close, process/job memory, active count
                    limits.basic.activeLimit = 1; // no guest agent or child helper allowed in probe
                    limits.processMemory = new UIntPtr(768UL * 1024 * 1024);
                    limits.jobMemory = new UIntPtr(768UL * 1024 * 1024);
                    Check(Native.SetInformationJobObject(job, 9, ref limits,
                          (uint)Marshal.SizeOf(typeof(Native.Limits))), "job limits");
                    VerifyLimits(writer,job,"before_creation");
                    Snapshot(writer,job,"empty_before_creation");
                    string exe = Path.GetFullPath(Path.Combine(root, "ucrt64", "bin", "qemu-system-x86_64.exe"));
                    Native.StartupEx startup = new Native.StartupEx();
                    startup.startup.cb = Marshal.SizeOf(typeof(Native.StartupEx));
                    UIntPtr attributeBytes=UIntPtr.Zero;
                    Native.InitializeProcThreadAttributeList(IntPtr.Zero,1,0,ref attributeBytes);
                    if(attributeBytes.ToUInt64()==0 || attributeBytes.ToUInt64()>65536) throw new IOException("attribute size invalid");
                    attributes=Marshal.AllocHGlobal(checked((int)attributeBytes.ToUInt64()));
                    Check(Native.InitializeProcThreadAttributeList(attributes,1,0,ref attributeBytes),"initialize attributes");
                    attributesReady=true; jobValue=Marshal.AllocHGlobal(IntPtr.Size); Marshal.WriteIntPtr(jobValue,job);
                    Check(Native.UpdateProcThreadAttribute(attributes,0,new UIntPtr(0x0002000d),jobValue,
                        new UIntPtr((uint)IntPtr.Size),IntPtr.Zero,IntPtr.Zero),"atomic job-list attribute");
                    startup.attributes=attributes;
                    environment = EnvironmentBlock(root, Path.Combine(Path.GetDirectoryName(Path.GetFullPath(output)),"child-scratch"));
                    string data = Path.Combine(root, "ucrt64", "share", "qemu");
                    // CREATE_SUSPENDED | CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT;
                    // inheritHandles=false, minimal environment, no user plugin/data search.
                    Check(Native.CreateProcess(exe, new StringBuilder(Quote(exe) + FixedArgs + " -L " + Quote(data)),
                          IntPtr.Zero, IntPtr.Zero, false, 0x08080404, environment,
                          Path.Combine(Path.GetDirectoryName(Path.GetFullPath(output)),"child-scratch"), ref startup, out process), "create fixed QEMU suspended");
                    // Assignment is atomic with creation; no non-atomic fallback.
                    assigned = true; bool inside;
                    Check(Native.IsProcessInJob(process.process, job, out inside) && inside, "verify job membership");
                    long created, exited, kernel, user;
                    Check(Native.GetProcessTimes(process.process, out created, out exited, out kernel, out user), "creation identity");
                    ulong started = Native.GetTickCount64();
                    watchdog = new Thread(delegate() {
                        while (Volatile.Read(ref stopRequested) == 0 && Native.GetTickCount64() - started < 15000)
                            Thread.Sleep(25);
                        Stop(job);
                    });
                    watchdog.IsBackground = true; watchdog.Name = "P309 fixed probe deadline"; watchdog.Start();
                    Snapshot(writer,job,"suspended_child");
                    if (Native.ResumeThread(process.thread) == UInt32.MaxValue) throw new Win32Exception();
                    writer.WriteLine("{\"event\":\"owned_start\",\"pid\":" + process.pid +
                        ",\"creation_filetime\":" + created + ",\"handle_inheritance\":false," +
                        "\"job_assigned_before_resume\":true,\"atomic_job_assignment\":true,\"started_tick_ms\":"+started+",\"admission\":\"BLOCKED\"}");
                    record.Flush(true);
                    uint early = Native.WaitForSingleObject(process.process, 5000);
                    if (early != 258) {
                        uint earlyExit; Check(Native.GetExitCodeProcess(process.process, out earlyExit), "early exit code");
                        throw new InvalidOperationException("QEMU early exit/wait: " + early + "; exit code: " + earlyExit);
                    }
                    uint aliveCount=Active(job);
                    writer.WriteLine("{\"event\":\"alive_at_5s\",\"active_job_processes\":" + aliveCount + "}");
                    record.Flush(true);
                    VerifyLimits(writer,job,"alive_at_5s");
                    Snapshot(writer,job,"alive_at_5s");
                    // Preserve bounded identities, then revoke immediately on the known violation.
                    // The separate 15-second watchdog remains active during observation/logging.
                    if(aliveCount != 1) Stop(job);
                    uint wait = Native.WaitForSingleObject(process.process, 18000);
                    Stop(job);
                    if (watchdog != null && !watchdog.Join(2000)) throw new IOException("watchdog did not finish");
                    uint finalWait = Native.WaitForSingleObject(process.process, 5000);
                    uint active = Active(job); uint exitCode;
                    Check(Native.GetExitCodeProcess(process.process, out exitCode), "exit code");
                    bool cleanup = finalWait == 0 && active == 0 && terminateSucceeded == 1;
                    Snapshot(writer,job,"after_stop");
                    writer.WriteLine("{\"event\":\"stop_timing\",\"started_tick_ms\":"+started+",\"stop_tick_ms\":"+Interlocked.Read(ref stopTick)+",\"observed_tick_ms\":"+Native.GetTickCount64()+"}");
                    writer.WriteLine("{\"event\":\"cleanup\",\"wait\":" + wait + ",\"final_wait\":" + finalWait +
                        ",\"active_job_processes\":" + active + ",\"exit_code\":" + exitCode +
                        ",\"terminate_error\":" + nativeStopError + ",\"cleanup_proven\":" +
                        cleanup.ToString().ToLowerInvariant() + ",\"admission\":\"BLOCKED\"}");
                    record.Flush(true); return cleanup ? 0 : 3;
                } finally {
                    if (job != IntPtr.Zero) Stop(job);
                    if (process.process != IntPtr.Zero && !assigned) Native.TerminateProcess(process.process, 0x309);
                    // Never recycle a native handle while a watchdog may still use it.
                    // Exiting this guard closes only its own handles; KILL_ON_JOB_CLOSE remains armed.
                    if (watchdog != null && !watchdog.Join(2000)) Native.ExitProcess(87);
                    if (process.thread != IntPtr.Zero) Native.CloseHandle(process.thread);
                    if (process.process != IntPtr.Zero) Native.CloseHandle(process.process);
                    if (job != IntPtr.Zero) Native.CloseHandle(job);
                    if (environment != IntPtr.Zero) Marshal.FreeHGlobal(environment);
                    if(attributesReady) Native.DeleteProcThreadAttributeList(attributes);
                    if(attributes!=IntPtr.Zero) Marshal.FreeHGlobal(attributes);
                    if(jobValue!=IntPtr.Zero) Marshal.FreeHGlobal(jobValue);
                    foreach(FileStream f in held) f.Dispose();
                }
            }
        }
        static int DiagnosticUnitTests() {
            int tests=0; Action<bool> ok=delegate(bool v){tests++;if(!v)throw new Exception("diagnostic unit "+tests);};
            ok(IntPtr.Size==8);
            ok(Marshal.SizeOf(typeof(Native.Startup))==104);
            ok(Marshal.SizeOf(typeof(Native.StartupEx))==112);
            ok(Marshal.OffsetOf(typeof(Native.StartupEx),"attributes").ToInt32()==104);
            ok(Marshal.SizeOf(typeof(Native.Accounting))==48);
            ok(Marshal.OffsetOf(typeof(Native.Accounting),"activeProcesses").ToInt32()==40);
            ok(Marshal.SizeOf(typeof(Native.BasicLimits))==64);
            ok(Marshal.OffsetOf(typeof(Native.BasicLimits),"activeLimit").ToInt32()==40);
            ok(Marshal.SizeOf(typeof(Native.Limits))==144);
            ok(Marshal.OffsetOf(typeof(Native.Limits),"processMemory").ToInt32()==112);
            ok(ParsePids(new byte[8],8).Length==0);
            byte[] valid=new byte[24];BitConverter.GetBytes(2U).CopyTo(valid,0);BitConverter.GetBytes(2U).CopyTo(valid,4);
            BitConverter.GetBytes(123UL).CopyTo(valid,8);BitConverter.GetBytes(456UL).CopyTo(valid,16);
            ok(ParsePids(valid,24)[1]==456);
            for(int mode=0;mode<7;mode++) {
                byte[] bad=(byte[])valid.Clone();int length=24;
                if(mode==0)length=7;if(mode==1)length=25;if(mode==2)length=16;
                if(mode==3)BitConverter.GetBytes(3U).CopyTo(bad,0);
                if(mode==4)BitConverter.GetBytes(0UL).CopyTo(bad,8);
                if(mode==5)BitConverter.GetBytes(123UL).CopyTo(bad,16);
                if(mode==6)BitConverter.GetBytes(UInt64.MaxValue).CopyTo(bad,8);
                bool rejected=false;try{ParsePids(bad,length);}catch(IOException){rejected=true;}ok(rejected);
            }
            ok(Json("a\n\\\"")=="\"a\\u000a\\\\\\\"\"");
            var env=EnvironmentValues(@"D:\runtime",@"D:\evidence\scratch",@"C:\Windows");
            ok(env["SystemDrive"]=="C:");ok(env["windir"]==@"C:\Windows");
            ok(env["TEMP"]==@"D:\evidence\scratch");ok(env["APPDATA"].StartsWith(@"D:\evidence\scratch\"));
            ok(env["ProgramData"]==@"D:\evidence\scratch\program-data");
            ok(!env.ContainsKey("PYTHONPATH") && !env.ContainsKey("SSH_AUTH_SOCK"));
            ok(!env["PATH"].Contains("%") && env.Count==12);
            Console.WriteLine("Diagnostic pure checks passed: "+tests+"; native/VM execution: none");return 0;
        }

        public static int Main(string[] args) {
            try {
                if (args.Length == 1 && args[0] == "--diagnostic-unit-tests") return DiagnosticUnitTests();
                if (args.Length != 6 || args[0] != "--approved-diagnostic-only" ||
                    args[5] != "deadline")
                    throw new ArgumentException("Only pure diagnostic tests or separately approved single deadline diagnosis is supported");
                if(!String.Equals(Path.GetFullPath(args[1]), @"D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3",StringComparison.OrdinalIgnoreCase) ||
                   !String.Equals(Path.GetFullPath(args[2]), @"D:\ReBaseGuard-309\local-vm-feasibility\candidate-v3.sha256",StringComparison.OrdinalIgnoreCase))
                    throw new ArgumentException("fixed approved runtime only");
                return Probe(Path.GetFullPath(args[1]), Path.GetFullPath(args[2]), args[3],
                             Path.GetFullPath(args[4]));
            } catch(Exception e) { Console.Error.WriteLine(e.GetType().Name + ": " + e.Message); return 2; }
        }
    }
}
