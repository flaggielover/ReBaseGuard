# P309-r2 owner reply form

Fill in one choice per line, using the exact option IDs, and send the completed form as a message.
- With the owner's authorization (AF-3), the message will be recorded **verbatim** in r2's `governance/` as an
  immutable file with its sha256. Nothing is recorded from this blank form.
- A line left as `OPEN` stays undecided. Nothing is inferred from an empty line, a recommendation, or this form's
  layout.
- The recommendations are in `OWNER_DECISION_EXECUTION_PACKET.md` §4. They are not pre-filled here, so that every
  answer is the owner's own.

```text
P309-r2 OWNER DECISIONS — reply to OWNER_DECISION_EXECUTION_PACKET.md
(packet commit: <hardening-branch commit of the packet>; r2 101ef2cb; candidate a119e978)

PHASE A
OD-R2-0(A):   [ CONFIRM | CORRECT: <discrepancy> | OPEN ]
OD-R2-0(B):   [ CONFIRM ALL ROWS | CONFIRM EXCEPT: <row> -> <amendment> | OPEN ]
OD-R2-0(C):   [ ACKNOWLEDGE | ACKNOWLEDGE WITH ADDITIONS (packet §1.3 item 6) | DECLINE | OPEN ]
OD-R2-1:      [ (b) | (a) | (c): <names> | OPEN ]
OD-R2-1b:     [ CONFIRM | NAME OTHERS: <bindings> | OPEN ]
OD-R2-2:      [ RATIFY | OTHER NAMES: <names> | DECLINE EXTENSION | OPEN ]
OD-R2-3:      [ APPROVE AUDIT ONLY | APPROVE | DECLINE | OPEN ]
              dedicated host available: [ NO | YES: <host> | UNKNOWN ]
OD-R2-5:      [ (i) | (ii) with amendment of message 3 §3: <text> | OPEN ]
OD-R2-6(ii):  [ REQUIRE | DO NOT REQUIRE | OPEN ]      (QC10 host re-run immediately before any grant)
OD-R2-6(iii): [ NO HOST AT FREEZE | NAME A HOST AT FREEZE | OPEN ]
SF1 path:     [ SF1-A | SF1-B | OPEN ]                 (SF1 must be resolved before the freeze: formal review C2)

PHASE B
OD-R2-H:      [ H-A | H-B | OPEN ]
              H-A means exactly: fast-forward claude/p5y-k5-cell309-p309-r2 from 101ef2cb to a119e978 under
              formal-review condition C1, with nothing else in the same step. It does NOT authorize the freeze,
              the qualification, any grant, Gamma(309), or any scientific-status change.
F-DRILL-ORDER:[ FD-A | FD-B | OPEN ]                   (FD-A requires H-A)

PHASE C   (answer when the stated evidence exists; may be left OPEN now)
OD-R2-4:      M1 P309 user ............ [ CONSENT | DECLINE | OPEN ]
              M2 volume/quota >= 40 GB  [ CONSENT | DECLINE | OPEN ]
              M3 polkit p309-r2-* units [ CONSENT | DECLINE | OPEN ]
              M4 reboot/upgrade hold .. [ CONSENT WITH CELL-308 OPERATOR FOR WINDOWS: <windows> | DECLINE | OPEN ]
              M5 private CPython 3.11.15[ CONSENT | DECLINE | OPEN ]
              unit limits ............. [ CONSENT: <values or "as in the host configuration"> | DECLINE | OPEN ]
AF-1 (only if the 8a audit finds the cell-308 checkout world-readable):
              [ AMEND MESSAGE 3 §6: <text>, with the cell-308 operator's consent | DO NOT AMEND | NOT TRIGGERED | OPEN ]
AF-2 (only if the qualification host has no IMDS):
              [ COMMISSION REVIEWED PORTABILITY CHANGE | USE AN IMDS HOST | NOT TRIGGERED | OPEN ]
AF-3:         [ AUTHORIZE governance-only filing in r2 (follow-up-5 brief/review/record; this reply verbatim),
                as a separate commit after the fast-forward | DO NOT FILE | OPEN ]
SF1-A only:   incorporate the reviewed SF1-A delta into r2 when its review accepts it:
              [ AUTHORIZE (fast-forward, nothing else in that step) | OPEN ]

PHASE D   (recommended to stay OPEN until prerequisites P-1 ... P-11 of the packet §1.4 hold)
OD-R2-0(D):   [ OPEN | DECLINE |
                AUTHORIZE — "<the R2_PACKET OD-R2-0(D) text verbatim>" — package: r2 at <exact commit> ]

PHASE E
OD-R2-6(i):   [ DEFER | (a) qualification host | (b) dedicated host: <host> | (c) shared worker + §C amendment ]
AF-4 grant:   not answerable until a passed, reviewed qualification exists.
AF-5 r3:      only if r2's qualification fails or is interrupted.

ADDITIONAL NOTES / CONDITIONS FROM THE OWNER (free text):
<...>

Signed / date (UTC):
```

**Consistency rules** (an answer set that breaks one is recorded with that line marked **INCONSISTENT** and returned to
the owner, never silently resolved):
- `F-DRILL-ORDER: FD-A` requires `OD-R2-H: H-A`.
- `OD-R2-6(iii): NAME A HOST AT FREEZE` requires an `OD-R2-6(i)` host answer (option (a), (b) or (c)).
- `OD-R2-0(D): AUTHORIZE` requires `OD-R2-H: H-A`, and `OD-R2-3` / `OD-R2-4` answered with consent. It is not
  admissible before prerequisites P-1 … P-11 hold.
- `SF1-A only: AUTHORIZE` requires `SF1 path: SF1-A`.
- `OD-R2-5: (ii)` requires the amendment text.
