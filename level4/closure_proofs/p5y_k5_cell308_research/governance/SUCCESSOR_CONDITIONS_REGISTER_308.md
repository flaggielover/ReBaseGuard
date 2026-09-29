# Cell-308 successor MB-S: register of binding conditions (coordinator; live; status as of 2026-09-29 ~19:35Z)

The authoritative texts are the cited documents. This register tracks **where** each condition binds and its
**status**. New cell-308 target evaluations: 0.

**Sources:**

| document | commits |
|---|---|
| governance | determination `e5871aa6`; A1 `ce145e51`; E1 `a7c969e8`; GOVERNANCE_ACCEPTED `00a432df` |
| route | audit `bddd85f8`; A1 `ce145e51`; E1 `a7c969e8`; E2 (this commit); ROUTE_ACCEPTED `87d0b2b9` |
| incident re-rating | reviewINC2, INCIDENT_AUDIT_ACCEPTED `b7e62dec` |
| architecture | `8a4a02b4`; A1 `87d0b2b9` |

| id | condition (short) | binds at | status |
|---|---|---|---|
| S1 | user ruling before any grant (count 2; notwithstanding brief §21 and mitigation 5; U1–U8; finality; caps; trade) | grant | **open (USER_RULING_REQUIRED)** |
| S2 | new namespace; MB r1 never modified; cited as consumed / interrupted / INDETERMINATE / not negative | always | met so far (`p5y_k5_cell308_mbs_r1` on `p5y-k5-cell308-mbs-r1`) |
| S3, S13, MBS-1, MBS-2 | no MB r1 run observation in any successor decision or brief; holders excluded from successor roles; caps from decoys only | always | E1″ + errata 1–2 recorded; builder restricted since about 18:39Z (its disclosure is pending in BUILD_REPORT) |
| S4, S11, RC1, MBS-9(i) | byte-identical science; AST source equality including module-level names; guard constants only | build, qualification | builder instructed; **checked at qualification** |
| S5, S12 | liabilities carried; risk re-rated | freeze | **met**: MEDIUM–HIGH upper end (`b7e62dec`) |
| S6, S17, RC6, MBS-3, MBS-4 | detached launch; durable persistence; checkpoints + mandatory resume; memory watchdog; exclusivity; no in-run observation; checkpoint quarantine | build, qualification, run | in build |
| S7 | own marker; own INDETERMINATE; further successors need a further process | protocol | in the protocol draft |
| S8, MBS-11 | fresh independent reviews; briefs committed before use | always | met so far (briefs 21–36 committed) |
| S9 | quarantine; no Γ308 before the grant | always | met (0) |
| S10 | cell 309 isolation | always | met |
| S14 | MB r1 §10 steps 6–8 accepted first | freeze | **met** (`a40211cc`, `9ad632c9`, `e451e634`) |
| S15 | successor preflight asserts MB r1's recorded state; named-exception marker | build, qualification | in build |
| S16 | freeze gates: (a) governance delta accepted; (b) route conditions met; (c) user decision covering the freeze; (d) S14 | freeze | (a) **met**; (b) as facts at qualification; (c) **open (USER DECISION REQUIRED)**; (d) **met** |
| RC2, DR2, MBS-9(iv) | platform pin at execute and every resume; research pins re-hashed; MBR1_REPRO exact; no-update window; auto-update refusal | build, qualification, run | builder instructed; **checked at qualification** |
| RC3 | MB-S only with accepted governance; C9 / E7 / second consumption cited | freeze | met |
| MBS-5 | deviations are an INCIDENT + INDETERMINATE (T4); later 308 routes start at HIGH | protocol | to be frozen |
| MBS-6 | finality of an MB-S INDETERMINATE decided before the freeze (recommended: final) | freeze | **open (user)** |
| MBS-7 | the C11R-I2 / COR-T trade decided before the freeze | freeze | **open (user)** |
| MBS-8 | caps: exactly two options, chosen mechanically; per-attempt EVAL_CAP reviewed | freeze | **open (user choice; non-holder draft)** |
| MBS-10 | S1 brief content; no outcome expectation; scanner plus non-holder check | before the freeze and grant | to be prepared |
| MBS-12 | C2, C7(a), C7(b), C8, C9 carried; "no selection on the value"; L5–L7 in the register | build, qualification | E2 done; the rest in build and qualification |
| MBS-13 | grant contents (the review, triggers, S1 verbatim, C1–C9, S11–S17, no-trigger statement, launch conditions) | grant | future |
| MBS-14 | adjudication contents (consumed twice, value computed at most once, resume history, T3 audit, closure-only, E8 extended) | adjudication | future |

**Triggers T1–T6** (escalation to HIGH): none has fired, as of this register.
