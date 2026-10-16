using System;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Threading.Tasks;

// This helper is for the ordinary compiler, linker, PE inspection, and memory
// tests. It has no ETL dispatch capability of its own.
public static class P309V8BuildToolRunner
{
    public sealed class StreamResult
    {
        public byte[] Bytes; public long TotalBytes; public bool Complete, Truncated, DecodeFailed;
        public string Text, Error;
    }
    public sealed class Result
    {
        public int Pid; public int? ExitCode; public bool TimedOut, KillRequested, Exited, Unknown;
        public string KillError; public StreamResult Stdout, Stderr;
    }
    private sealed class Drain
    {
        private readonly object gate = new object(); private readonly byte[] captured = new byte[1048576];
        private int stored; private long total; private bool complete; private string error;
        internal void Read(Stream stream)
        {
            try
            {
                byte[] buffer = new byte[4096]; int n;
                while ((n = stream.Read(buffer, 0, buffer.Length)) != 0)
                    lock (gate) { int take = Math.Min(n, captured.Length - stored); Buffer.BlockCopy(buffer, 0, captured, stored, take); stored += take; total += n; }
                lock (gate) complete = true;
            }
            catch (Exception e) { lock (gate) error = e.GetType().FullName; }
        }
        internal StreamResult Snapshot()
        {
            StreamResult result;
            lock (gate) { byte[] bytes = new byte[stored]; Buffer.BlockCopy(captured, 0, bytes, 0, stored); result = new StreamResult { Bytes = bytes, TotalBytes = total, Complete = complete, Truncated = total > stored, Error = error }; }
            try { result.Text = Encoding.GetEncoding(936, EncoderFallback.ExceptionFallback, DecoderFallback.ExceptionFallback).GetString(result.Bytes); }
            catch (Exception e) { result.DecodeFailed = true; result.Error = e.GetType().FullName; }
            return result;
        }
    }
    private static readonly System.Collections.Generic.List<Process> uncertain = new System.Collections.Generic.List<Process>();
    public static Result Run(string executable, string arguments, string directory, string toolDirectory, string sdkBin)
    {
        ProcessStartInfo si = new ProcessStartInfo(executable, arguments); si.UseShellExecute = false; si.CreateNoWindow = true; si.WorkingDirectory = directory; si.RedirectStandardOutput = true; si.RedirectStandardError = true;
        si.EnvironmentVariables.Clear(); si.EnvironmentVariables["SystemRoot"] = "C:\\Windows"; si.EnvironmentVariables["WINDIR"] = "C:\\Windows";
        si.EnvironmentVariables["PATH"] = toolDirectory + ";" + sdkBin + ";C:\\Windows\\System32"; si.EnvironmentVariables["TEMP"] = directory; si.EnvironmentVariables["TMP"] = directory; si.EnvironmentVariables["VSLANG"] = "1033";
        Process process = Process.Start(si); Result result = new Result { Pid = process.Id }; Drain stdout = new Drain(), stderr = new Drain();
        Task first = Task.Factory.StartNew(delegate { stdout.Read(process.StandardOutput.BaseStream); }); Task second = Task.Factory.StartNew(delegate { stderr.Read(process.StandardError.BaseStream); });
        try
        {
            result.Exited = process.WaitForExit(60000);
            if (!result.Exited)
            {
                result.TimedOut = true; result.KillRequested = true;
                try { process.Kill(); } catch (Exception e) { result.KillError = e.GetType().FullName; }
                result.Exited = process.WaitForExit(2000);
            }
            if (result.Exited) result.ExitCode = process.ExitCode;
            Task.WaitAll(new Task[] { first, second }, 2000); result.Stdout = stdout.Snapshot(); result.Stderr = stderr.Snapshot();
            result.Unknown = !result.Exited || !result.Stdout.Complete || !result.Stderr.Complete || result.Stdout.Truncated || result.Stderr.Truncated || result.Stdout.DecodeFailed || result.Stderr.DecodeFailed || result.Stdout.Error != null || result.Stderr.Error != null || result.KillError != null;
            return result;
        }
        finally
        {
            // A failed/timeout wait is never proof of exit; retain this exact
            // owned Process object rather than reopening an unverified PID.
            if (result.Exited && result.Stdout != null && result.Stdout.Complete && result.Stderr.Complete) process.Dispose();
            else lock (uncertain) uncertain.Add(process);
        }
    }
}
