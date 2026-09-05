# Repair2 provenance evidence

NON-RESULT-BEARING. Repair2 changes no science: it binds each emitted
certificate to the code that produced it and to the actual dependency
certificates it consumed.

## Producer implementation identity

```text
producer implementation hash  f703921b045f39092d9bdf67d02927f70961dd344dc3be50d17aab0b23df16bd
backend contract hash         8abad284d1eb642e0e682de3eb118f1f901993ae16c939b29ab95c339b2ebf25
reviewed parent hash          44f5417bdbba87fd34ff1d161fa307b3236bf7f55ea9b27cb12ddd5681938155
distinct from parent          True
certifying inputs hashed      38
```

Repair1 stamped the reviewed parent hash, which hashes thirteen files
in the reviewed namespace and none of Repair1's own
certificate-producing modules. The Repair2 manifest covers Repair2's
modules, the Repair1 modules actually executed, the reviewed modules
actually executed, the frozen algebra and config, the certified backend
contract, and the fixed generation parameters (including the pinned
python-flint version).

## Certificate chains

| cell | bits | scope | obligations | verified | leaf maps empty |
|---:|---:|---|---:|---|---|
| 221 | 256 | full | 28 | True | True |
| 221 | 256 | m1_only | 0 | False | n/a |

The m=1 SCOPED run issues **no certificate**: it never computes
the frozen dependency bundle, so it discharges no obligation.
Refusing to certify work that was not done is the same class of
protection this repair adds.

### Cell 221 leaf obligations

```text
CUSUM|221|object|h_1   source_certificate_hashes = {}
CUSUM|221|object|S_0   source_certificate_hashes = {}
```

### Sample non-leaf binding

```text
CUSUM|221|object|dF_2
  certificate hash  aa8fcee736d70c6ab54e3b1614c7ab7fbc3ff1d70cd908657112822844369d0b
  consumes CUSUM|221|dependency_bundle|orders_0_1
           686f674f58a8b006b222146a755bee37b232b15ecb000f96dbbf7cbaacde60b8
  consumes CUSUM|221|object|F_2
           c1c812972443a8ea319194336fdf20f834deb10bf9588030baed3b31a8f01a2c
```

## Scientific regression

Repair2 changes no certified value. Against Repair1 on cell 221:

```text
mag(D_interval) delta = 0    M_R2 delta = 0    B_cover delta = 0
all statuses PASS -> PASS    R_intervals identical
S0 remainder charged exactly once (representation A) retained
h_2:0 = 1.831353e-06   S_1:0 = 2.764060e-06
```
