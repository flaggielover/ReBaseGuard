using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;

// Ordinary compiler/test children only. Never used by the installed anchor or a production query.
public static class P309BuildToolRunnerV10
{
    public sealed class Result
    {
        public int Pid; public int? ExitCode; public bool TimedOut, KillRequested, Exited, Unknown;
        public string KillError; public StreamResult Stdout, Stderr;
    }
    public sealed class StreamResult
    {
        public byte[] Bytes; public long TotalBytes; public bool Complete, Truncated, DecodeFailed;
        public string Error, Text; public int DecodingCodePage = 936; public bool StrictDecode = true;
    }
    private sealed class Drain
    {
        private readonly object gate = new object(); private readonly byte[] captured = new byte[131072]; private int stored;
        private long total; private bool complete; private string error;
        internal void Run(Stream input)
        {
            try
            {
                byte[] b = new byte[4096]; int n;
                while ((n = input.Read(b, 0, b.Length)) != 0) lock (gate) { int take = Math.Min(n, captured.Length - stored); Buffer.BlockCopy(b, 0, captured, stored, take); stored += take; total += n; }
                lock (gate) complete = true;
            }
            catch (Exception e) { lock (gate) error = e.GetType().FullName + ": " + e.Message; }
        }
        internal StreamResult Snapshot()
        {
            StreamResult r; lock (gate) { byte[] b = new byte[stored]; Buffer.BlockCopy(captured, 0, b, 0, stored); r = new StreamResult { Bytes = b, TotalBytes = total, Complete = complete, Truncated = total > stored, Error = error }; }
            try { r.Text = Encoding.GetEncoding(936, EncoderFallback.ExceptionFallback, DecoderFallback.ExceptionFallback).GetString(r.Bytes); if (r.Text.Length > 65536) { r.Text = r.Text.Substring(0, 65536); r.Truncated = true; } }
            catch (Exception e) { r.DecodeFailed = true; r.Error = (r.Error ?? "") + "; strict CP936 decode: " + e.GetType().FullName; }
            return r;
        }
    }
    private static readonly List<Process> RetainedUncertainProcesses = new List<Process>();
    public static Result Run(string executable, string arguments, string workingDirectory, int timeoutMilliseconds)
    {
        if (timeoutMilliseconds < 1 || timeoutMilliseconds > 60000) throw new ArgumentOutOfRangeException("timeoutMilliseconds");
        ProcessStartInfo si = new ProcessStartInfo(executable, arguments); si.UseShellExecute = false; si.CreateNoWindow = true; si.WorkingDirectory = workingDirectory; si.RedirectStandardOutput = true; si.RedirectStandardError = true;
        si.EnvironmentVariables.Clear(); si.EnvironmentVariables["SystemRoot"] = "C:\\Windows"; si.EnvironmentVariables["WINDIR"] = "C:\\Windows"; si.EnvironmentVariables["PATH"] = "C:\\Windows\\System32"; si.EnvironmentVariables["TEMP"] = workingDirectory; si.EnvironmentVariables["TMP"] = workingDirectory;
        Process p = Process.Start(si); Result r = new Result { Pid = p.Id }; Drain stdout = new Drain(), stderr = new Drain();
        Task outTask = Task.Factory.StartNew(delegate { stdout.Run(p.StandardOutput.BaseStream); }); Task errTask = Task.Factory.StartNew(delegate { stderr.Run(p.StandardError.BaseStream); });
        r.Exited = p.WaitForExit(timeoutMilliseconds);
        if (!r.Exited)
        {
            r.TimedOut = true; r.KillRequested = true;
            try { p.Kill(); } catch (Exception e) { r.KillError = e.GetType().FullName + ": " + e.Message; }
            r.Exited = p.WaitForExit(2000);
        }
        if (r.Exited) r.ExitCode = p.ExitCode;
        Task.WaitAll(new Task[] { outTask, errTask }, 2000); r.Stdout = stdout.Snapshot(); r.Stderr = stderr.Snapshot();
        r.Unknown = !r.Exited || !r.Stdout.Complete || !r.Stderr.Complete || r.Stdout.Truncated || r.Stderr.Truncated || r.Stdout.DecodeFailed || r.Stderr.DecodeFailed || r.Stdout.Error != null || r.Stderr.Error != null || r.KillError != null;
        if (r.Exited && r.Stdout.Complete && r.Stderr.Complete) p.Dispose(); else lock (RetainedUncertainProcesses) RetainedUncertainProcesses.Add(p);
        // OS calls (Start/Kill/Read/Wait) are not promised to be hard preemptible. A timeout never means a proven stop.
        return r;
    }
}
