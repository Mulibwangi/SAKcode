# Dual group Sha(E′)[ψ̂] for the 315 curves: preregistration

Written and committed **before** the harness was written or run. 2026-10-24.

## Purpose

The record leaves OPEN why every |Sha(E/Q)[ψ]| is a square (1, 9, 81), now confirmed on 315/315 curves. The Cassels–Tate pairing relates Sha(E)[ψ] to the dual Sha(E′)[ψ̂], so squareness is not automatic.

Here E: x³ + y³ = Dz³ (≅ y² = x³ − 432D²), E′: η² = ξ³ + 16D², ψ: E → E′, ψ̂: E′ → E.

## Method (fixed in advance; no PARI, no arithmetic over ℚ(√−3))

1. **Cassels' Selmer-ratio formula:**

       |Sel^ψ(E)| / |Sel^ψ̂(E′)| = (|E(Q)[ψ]| / |E′(Q)[ψ̂]|) · ∏_v |E′(Q_v)/ψE(Q_v)| / |E(Q_v)[ψ]|

   The global factors:
   - E(Q)[ψ] = 0, because the kernel points need √−3;
   - |E′(Q)[ψ̂]| = 3, from (0, ±4D).

   The local factors:
   - v = ∞: 1, since the kernel is not real and the cokernel of an odd-degree map is trivial;
   - p ∤ 3D: 1, by good reduction with p ≠ 3;
   - p | 3D: computed.

   Hence |Sel^ψ̂(E′)| = 3 · |Sel^ψ(E)| · ∏_{p | 3D} |E(Q_p)[ψ]| / |im δ_p|.
2. **The local quantities:**
   - |E(Q_p)[ψ]| = 3 if p ≡ 1 (mod 3), else 1.
   - |im δ_p| = #{q ∈ Q_p*/Q_p*³ : C_q(Q_p) ≠ ∅}, with C_q: cf(D q²) x³ + cf(q) y³ + z³ = 0, tested by the validated local test (`solvable_normalised`).

   Representatives of Q_p*/Q_p*³:
   - {pⁱ}, for p ≡ 2 (mod 3);
   - {pⁱ uʲ}, u a non-cube mod p, for p ≡ 1 (mod 3);
   - {3ⁱ 2ʲ}, for p = 3.
3. **The dual Sha.** |E(Q)/ψ̂E′(Q)| = 3^{r+1} / |im δ|, since E′(Q)[3] = ℤ/3 and E(Q)[ψ] = 0. So

       |Sha(E′)[ψ̂]| = |Sel^ψ̂(E′)| · |im δ| / 3^{r+1}

   using r from mwrank (308 curves) or the analytic rank 0 (7 curves), and |Sel^ψ|, |im δ| from `sha_results.json`.

## Predictions

- **T0 (validation; any failure means the formula orientation or the local computation is wrong):**
  - At two good primes per curve (one ≡ 1 and one ≡ 2 mod 3), |im δ_p| = |E(Q_p)[ψ]|.
  - |Sel^ψ̂| and |Sha(E′)[ψ̂]| come out as positive integer powers of 3 for **all 315 curves**.
  - D = 1 gives |Sel^ψ̂| = 3 and |Sha(E′)[ψ̂]| = 1. (E is the Fermat cubic, with E(Q) = ℤ/3 and rank 0.)
- **T1 (the hypothesis, held without strong prior): Sha(E′)[ψ̂] = 0 for all 315 curves.**
  If it holds, then Sha(E)[ψ] = Sha(E)[3]. That follows from the exact sequence 0 → Sha(E)[ψ] → Sha(E)[3] → Sha(E′)[ψ̂]. Cassels–Tate then makes |Sha(E)[3]| a square whenever Sha(E)[3^∞] is finite, which **explains the observed pattern**. That finiteness is known by Kolyvagin when the analytic rank is ≤ 1, and is otherwise conjectural.
  If T1 fails, the curves where it fails are listed with both sizes, and the explanation stays OPEN.

## Evidential status, stated in advance

- **Formula:** the computation rests on Cassels' theorem. The local factors and Selmer groups are this project's own exact computations.
- **The explanation in T1:** conditional on Sha[3^∞] being finite wherever that is not already known.
