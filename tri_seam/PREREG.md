# Tri-seam re-scoring test: preregistration

Written and committed **before** any harness in this folder was run. 2026-10-24.

## Question

Does reading the seam as three faces (A, L, Co) instead of the conjunction A ∧ L ∧ Co materially change any earlier outcome?

## What can be tested here, and what can't

- **Testable in this cloud session:** the diagonal-cubic box from the Seam Obstruction Record (23 Oct 2026). This harness is written from scratch in Python and numpy and shares no code with DL's PARI harnesses. That makes it an independent re-check of the *local* and *search* parts.
- **Not testable here:**
  - The 3-isogeny descent. PARI/GP is not installed, so the 157 obstructions cannot be certified in this session.
  - The 780-case structural-witness set and the 200 finite seam checks. Their data is on DL's machine.

## Face assignment for a cubic a x³ + b y³ + c z³ = 0

| Face | Witness used here | PASS | FAIL | UNRESOLVED |
|---|---|---|---|---|
| A (admissibility) | exact local test at ℝ and every prime (Hensel, see code) | solvable at every place | not solvable at some place (named) | depth cap hit |
| L (lawful closure) | an explicit rational point, checked exactly | point found | (not used) | no point found up to the bound |
| Co_global | a point found (PASS); a descent certificate (FAIL), which is unavailable here | point found | — | otherwise |

Seam verdict, three-valued: FAIL if any face is FAIL; PASS if all are PASS; otherwise UNRESOLVED.
Conjunctive baseline: the same witnesses folded into one predicate, computed by separate code.

## Box convention (fixed in advance)

- **Primary:** 1 ≤ a ≤ b ≤ c ≤ 30; each coefficient cube-free; pairwise coprime (Selmer's normalisation).
- **Secondary, reported only:** the same, but requiring only gcd(a, b, c) = 1.

## Predictions

- **R1.** Primary box: exactly **393** cubics PASS face A.
  If not, the record's box convention differs from ours. That is reported as a definitional mismatch, not as a failure of the record.
- **R2.** Of the cubics that PASS A:
  - points with all coordinates ≤ 60 exist for **227** of them (the 26 trivial cubics plus 201);
  - with a search bound of 3,000, for **234**;
  - **159** have no point found up to 3,000 (the record's plateau).
- **R3 (the tri-seam question).** The tri-seam verdict equals the conjunctive verdict on every cubic: **0 changes**.
- **R4.** Every cubic that FAILs A names a failing prime in {3, 7, 13, 19}. The record says local failures occur only at these primes.
- **R5.** The two descent-only solutions in the record, (1, 25, 29) and (19, 25, 29), are not found by search up to 3,000. Both stay UNRESOLVED here. That they are solvable is checked separately by verifying the record's stated points exactly.
- **R6 (the limit, stated in advance).** Without a descent witness, the tri-seam leaves all ~159 unresolved cubics UNRESOLVED. **It cannot reproduce the 157 FAILs.** The faces reading reorganises witnesses; it does not supply them.

## Constructed cases (logic checks, labelled CONSTRUCTED)

These pass by construction, so they show that the code matches the definitions. They are **not** evidence about the world.

- **K1.** Relation counterexample: exact round-trip, order not preserved. Predicted faces: A PASS, L PASS, Co FAIL.
- **K2.** ℤ₃ cocycle on a triangle: every overlap agrees pairwise, but the product of the transition elements is not 1. Predicted: Co_local PASS, Co_global FAIL.
- **K3.** Wrong-referent proxy: the round-trip and the relations are preserved, but the referent ID is swapped. Predicted: A FAIL, L PASS, Co PASS.

In every case the conjunctive verdict is FAIL. Only the tri-seam names the face.
