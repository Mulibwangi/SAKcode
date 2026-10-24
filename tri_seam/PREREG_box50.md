# Widening the cubic box to coefficients ≤ 50: preregistration

Written and committed **before** the box-50 pipeline was run. 2026-10-24.

## What is new

The Seam Obstruction Record and all checks so far use 1 ≤ a ≤ b ≤ c ≤ 30 (cube-free, pairwise coprime): 969 triples. Raising the bound to 50 gives **4 624 triples**. Nothing in the record covers the new ones, so this is new data for the programme. The mathematics stays classical.

## Pipeline (fixed in advance; `run_box.sh 50`, outputs in `box50/`)

1. `cubic_faces.py --box 50`: exact local test, then point search with |x|, |y| ≤ 60, then ≤ 3000.
2. `descent_check.py`: mwrank rank and saturated generators of E′; exact membership test m ∈ im δ.
3. `box_analytic.py`: for each curve mwrank leaves undecided, analytic rank via `rank_check.analyse`.
   - **Analytic rank 0:** im δ = ⟨[D]⟩.
   - **Analytic rank 1** with one saturated mwrank generator: im δ comes from that generator.
   - **Otherwise:** the curve stays UNRESOLVED.
   - The raw mwrank output is kept in `descent_raw.json`.
4. `sha_check.py` and `dual_sha_check.py`: |Sha(E)[ψ]| and |Sha(E′)[ψ̂]| for every decided curve.
5. `rank_check.py`: analytic rank ≤ 1, hence finite Sha (Kolyvagin), for every curve with |Sha[ψ]| ≥ 9.
6. `box_report.py`: the predictions below, including comparison with the box-30 results in the parent folder.

## Predictions

- **X0 (nesting; any failure is a method error).** Restricted to coefficients ≤ 30, box 50 reproduces box 30 exactly:
  - 969 triples, 393 admissible, 234 with a point;
  - the same 157 obstructed cubics;
  - identical |Sha[ψ]|, |Sha(E′)[ψ̂]| and analytic-rank verdicts on the 315 box-30 curves.
- **X1.** No cubic with a found rational point is classified obstructed.
- **X2.** Local failures occur only at p = 3 and at primes p ≡ 1 (mod 3). In the 50-box the failing set is exactly **{3, 7, 13, 19, 31, 37, 43}**. For p ≡ 2 (mod 3) cubing is a bijection on units, so a diagonal cubic is always solvable there.
- **X3 (exploratory, no numeric prediction).** The obstructed share of admissible cubics, compared with 39.9% in box 30.
- **X4.** Every decided |Sha[ψ]| is a square, and |Sha(E′)[ψ̂]| = 1 on every decided curve. This is the box-30 pattern carried over; a failure would be informative, not a method error.
- **X5.** Every curve with |Sha[ψ]| ≥ 9 and algebraic rank ≤ 1 gets analytic rank = algebraic rank, so finite Sha and an unconditional square explanation. Curves of rank ≥ 2 stay conditional.
- **X6 (exploratory).** Does "|Sha[ψ]| ≥ 9 ⇔ the curve carries an obstructed cubic in the box" persist? In box 30 it held one way (117/117) but not the other: the two size-81 curves carry none. Counts are reported both ways.
- **X7.** At least 95% of admissible cubics are decided (point found, or descent with an mwrank or analytic witness).

## Evidential status, stated in advance

- **Local test, search, descent test, Selmer and dual computations:** this project's exact code.
- **Generators:** mwrank.
- **Analytic ranks:** NUMERICAL + THEOREM, as before.
- **Novelty:** the data is new to the record; the mathematics is classical, and nothing here is claimed as new mathematics.
