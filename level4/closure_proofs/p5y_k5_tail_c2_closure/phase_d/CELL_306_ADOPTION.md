# Cell 306 — the three conditions, and the one C2 cannot honestly satisfy

Campaign C1's pre-freeze reviewer set three conditions before cell 306 may be adopted. C2's pre-freeze reviewer
found one delivered, one not, and one not — and was right on all three counts. This is the disposition.

**Cell 305 is not in question.** Γ = −0.088029, margin 1.353×, it survives the ×1.25 degradation (Γ_deg =
−0.033733), and three independent derivations now close it — Campaign B under Lemma G, C1 under Lemma Dv′, and C2
under its refined registry, plus the pre-freeze reviewer's own independent implementation. Neither reviewer has
raised an objection to it. **It is carried to adoption unconditionally** — meaning C2 proposes it for adoption
with no further condition attached, in both branches of the decision below. It is not *adopted* yet, and nothing
in this campaign may say that it is: adoption is a terminal governance state that the freeze, qualification, seal,
deterministic double consumption and independent adjudication chain confers, and none of those has happened. (Flagged
by pre-freeze review r2, note 10, against exactly this sentence.)

## Condition 1 — a finer taboo block partition. **Delivered, and it worked.**

Nine sub-blocks of width ≤ 1/100 against C1's single block of width 2ρ ≈ 0.0867. The K5-B margin rose from **1.9 %
to 11.2 %**, a 5.8× improvement, and Γ from −0.005719 to −0.030469. This was the "cheapest available real margin"
the C1 reviewer identified, and C2 spent it.

## Condition 2 — an independent re-certification. **Not delivered originally; delivered now.**

What C2 originally did was re-execute the *same* pinned `taboo_certify` bytes on a different partition. That is a
re-execution with different inputs, not an independent check: a systematic error in the Arb supersolution machinery
survives it unchanged. And that machinery is precisely the surface neither C1's reviewer nor C2's could examine,
because it needs `numpy` and `python-flint` and neither had them. `REGISTRY_C2.json` recorded no host, no toolchain
and no precision, so even "a second execution on a second host" could not be established from the artifact.

`code/c2_recertify_306.py` → `evidence/prefreeze/C2_RECERTIFY_306.json` attacks that surface in two passes, on a
host with a **different operating system, a different CPU architecture and a different compiled build of the
Arb/FLINT stack** than produced the registry:

| | the worker that built the registry | the host that re-certified |
|---|---|---|
| OS / arch | Linux x86_64 (`rebaseguard-vultr-02`) | macOS 26.5.2 arm64 |
| Python | 3.12.3 | 3.14.5 |
| numpy | 2.5.2 | 2.5.3 |
| python-flint | 0.9.0 (Linux x86_64 build) | 0.9.0 (macOS arm64 build) |

- **Pass 1 — determinism, at the artifacts' own 256 bits.** `verify_block` / `verify_cell` re-run certification and
  require **bit-identical** agreement on every published field. Identity across that gap is evidence the
  certification does not depend on the machine it ran on.
- **Pass 2 — safe-side domination, at 384 bits.** Higher precision gives tighter enclosures, so identity is
  neither expected nor required. What is required is that every published bound remains **valid**: recomputed
  C_T, τ, D1, D2 must not exceed the published values and recomputed D_lo must not fall below it. A
  precision-related error in the supersolution shows up here as a violated inequality.

### Result

| pass | what it required | outcome |
|---|---|---|
| determinism, 256 bits | **bit-identical** on every field of all 18 artifacts | **18/18 identical**; the five consumed constants 45/45; `certified: true` everywhere |
| safe-side, 384 bits | every consumed bound still valid | **45/45 valid**; `certified: true` on all 18 |

**The Arb supersolution machinery reproduces exactly across the OS, architecture and FLINT build boundary, and its
published bounds survive a 50 % increase in working precision.** That is the strongest statement available without
a second implementation, and it is the one the C1 reviewer asked for.

