# P309 saved ExtendedData v8 — built, actual scan not run

This package builds a Windows x64 saved-ETL aggregate scanner. The final ordinary build is `build-ordinary-04`. Compilation with `/W4 /WX`, explicit `/NODEFAULTLIB` linking, PE inspection, and all **21 synthetic memory checks passed**. No actual ETL bytes were read and no OpenTrace call was made in this development task. I1–I7 are OPEN; admission is BLOCKED.

The scanner reports only aggregate counts and structural evidence. It emits no captured PID, TID, path, command line, scalar Process Start Key, key digest, SID, stack, or payload. The separate compiler records contain build paths and the build runner's own child-process metadata; those are not ETL-derived output.

## Files and current bindings

- `SavedExtendedData.cpp`: implementation and memory checks; SHA256 `e493c3dc93ff99c948ac344bd8326129ef5b9648cdb11078398a96fb9e7c81cf`.
- `build-ordinary-04/SavedExtendedData.exe`: final executable; SHA256 `a9a8f84d64051d11743f9c7d4a0cdbb56b21eb6b599026d50cd7ade91f3e903d`.
- `Build-Only.ps1` and `BuildToolRunner.cs`: ordinary build, PE inspection, and memory checks only. The script contains no actual-scan dispatch.
- `build-ordinary-04/BUILD_RESULT.json`: source / executable / tools / libraries / transitive SDK header hashes, hash commands, and exact native command arguments.
- `build-ordinary-04/memory-checks.stdout.txt`: 21 PASS lines and the memory-only result.
- `DESIGN.md`: scope, implementation choices, coverage, and evidence boundaries.
- `SOURCE_BINDINGS.json`: approved fixed input binding, reference-source bindings, and final artifact hashes.

The compiler is MSVC `14.44.35207` x64 `cl.exe`, SHA256 `6aa39ae173cb8563d796359930b332a08b2fdc1745b70e5a4caa48a9779fdd07`. The SDK is `10.0.26100.0`. The final manifest records 221 transitive headers and eight explicitly named link libraries, plus compiler and other tool files. Source snapshots, tool files, and explicit libraries are held read-only during their use. Transitive headers were discovered by `/showIncludes`, then hashed and held after compilation; this is not a claim of an immutable SDK snapshot before the build.

The retained `build-ordinary-01` failure was a build-inventory parser failure: the compiler succeeded, but its actual `/showIncludes` prefix was Chinese despite requested VSLANG 1033. The parser was corrected to accept the observed strict CP936 Chinese prefix and English. `ordinary-02` passed; `ordinary-03` added explicit input close status and output directory pins; `ordinary-04` added a top-level initialization-failure refusal. Earlier records remain unchanged.

## Ordinary build command

From the workspace root, with a fresh ordinary build name:

```powershell
& '.\outputs\p309-saved-extended-v8-staging\Build-Only.ps1' -RunName 'ordinary-04'
```

That recorded name now exists and must not be rerun. The final manifest records the actual compile, link, dumpbin, and `--self-test` arguments. The compiler was used via its absolute path; no Visual Studio setup script, service, elevation, capture, VM, WSL, or installer was invoked. Child output is drained into bounded one-MiB raw buffers per stream with strict CP936 decoding. Timeout, truncation, incomplete drainage, decoding failure, or uncertain owned-child termination makes the ordinary build fail or UNKNOWN.

## Future saved-file interface — not executed

```text
SavedExtendedData.exe --scan-saved <fresh-alphanumeric-hyphen-attempt-name>
```

The source fixes this input binding:

```text
D:\ReBaseGuard-309\records\p309-i2-root-v3-attempt-20261016-01\capture\capture.etl
bytes: 308346880
SHA256: 3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870
```

Those values were supplied for future verification. This task did not open, hash, or decode that ETL. The next action is independent source/binary/entry review and a fixed separately authorized saved-file call. A future caller must pin the reviewed executable and sources for dispatch; the scanner does not bootstrap trust in its own loaded binary. There is no arbitrary input path or real-time mode.

The future command creates `scan-<attempt-name>` under the executable directory. An existing attempt is refused. No file is replaced, no failed attempt is automatically repeated, and no old attempt is resumed. All input ancestors and the held leaf remain pinned while trace processing and the post-read hash run.

## How to interpret a future result

Treat a scan as complete only if all of these are true:

1. The native process exits zero and its final stdout record says `COMPLETE`, including successful completion-file I/O and output-directory close.
2. `completion.json` parses, has the expected schema/version, and has both `complete` and `scan_complete` true.
3. The actual aggregate bytes match the completion's SHA256 and length. This is a report-file digest, never a captured key digest.
4. `aggregate.json` reports `status.scan_complete=true`, fixed pre/post input hashes, stable held identity, a supported raw QPC clock, successful ProcessTrace/CloseTrace and input closes, conservation, and descriptor coverage.

Missing or malformed completion, nonzero exit, a partial file, write/flush/close failure, input drift, incompatible clock, callback failure, budget exhaustion, or an inaccessible descriptor array means PARTIAL/UNKNOWN. `STARTED.txt` alone is never success. Flushes are checked Windows file flush requests; the package claims no general directory flush or power-loss guarantee.

`psk_candidate` means one structurally valid eight-byte readable type-13 descriptor. It does not mean that any payload process has been identified. Other categories distinguish absence, duplicate keys, malformed structure, and uninspectable arrays. Nonzero reserved fields are conservatively classified as structurally unacceptable; this is not a claim that a provider was malicious. Other extended payloads are not decoded or dereferenced. A malformed/null/wrong-size PSK can still be counted during a full descriptor scan while its identity evidence remains UNKNOWN.

Loss output includes the open-file header and maximum buffer-callback header counters, plus documented Lost_Event provider opcodes 32/33/34. The callback `EVENT_TRACE_LOGFILE.EventsLost` field is explicitly marked unused. These observations do not certify a loss-free capture, and equal-QPC delivery does not establish event causality. No CPU attribution, thread birth/death reconstruction, saved-partition change, formal grant, or admission decision is produced.

## Official API basis

- [EVENT_RECORD](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/ns-evntcons-event_record) defines ExtendedDataCount and ExtendedData.
- [EVENT_HEADER_EXTENDED_DATA_ITEM](https://learn.microsoft.com/en-us/windows/win32/api/evntcons/ns-evntcons-event_header_extended_data_item) defines descriptor size, pointer, and Process Start Key's 64-bit scalar form.
- [ENABLE_TRACE_PARAMETERS](https://learn.microsoft.com/windows/win32/api/evntrace/ns-evntrace-enable_trace_parameters) documents the capture enable property; no enablement is inferred from historical payloads.
- [EVENT_TRACE_LOGFILEW](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/ns-evntrace-event_trace_logfilew) documents RAW_TIMESTAMP, callbacks, and the unused EventsLost field.
- [ProcessTrace](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-processtrace) documents completion/error status and ordering limitations.
- [Lost_Event](https://learn.microsoft.com/en-us/windows/win32/etw/lost-event) and [RT_LostEvent](https://learn.microsoft.com/en-us/windows/win32/etw/rt-lostevent) define the loss notification provider and opcodes. Their payloads are not interpreted as counts.
