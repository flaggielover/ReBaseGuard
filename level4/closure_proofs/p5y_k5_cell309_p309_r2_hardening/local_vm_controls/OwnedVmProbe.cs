// Preparation/feasibility probe ONLY. No P309 launcher or grant interface.
// --unit-tests performs no native calls. Real probes require separate approval.
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
            uint flags, IntPtr environment, string directory, ref Startup startup, out ProcessInfo info);
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
    }

    public static class OwnedVmProbe {
        // No caller-supplied QEMU switches, disks, network, commands, PID or job name.
        // Paused 128 MiB hardware probe; NOT the formal 8 GB capacity acceptance.
        const string FixedArgs = " -no-user-config -nodefaults -machine q35 -accel whpx,ssd=on" +
            " -smp 4 -m 128 -S -display none -serial none -monitor none -nic none";
        static int stopRequested, terminateSucceeded, nativeStopError;

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

        static IntPtr EnvironmentBlock(string root, string scratch) {
            string windows = Environment.GetFolderPath(Environment.SpecialFolder.Windows);
            SortedDictionary<string, string> env = new SortedDictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            env.Add("PATH", Path.Combine(root, "ucrt64", "bin") + ";" + Path.Combine(windows, "System32"));
            env.Add("SystemRoot", windows);
            env.Add("TEMP", scratch); env.Add("TMP", scratch);
            env.Add("QEMU_MODULE_DIR", Path.Combine(root, "ucrt64", "lib", "qemu"));
            env.Add("QEMU_DATA_DIR", Path.Combine(root, "ucrt64", "share", "qemu"));
            StringBuilder block = new StringBuilder();
            foreach(KeyValuePair<string, string> item in env) block.Append(item.Key).Append('=').Append(item.Value).Append('\0');
            block.Append('\0'); return Marshal.StringToHGlobalUni(block.ToString());
        }

        static uint Active(IntPtr job) {
            Native.Accounting data;
            Check(Native.QueryInformationJobObject(job, 1, out data,
                  (uint)Marshal.SizeOf(typeof(Native.Accounting)), IntPtr.Zero), "query job accounting");
            return data.activeProcesses;
        }
        static void Stop(IntPtr job) {
            // Native stop precedes every diagnostic/file operation. No shared
            // session lock, signer, logger, endpoint or guest response involved.
            if (Interlocked.Exchange(ref stopRequested, 1) == 0) {
                if (Native.TerminateJobObject(job, 0x309)) Interlocked.Exchange(ref terminateSucceeded, 1);
                else Interlocked.Exchange(ref nativeStopError, Marshal.GetLastWin32Error());
            }
        }

        static int Probe(string root, string hashList, string expectedListHash, string output, bool abrupt) {
            if (Environment.Is64BitProcess == false) throw new InvalidOperationException("x64 required");
            if (File.Exists(output)) throw new IOException("evidence exists; no overwrite");
            // New evidence file is opened before VM creation. No app policies changed.
            using (FileStream record = new FileStream(output, FileMode.CreateNew, FileAccess.Write, FileShare.Read))
            using (StreamWriter writer = new StreamWriter(record, new UTF8Encoding(false))) {
                writer.AutoFlush = true;
                List<FileStream> held = LockRuntime(root, hashList, expectedListHash);
                IntPtr job = IntPtr.Zero; Native.ProcessInfo process = new Native.ProcessInfo();
                Thread watchdog = null; bool assigned = false; IntPtr environment = IntPtr.Zero;
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
                    string exe = Path.GetFullPath(Path.Combine(root, "ucrt64", "bin", "qemu-system-x86_64.exe"));
                    Native.Startup startup = new Native.Startup(); startup.cb = Marshal.SizeOf(typeof(Native.Startup));
                    environment = EnvironmentBlock(root, Path.GetDirectoryName(Path.GetFullPath(output)));
                    string data = Path.Combine(root, "ucrt64", "share", "qemu");
                    // CREATE_SUSPENDED | CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT;
                    // inheritHandles=false, minimal environment, no user plugin/data search.
                    Check(Native.CreateProcess(exe, new StringBuilder(Quote(exe) + FixedArgs + " -L " + Quote(data)),
                          IntPtr.Zero, IntPtr.Zero, false, 0x08000404, environment,
                          Path.GetDirectoryName(exe), ref startup, out process), "create fixed QEMU suspended");
                    Check(Native.AssignProcessToJobObject(job, process.process), "assign job before resume");
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
                    if (Native.ResumeThread(process.thread) == UInt32.MaxValue) throw new Win32Exception();
                    writer.WriteLine("{\"event\":\"owned_start\",\"pid\":" + process.pid +
                        ",\"creation_filetime\":" + created + ",\"handle_inheritance\":false," +
                        "\"job_assigned_before_resume\":true,\"admission\":\"BLOCKED\"}");
                    record.Flush(true);
                    uint early = Native.WaitForSingleObject(process.process, 5000);
                    if (early != 258) {
                        uint earlyExit; Check(Native.GetExitCodeProcess(process.process, out earlyExit), "early exit code");
                        throw new InvalidOperationException("QEMU early exit/wait: " + early + "; exit code: " + earlyExit);
                    }
                    writer.WriteLine("{\"event\":\"alive_at_5s\",\"active_job_processes\":" + Active(job) + "}");
                    record.Flush(true);
                    if (abrupt) {
                        writer.WriteLine("{\"event\":\"about_to_exit_guard\",\"cleanup_proven\":false}");
                        record.Flush(true);
                        // Approved fault injection only: kernel closes the unnamed
                        // job's last handle. An external observer must prove exit.
                        Native.ExitProcess(86);
                    }
                    uint wait = Native.WaitForSingleObject(process.process, 18000);
                    Stop(job);
                    if (watchdog != null && !watchdog.Join(2000)) throw new IOException("watchdog did not finish");
                    uint finalWait = Native.WaitForSingleObject(process.process, 5000);
                    uint active = Active(job); uint exitCode;
                    Check(Native.GetExitCodeProcess(process.process, out exitCode), "exit code");
                    bool cleanup = finalWait == 0 && active == 0 && terminateSucceeded == 1;
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
                    foreach(FileStream f in held) f.Dispose();
                }
            }
        }
        static int UnitTests() {
            int tests = 0;
            Action<bool> ok = delegate(bool value) { tests++; if (!value) throw new Exception("unit " + tests); };
            ok(Quote("x") == "\"x\"");
            ok(Quote("a b") == "\"a b\"");
            ok(Quote("a\"b") == "\"a\\\"b\"");
            ok(Quote("a\\") == "\"a\\\\\"");
            ok(Quote("") == "\"\"");
            foreach(string bad in new string[] { "a\0b", "a\nb", "a\rb" }) {
                bool rejected = false; try { Quote(bad); } catch(ArgumentException) { rejected = true; } ok(rejected);
            }
            ok(!FixedArgs.Contains("tcg")); ok(!FixedArgs.Contains("hostfwd"));
            ok(!FixedArgs.Contains("-drive")); ok(FixedArgs.Contains("-accel whpx,ssd=on"));
            Console.WriteLine("Pure unit checks passed: " + tests + "; native/VM execution: none"); return 0;
        }
        public static int Main(string[] args) {
            try {
                if (args.Length == 1 && args[0] == "--unit-tests") return UnitTests();
                if (args.Length != 6 || args[0] != "--approved-feasibility-only" ||
                    (args[5] != "deadline" && args[5] != "guard-exit"))
                    throw new ArgumentException("Only --unit-tests or separately approved fixed feasibility probe is supported");
                return Probe(Path.GetFullPath(args[1]), Path.GetFullPath(args[2]), args[3],
                             Path.GetFullPath(args[4]), args[5] == "guard-exit");
            } catch(Exception e) { Console.Error.WriteLine(e.GetType().Name + ": " + e.Message); return 2; }
        }
    }
}
