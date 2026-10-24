# Analytic rank ≤ 1 for the curves with non-trivial Sha[ψ]: preregistration

Written and committed **before** the harness was run on any of these curves. 2026-10-24.

## Purpose

`dual_sha_check.py` showed Sha(E′)[ψ̂] = 0 on all 315 curves. So Sha(E)[3] = Sha(E)[ψ], and |Sha(E)[ψ]| is a square **if Sha(E)[3^∞] is finite**.

Kolyvagin proves Sha finite when ord_{s=1} L(E, s) ≤ 1. This run tries to prove that for the **119 curves with |Sha[ψ]| ≥ 9** (117 of size 9, 2 of size 81). E and E′ are isogenous, so they share an L-function.

## Method (fixed in advance; independent of PARI and eclib)

- **Reused from the validated `lfun_check.py`:** the CM coefficients aₚ (checked against brute force on every curve) and the functional-equation search for N, w and the Euler factors at 2 and 3.
- **Speed change:** θ sums are grouped by (v₂(n), v₃(n)), with a coarse first pass over the 40 conductor candidates. The acceptance rule is unchanged: best residual < 10⁻⁹, runner-up > 10⁻⁶, at t = 1.1, 1.25, 1.5.
- **w = +1:** L(1) = Σ aₙ/n · (e^{−αn t₀} + e^{−αn/t₀}), with α = 2π/√N. Computed at t₀ = 1 and at t₀ = 1.2; the two must agree to 10⁻⁸ relative.
  - **Analytic rank 0** iff L(1) > 1000 × the error bound.
- **w = −1:** L′(1) = α Σ aₙ [I(t₀) + I(1/t₀)], with I(u) = (e^{−αnu} ln u + E₁(αnu)) / (αn). At t₀ = 1 this reduces to 2 Σ aₙ/n · E₁(αn). The same two-t₀ agreement is required.
  - **Analytic rank 1** iff L′(1) > 1000 × the error bound.
- **E₁:** scipy if available; otherwise a series below 1 and a continued fraction above. Either way it is checked against reference values before use.
- **Inputs:** the 119 curves come from `sha_results.json` (sha ≥ 9); algebraic ranks come from `descent_results.json` (mwrank) or the 7 analytic results.
- **Controls:** the rank-1 curves D = 6, 7, 9 (expect w = −1, L′(1) ≠ 0) and the rank-2 curves D = 19, 30, 65 (expect w = +1, L(1) ≈ 0).

## Predictions

- **R0 (validation).**
  - aₚ matches brute force on every curve.
  - E₁ is accurate to 10⁻¹² on reference points.
  - The two-t₀ values agree to 10⁻⁸ wherever an L-value is accepted.
  - Controls: rank-1 curves give w = −1 with L′(1) clearly non-zero; rank-2 curves give w = +1 with |L(1)| < 10⁻⁸.
- **R1 (parity).** For each of the 119 curves, a unique (N, w) with w = (−1)^r, where r is the algebraic rank.
- **R2.** Every curve with r = 0 has analytic rank 0, and every curve with r = 1 has analytic rank 1. For these, **Sha(E) is finite** (Gross–Zagier–Kolyvagin), so the square pattern is explained **unconditionally**.
- **R3.** Curves with r ≥ 2 do not reach analytic rank ≤ 1. For them finiteness of Sha stays **conditional**, and this is reported as a limit, not a failure.

## Evidential status, stated in advance

**NUMERICAL + THEOREM.** As in the earlier analytic check, the conductor is identified numerically, by the functional equation. L(1) or L′(1) ≠ 0 is established numerically with explicit error bounds. The cited theorems do the rest.
