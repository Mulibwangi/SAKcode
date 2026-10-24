# Independent 3-isogeny descent check: preregistration

Written and committed **before** the descent harness was written or run. 2026-10-24.

## Purpose

The Seam Obstruction Record (DL, 23 Oct 2026) certifies 157 of the 393 locally admissible diagonal cubics as local-global failures. Those certificates use PARI's `ellrank`, `ellsaturation` and `elltors`. The record's next step 3 asks for an independent re-check.

This check also completes the tri-seam's Co_global face for the box. With a descent witness, the 157 should move from UNRESOLVED to FAIL. Without one, `cubic_faces.py` left them UNRESOLVED.

## Method (fixed in advance)

For C: a x³ + b y³ + c z³ = 0, put D = abc and m = [b/c] ∈ Q*/Q*³. Take the companion curve E′: η² = ξ³ + 16D² and the descent map δ(ξ, η) = [η − 4D], with δ(O) = 1, δ(0, 4D) = [1/D], δ(0, −4D) = [D]. These are the record's conventions, §1. C has a rational point if and only if m ∈ im δ.

1. **Rank and generators of E′(Q)** come from a tool **independent of PARI's `ellrank`**: Cremona's `mwrank` (eclib), either directly or through Sage. The tool is chosen by what is available on the machine.
   - A case counts as *decided* only if the tool states that the rank and a saturated basis were determined **unconditionally**.
   - Every generator is checked exactly on η² = ξ³ + 16D² before use.
2. **Torsion** contributes only δ(0, ±4D) = [D]^{±1}. Points of order 2 map trivially into the 3-torsion group Q*/Q*³.
3. **Membership test, with no factoring.** m ∈ im δ if and only if, for some exponents in {0, 1, 2}, m · [D]^{e₀} · ∏ δ(gᵢ)^{eᵢ} is a rational cube. A rational is a cube if and only if its reduced numerator and denominator are perfect cubes; −1 is a cube. This step is written from scratch, using exact integers.
4. **Inputs.** The 393 cubics that pass face A, from `cubic_faces_results.json`:
   - **solvable:** the 234 with a point found by search, plus (1, 25, 29) and (19, 25, 29) from the record's descent: 236 in total;
   - **obstructed:** the remaining 157.

## Predictions

- **D1 (control: validates δ and the normalisation of m).** All 236 solvable cubics: m ∈ im δ, for every decided case.
  A failure here means the method or the conventions are wrong. It does **not** refute the record.
- **D2 (the check).** All 157 obstructed cubics: m ∉ im δ, for every decided case.
  Each disagreement is reported individually.
- **D3.** Of the 157, **92** have a rank-0 companion and **65** a positive-rank companion. These are the record's counts.
- **D4.** At least 90% of the 393 cubics are decided unconditionally. Undecided cases are reported as UNRESOLVED, never counted as agreement.
- **D5 (tri-seam).** For every decided obstructed cubic, the face vector becomes A PASS, L UNRESOLVED, Co_global FAIL, and the seam verdict becomes FAIL. No PASS verdict changes.

## Limits stated in advance

- `mwrank` is independent of PARI's descent, but not of mathematics shared by both: the j = 0 curve and the conventions above. D1 is the guard against a shared convention error.
- This re-checks *which* cubics are obstructed. It does **not** re-measure the |Sha[ψ]| group sizes (1, 9, 81) or explain why they are all squares.