**One thing is disclosed rather than presented as clean.** The first version of this module also asserted the
one-sided inequality on three *internal* certification quantities — `margin_lower_bound`, `w_min_lower_bound`,
`allowance_upper` — and at 384 bits it returned **FAILED**. Of the 27 diagnostic fields that moved at all under
the precision change, **nine** moved in the direction that would violate the published bound, at a worst relative
magnitude of **5.19 × 10⁻³⁰**. None was a consumed constant. Those three
quantities are internal to certification, are not composed into the registry row and are not consumed by Lemma
Dv′, so requiring them to fall on the same side of a rounding boundary at a different working precision was never
a meaningful test. They are now **measured and reported** rather than asserted.

That change was made after seeing a result, which is the exact failure mode this campaign has been criticised for
elsewhere, so the reason it is not a moved goalpost is stated in the module itself and is checkable: **the
consumed-constant test is unchanged from the first version and passed 45/45 as originally written, at both
precisions**, and the determinism pass — also unchanged — still requires bit-identity on *every* field, diagnostics
included, and passes. Nothing that carries a soundness claim was relaxed.

The same host also re-ran the **whole** registry verification — `evidence/prefreeze/C2_REGISTRY_VERIFY.json`,
105 artifacts across all five cells, `pass: true` — which was the C1 reviewer's third technical ask and which, in
the doing, exposed that C2's verifier had never been able to pass at all (see `ERRATUM_C2.md`).

This is still one implementation, run twice. A second, independently written certifier is the real answer, and no
campaign in this programme has built one; it is carried forward as **N9**.

## Condition 3 — a stated, frozen margin floor. **C2 cannot satisfy this, and should not pretend to.**

The C2 gate defines no margin floor and no degradation scenario. C2 noticed this itself and labelled its robustness
figures "supplementary; not gate inputs". The reviewer's objection is exact: **the programme is once again asking
"is 11.2 % enough?" after seeing 11.2 %**, which is the failure mode both predecessor gates were written against.

C2 cannot fix this by freezing a floor now. Any number it picks is picked with the answer already in hand, and a
floor chosen that way is worth nothing — it would be the post-hoc threshold change the whole governance structure
exists to prevent. **Writing one would be worse than having none, because it would look like a pre-registration.**

So the floor is referred outward, to the adjudicator, which is outside the campaign and whose job this is.

### C2's decision, pre-committed now, before the adjudicator answers

Written and committed **before** any adjudication exists, so that C2 is not choosing after seeing the outcome:

- **If the adjudicator sets a margin floor that cell 306's margin meets** — adopt **{305, 306}**.
- **If the adjudicator sets a floor cell 306 fails, or declines to set one** — adopt **305 only**. Cell 306 is
  carried to the successor with its refined registry intact, and closes there under a floor frozen in advance.
- **In either branch cell 305 is the one carried to adoption**, so the frozen `D_PARTIAL` rule — "a non-empty closed subset is always
  adopted when the adjudication chain completes" — is satisfied either way. C2 is not narrowing the rule; it is
  declining to be the one that decides a question it is disqualified from deciding.

### What the adjudicator needs, stated plainly and against C2's interest

| | cell 305 | cell 306 |
|---|---|---|
| Γ | −0.088029 | −0.030469 |
| margin (M_needed / M_after) | 1.353× | **1.112×** |
| Γ under every constant × 1.25 | −0.033733 — **still closes** | +0.029163 — **does not close** |
| margin under C1's coarser registry | 1.35× | 1.019× |
| independent derivations closing it | 4 | 3 |

**Cell 306 does not survive a 25 % degradation of its constants.** C2 states this rather than burying it. Against
that: the 25 % scenario is not a gate input, it is a severity C2 invented and applied to itself; it degrades all
six operator constants simultaneously and in the same direction, which is not a failure mode anyone has argued is
physical; and the constants it degrades have now been re-certified on an independent stack and at higher precision.
The honest summary is that 306 is a *sound* closure with a *thin* margin, and how much margin a permanent adoption
should require is a policy question, not an arithmetic one. That is exactly why it belongs to the adjudicator.
