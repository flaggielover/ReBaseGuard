/* Ten codec/digest checks only. Does not call ProductionEntry, admin(),
 * CreateProcess, any trace/Job/fixture, directory creation or elevation. */
#define Entry ProductionEntry
#include "NativeEntry.c"
#undef Entry
void WINAPI TestEntry(void) {
    const char* inputs[]={"","f","fo","foo","foob","fooba","foobar"};
    const wchar_t* expected[]={L"",L"Zg==",L"Zm8=",L"Zm9v",L"Zm9vYg==",L"Zm9vYmE=",L"Zm9vYmFy"};
    char digest[65];int i;BYTE wideA[]={65,0};
    for(i=0;i<7;i++)if(lstrcmpW(base64((const BYTE*)inputs[i],(DWORD)length(inputs[i])),expected[i]))ExitProcess(10+i);
    if(lstrcmpW(base64(wideA,2),L"QQA="))ExitProcess(17);
    if(!hash((const BYTE*)"",0,digest)||!equal(digest,"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",64))ExitProcess(18);
    if(!hash((const BYTE*)"abc",3,digest)||!equal(digest,"ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",64))ExitProcess(19);
    ExitProcess(0);
}
