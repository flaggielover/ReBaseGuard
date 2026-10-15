// Read-only capability probe. Never creates a partition, VM, service or trace.
using System;
using System.Runtime.InteropServices;
internal static class WHPReadOnlyProbe {
    [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
    [DllImport("WinHvPlatform.dll", ExactSpelling=true)]
    private static extern int WHvGetCapability(uint code, out ulong value, uint capacity, out uint written);
    public static int Main() {
        try {
            ulong value; uint written;
            int hr = WHvGetCapability(0, out value, 8, out written);
            bool usable = hr == 0 && written == 4 && value == 1;
            Console.WriteLine("{\"schema\":\"P309_WHP_READONLY_CAPABILITY/1\",\"utc\":\"" +
                DateTime.UtcNow.ToString("o") + "\",\"hresult_hex\":\"0x" + hr.ToString("X8") +
                "\",\"written_bytes\":" + written + ",\"raw_value\":" + value +
                ",\"hypervisor_api_present\":" + (usable ? "true" : "false") +
                ",\"partition_created\":false,\"admission\":\"BLOCKED\"}");
            return hr == 0 && written == 4 ? 0 : 2;
        } catch (Exception e) {
            Console.WriteLine("{\"schema\":\"P309_WHP_READONLY_CAPABILITY/1\",\"status\":\"UNKNOWN\",\"error_type\":\"" +
                e.GetType().Name + "\",\"partition_created\":false,\"admission\":\"BLOCKED\"}");
            return 2;
        }
    }
}
