# Tri-Seam: treating the CPMF seam as a three-faced object

Principal: David Lee · Drafted 2026-10-24 · Builds on CPMF_SEM_HANDOVER (2026-10-24)

Overall status: **CONCEPTUAL**. This document proposes structure and does not report any new result.
Every proposition below carries its own evidential label.

---

## 1. The change in one line

Handover form: `S = {(P, C, w) : A ∧ L ∧ Co}`. The seam is a single predicate, and it collapses three checks into one bit.

Tri-seam form: `S = (S_A, S_L, S_Co)`. The seam is a **triple of faces**. Each face carries its own witness and verdict, and the faces are combined only at the end, by an explicit rule.

> P1 (CONCEPTUAL). The tri-seam loses no information against the conjunctive seam: the old verdict is recoverable as
> `PASS ⇔ v_A = v_L = v_Co = PASS`. The reverse does not hold, because one conjunctive FAIL cannot say which face failed.

## 2. The three faces

| Face | Question it answers | Witness it needs | What it must not be confused with |
|---|---|---|---|
| **A** (Admissibility) | Is this candidate *allowed* to cross? (identity and version of the referent, typed interpretations, declared legitimate losses) | Independent referent grounding | Relational fit (that is R) |
| **L** (Lawful closure) | Do the forward and return maps close under the declared law? (`B(F(p)) ~_I p`, explicit after-state) | Round-trip and closure witness | Truth: *recovery ≠ truth* |
| **Co** (Coherence/constraint) | Do the preserved relations hold **jointly**, within tolerance? | Relation-preservation and joint-compatibility witness | Pairwise consistency: *pairwise ≠ global* |

Kept from the handover, unchanged:
- **R** is *derived* from A and Co (`R := R(A, Co)`). **It is not a fourth face.**
- **B** is the recovery operation, used *inside* the L face. **B is not R.**

## 3. The face verdicts

Each face returns one of `{PASS, FAIL, UNRESOLVED}`, so a seam crossing gets a **verdict vector** `v = (v_A, v_L, v_Co)` with 27 possible states.

> P2 (CONCEPTUAL). The three faces are separable: each is witnessed independently. Exactly how independent they are is open (see §6).

Combining rule, which must be stated explicitly and never left implicit:
- **Seam PASS:** all three faces PASS.
- **Seam FAIL:** any face FAILs, and the report **names the face**.
- **Seam UNRESOLVED:** otherwise. Report which faces are still open.
- *Failing to convict is not certification.* `(PASS, PASS, UNRESOLVED)` is UNRESOLVED, not "nearly PASS".

## 4. Why three faces: existing results land on different faces

These results are already in the handover. The tri-seam does not re-prove them; it only shows where each one sits.

| Existing result | Status (as handed over) | Profile it implies | What one conjunctive bit would hide |
|---|---|---|---|
| Relation counterexample: exact round-trip, relations not preserved | MATHEMATICAL | `(·, PASS, FAIL)` | That closure *succeeded*. The failure is on Co alone |
| Isospectral Lindblad: spectra match (~5.68e-14), algebras differ | COMPUTED | The spectral witness passes Co, while a richer algebraic witness fails it | That the verdict depends on how strong the **witness** is, face by face |
| Joint obstruction: locally compatible, does not glue globally | MATHEMATICAL_IN_SPECIFIED_MODELS | `(·, ·, FAIL)` at global scope, while each local patch PASSes | The difference between pairwise and global coherence |
| ZipTie proxy keeps the wrong referent | NEGATIVE FINDING | `(FAIL, PASS?, PASS?)` | An A failure hidden behind good closure |
| "Flicker": instantiation without enough holding/return evidence | CONCEPTUAL | `(PASS?, UNRESOLVED, ·)` | That flicker is specifically an **L** gap |

> P3 (CONCEPTUAL, motivated by the results above). The known failure modes are not all one kind: they sit on different faces. A seam instrument that reports per face is therefore strictly more diagnostic than a conjunctive one. This is a claim about *reporting*, not about the world.

## 5. Mapping onto the modalities and the scalpel

- **is / might / may → faces** (CONCEPTUAL, offered as a reading, not an identity):
  - *might* ≈ the A face (a candidate under admissibility constraints).
  - *is* needs L (the instantiation was recorded and it returns).
  - *may* (constitutive counts-as, SA) is **not** delivered by any face. All three faces PASSing is necessary at most, never sufficient. **SA certification remains NOT_ACHIEVED.**
- **Semantic scalpel, per face:**
  - referent and claim scope → A
  - term meaning and witness strength → L and Co
  - relation preservation → Co
  - modal register → the combining rule

  The forbidden identifications now each have a home: `recovery == truth` (L), `pairwise == global` (Co), `spectral == algebraic` (Co witness strength), `SA == SEM` (outside every face).

## 6. Open questions this raises

1. **How independent are the faces?** Can Co be judged when L is UNRESOLVED? A first guess is a partial order, *A before L before Co*, but loops in the transport may break that. UNRESOLVED.
2. **Per-face metrics.** Split `Θ_SEM` into `(Θ_A, Θ_L, Θ_Co)` plus a separate obstruction penalty? This must not inherit TAS's product form (`Q = τασκ`), which stays HEURISTIC and must not be presented as a probability law. UNRESOLVED.
3. **Tri-register reading.** "Tri" could also mean a seam spanning GR / QM / SEM at once. That needs the joint GR-QM-SEM witness that has not yet been built (`GR_QM_SA_common_transport_not_constructed`). It is a different object from the three faces and must not be merged with them. UNRESOLVED.
4. **Empirical check.** Re-score the existing finite seam checks (200) and the structural-witness set (780 classifications, 30.95% coverage) with per-face verdicts. Does abstention concentrate on one face? NOT YET RUN.

## 7. What this document does *not* claim

- That the faces are orthogonal, or form any geometry.
- That the three faces are complete: no other face has been ruled out, and R is excluded **by design**, not by proof.
- That passing all three faces certifies meaning, truth, or SA.
- Any revision of earlier results or negative findings. Those stand as recorded in the handover.
