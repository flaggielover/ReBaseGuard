# Independent reviewer R2: preserved executions and scripts (verbatim)

Copied from the reviewer's scratch folder after review R2 phase B (2026-09-29 ~23:30Z).
* **Scripts** are stored as inert text (`*.py.txt`), byte-identical to the reviewer's files. They are records, not
  campaign code. Some contain the quarantine-band definition or refusal-probe literals, which are legitimate in the
  reviewer's context, so they are kept outside the code scan instead of being edited.
* **Execution ledgers** (`reviewer_exec_ledger*.jsonl`, 91 lines) are also transcribed into
  `ledger/ZERO_TARGET_LEDGER.jsonl` with `executor = independent-reviewer-R2`. Every target counter is 0 and the
  maximum real-kernel |drift| is 33/32.

| file | sha256 |
|---|---|
| `harness_v1_bf5c87c4.py.txt` | `54840bf4d364f7b4853b542d74f81f9c5cdbd9ad97e5b447a1a2b808e2a8d2be` |
| `ledger_scan.py.txt` | `4dbba86b060a315713aa0886bb9a12629dae2f7aa47f49cd395a93a885fb09fa` |
| `rd2_0_scan.py.txt` | `2caae1a666ab8ccf3f6e044242478a9246757e651fd4bb28f47b49f59aff479e` |
| `rd2_1_cellblocks.py.txt` | `d2abd8d947cf461f48cefa12b43fb522e809d64d4b4fcf3e2ada1e3b2a0044db` |
| `rd2_2_gate.py.txt` | `8820e9254755881dc60570272d1b02c2a3a5be0fc5f380ade6f3d72721b4fee0` |
| `rd2_3_t1power.py.txt` | `9c6aec46f4be24a43cac7c8890175283e6def4d6fb9e161118843762d9c9d8c1` |
| `rd2_b1_integrity.py.txt` | `db15b9ec86d5114b787f6d98d9f72932205fca75e688835c16d1f58a8e43b83e` |
| `rd2_b2_gate.py.txt` | `85a779989cefc6748516c619152da7e97b21a7a53e4fef552c40e0d8c33f153a` |
| `rd2_b3_certmut.out` | `856a061f6639d19864a4490d084db6852e07e2af61713c26fe115439509dbe42` |
| `rd2_b4_e2e.out` | `c7c9d40221f5cdf2a2f999b089b317574dc1a521b9e2892c37844068465e0ddd` |
| `rd2_b4_e2e.py.txt` | `d302529ad7d5e789b0feb12901f9223056a22aed9cf3ab0315a4b35a818640c5` |
| `rd2_b5_verify.out` | `e2abb5cf10780ef75d4dff15819f6c4e8e2d3880ccbfe161ac21e62b0ed9461f` |
| `rd2_b5_verify.py.txt` | `453ecfe1b423e696c74521dbb5ea4ef0037be4baae920b1c190b7267b6dbaed8` |
| `rd2_b5b.out` | `2e00fd6a9317770929b2715edf35c953015bc6479eb1677f0aa4bc4d55929cd8` |
| `rd2_b5b_verify_all.py.txt` | `6361e819a61deb18e4ca433073966edfe2c4ea2db1f492696c36569a2646861d` |
| `rd2_b6_mc.out` | `0a0708c4ce69b0799a5ac14b560b335e7b449f5e39dfbeb30df7113e5082c8cb` |
| `rd2_b6_mc.py.txt` | `04f81d7fa4bf82a38599c60f294699d5afa70c5f240ff497a5372d0ed03b2466` |
| `rd2_b6_mc_all.out` | `b9919c74810b31d1d51dd434b9325f935f14c07763adf8b648c16f2d63702240` |
| `rd2_c0.py.txt` | `fd021a176442d189ff4b1bf5945b9068f9c674580607100d458ed91e68b5c057` |
| `rd2_c1_adapter.py.txt` | `22774418b8a9b89dd643db4bab031835597aa521cf74356fbc23663381caca21` |
| `rd2_c2_selftests.out` | `3a27083274341fc0de691a3869270e83a65db0afb651561218eebca4107627a6` |
| `rd2_c2_selftests.py.txt` | `1bccd44ee26cab9e1152b4ccd2129e096d2480b8ecca44f6758b52a1df59e556` |
| `rd2_c3_battery.out` | `922e43b5738d0a6fee1ddcbc0d5c0f22e1bed506b7ed2aef4dec99254063ede3` |
| `rd2_c3_battery.py.txt` | `97c9d5d06cc5b95c1532034b0cb6b20bf8f27d0349ddd87b57c25268571c6e1c` |
| `rd2_d1_envelope.py.txt` | `6549afc42910a76c2aef44ad80cb8b581b12408bd1fb65f51e739ee2c2c3806f` |
| `rd2_d2_replay.py.txt` | `f2663a0c718ef832f5e9601f726e98e87ae07ec61e92cd8f38c5b8df6c8ff333` |
| `rd2_t.py.txt` | `665b9b8f3e81a6dfc6454e87881e15a428cd9543e17b5ea67f90e1881db241bf` |
| `rd2_t_certmut.out` | `cf2950850f2b7bd9e7054e351cf37ce71218ee049e87582ebcab824c3b4ffd12` |
| `reviewer_exec_ledger.jsonl` | `e9a160fc672d53cb0451de49f5358a839ba209a9400733a3d4429faccef3e5a6` |
| `reviewer_exec_ledger_c2.jsonl` | `d1dc58506498377a86ce5496593847c17e9d75174a1eaa2ccfdee16e623c44f5` |
| `reviewer_exec_ledger_c3.jsonl` | `a51539f691525e281e2cdaa43b90af455112834d88ba2d7fb53d2c2c90229418` |
| `reviewer_exec_ledger_cm.jsonl` | `2631f81ce2ac8fc0210a74ad870a1b0316660bfaa027d1d2b3dfbb5cede85922` |
| `reviewer_exec_ledger_e2e.jsonl` | `577a72883091082f76598be7160d160cedd1e4a8ec2c1217ebe2c459d00c04ac` |
| `reviewer_exec_ledger_mc.jsonl` | `a342a73398f490ae3eea63f1fe2db27c9788c84ff0e68b5cc004ade4c0b3b257` |
| `reviewer_exec_ledger_mc2.jsonl` | `87d22e3458ce16b80963fa9241a6dc36066961e83e90ddcae4352103fe74dd9b` |
| `reviewer_exec_ledger_vf.jsonl` | `041cc6b6959ca0a8d91b9ed75b3a014e4095b9db5a5ad0e29b4bd32474fb19a3` |
| `reviewer_exec_ledger_vf2.jsonl` | `ecfd576ba67cf7ed282a2b9b0d3bca3f8dbb21addfc09b72886b113be8bf3f30` |

Phase C files (rd2_c*, reviewer_exec_ledger_c*) added 2026-09-30 ~00:2xZ; phase D scripts (rd2_d*, harness_v1_bf5c87c4) added ~00:4xZ (read-only runs; no ledger lines needed).
