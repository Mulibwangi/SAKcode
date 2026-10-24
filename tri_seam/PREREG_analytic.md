# Analytic rank-0 check for the 7 undecided curves: preregistration

Written and committed **before** the harness was run on any target or control curve. 2026-10-24.
During development the code was checked only on y² = x³ + k for k ∈ {1, −2, 9, −432, 16, 17, 2250, 180625}, which validated the aₚ formula and the functional-equation test.

## Why this route

mwrank left 7 companion curves undecided: it finds rank 0 but cannot prove it. A 3-isogeny Selmer bound cannot settle them. The obstruction elements themselves lie in Sel^ψ, so |Sel^ψ| ≥ 3 · |Sha[ψ]| ≥ 27 (the record gives |Sha[ψ]| ≥ 9 on these curves). That caps the bound at rank ≤ 2.

Instead: if L(E′, 1) ≠ 0 then rank E′(Q) = 0. This is Gross–Zagier–Kolyvagin together with modularity (Breuil–Conrad–Diamond–Taylor). With rank 0, im δ = ⟨[D]⟩, and the obstruction holds exactly when m = [b/c] ∉ {1, [D], [D]²}. That last step is an exact cube test.

| D | 850 | 1012 | 1173 | 2300 | 3335 | 7337 | 12325 |
|---|---|---|---|---|---|---|---|
| cubic (a, b, c) | (2,17,25) | (4,11,23) | (3,17,23) | (4,23,25) | (5,23,29) | (11,23,29) | (17,25,29) |

## Method (fixed in advance)

E′: y² = x³ + k, with k = 16D² reduced by sixth powers.

1. **aₚ.**
   - Good p ≡ 2 (mod 3), p ≥ 5: aₚ = 0.
   - Good p ≡ 1 (mod 3): aₚ = −Tr( conj((4k/π)₆) · π ), where π ≡ 2 (mod 3) is the primary prime of ℤ[ω] above p.
   - p ≥ 5 dividing k: additive reduction, aₚ = 0, conductor exponent 2.
   - Prime powers by the Hecke recursion.
2. **Validation (a prerequisite; abort on any mismatch).** The formula is checked against brute-force point counts at every good prime below 20 000, and at 10 random primes above 10⁶ (or as many as the coefficient range reaches), for every curve.
3. **Conductor and root number** are unknown only at 2 and 3. Search f₂ ∈ {0, 2, …, 8}, f₃ ∈ {0, 2, …, 5}; a₂ ∈ [−2, 2] if f₂ = 0, else 0; a₃ ∈ [−3, 3] if f₃ = 0, else 0; w = ±1. For each candidate, test θ(1/t) = w t² θ(t) at t = 1.1 and t = 1.25, where θ(t) = Σ aₙ e^{−2πnt/√N}.
   - **Accept** only a unique candidate with relative residual < 10⁻⁹ whose runner-up is > 10⁻⁴.
4. **L(E′, 1) = (1 + w) Σ aₙ/n · e^{−2πn/√N}**, with an explicit truncation-and-rounding error bound.
   - **Rank 0 certified** iff w = +1 and L(1) > 1000 × the error bound.
5. **Controls (selection rule fixed now).** From `descent_results.json`, among the curves mwrank certified: the 3 smallest D of rank 0, of rank 1 and of rank 2, plus the smallest D of rank 3.

## Predictions

- **V.** Validation passes for every curve.
- **F1.** Each of the 7 targets gets a unique accepted (N, w).
- **F2.** w = +1 for all 7.
- **F3.** L(E′, 1) > 1000 × the error bound for all 7. So rank 0, m ∉ im δ, and all **7 obstructions certified**.
  The tri-seam box would then read 234 PASS / 157 FAIL / 2 UNRESOLVED; the 2 are the descent-only solvable cubics, which lack a face-L point in this pipeline.
- **C1 (controls).** w = (−1)^rank for every control. L(1) is clearly positive at rank 0, and |L(1)| < 10⁻⁸ at rank ≥ 1.

## Evidential status, stated in advance

**NUMERICAL + THEOREM.**
- The conductor is identified numerically, by the functional equation.
- L(1) ≠ 0 is established numerically, with an explicit error bound.
- Rank 0 then follows from the cited theorems.

The code is independent of both PARI and eclib.

## Amendment (2026-10-24, before any target or control run)

**What happened.** In the self-test, y² = x³ + 9 got the correct candidate (N = 972, w = −1) with residual 1.4 × 10⁻¹⁵. An unrelated small-conductor candidate (N = 27) came in at 6.1 × 10⁻⁵, under the 10⁻⁴ runner-up rule, so the correct answer was wrongly rejected. Tiny-N candidates give smooth θ functions that the two-point test separates poorly.

**Changes, fixed before any target or control was run:**
- Test the functional equation at t = 1.1, 1.25 **and 1.5**.
- Accept iff the best residual < 10⁻⁹ **and the runner-up > 10⁻⁶**.

All target curves have N ≥ 7225, where this effect does not arise.
