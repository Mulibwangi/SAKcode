# Tri-seam re-scoring test: results

Run on 2026-10-24 on DL's machine (Minisforum, Ubuntu), in `~/Desktop/sshj/tri_seam/`, with system python3 and numpy 1.26.4.
The harness checksum matched the committed file (sha256 `8021aaca…acb11`). The run took 36.1 s.
The per-cubic results are in `cubic_faces_results.json` on that machine. They were not copied here.
Predictions: `PREREG.md`, committed before the run.

## Summary output

```json
{"box_primary":969,"A_PASS":393,"A_FAIL":576,"A_UNRESOLVED":0,"trivial_family":26,
 "point_le_60":227,"point_le_3000":234,"no_point_to_3000":159,"failing_primes":[3,7,13,19],
 "verdict_changes_tri_vs_conj":0,"tri_verdicts":{"PASS":234,"FAIL":576,"UNRESOLVED":159},
 "descent_only_cases_unresolved":[[1,25,29],[19,25,29]],"secondary_box_gcd_only":2744,"secs":36.1,
 "record_points_verify":{"1,25,29":true,"19,25,29":true}}
```

## Predictions against outcomes

| | Prediction | Outcome | Verdict |
|---|---|---|---|
| R1 | 393 cubics PASS face A (primary box) | 393 of 969 | **Supported** |
| R2 | Points: 227 at bound 60, 234 at bound 3000, 159 with none | 227 / 234 / 159 | **Supported** |
| R3 | 0 verdict changes, tri-seam vs conjunctive | 0 | **Supported** (by construction, see below) |
| R4 | Local failures only at primes {3, 7, 13, 19} | [3, 7, 13, 19] | **Supported** |
| R5 | (1,25,29) and (19,25,29) are not found by search; the record's points verify exactly | Both unresolved; both points verify | **Supported** |
| R6 | Without descent, the tri-seam cannot reproduce the 157 FAILs | 159 UNRESOLVED, 0 obstructions certified | **Supported** (the stated limit holds) |
| K1 | Exact round trip, order broken: faces A PASS, L PASS, Co FAIL | A PASS, L PASS, Co FAIL (7 order violations) | **Supported** (constructed) |
| K2 | ℤ₃ triangle: Co_local PASS, Co_global FAIL | Co_local PASS; Co_global FAIL (0 global sections, obstruction class 2) | **Supported** (constructed) |
| K3 | Swapped referent: A FAIL, L PASS, Co PASS | A FAIL (p0, p1), L PASS, Co PASS | **Supported** (constructed) |

## What this shows (each item labelled)

- **SOLID (independent reproduction).** Code written from scratch reproduces, exactly, the record's locally admissible count (393) and the points at bounds 60 and 3000 (26 + 201, plus 7). It also reproduces the search plateau (159) and the failing primes (3, 7, 13, 19). The local test (exact Hensel lifting) and the point search (numpy) share no code with DL's PARI harnesses.
  This also pins down the box convention: 1 ≤ a ≤ b ≤ c ≤ 30, each coefficient cube-free, pairwise coprime.
- **Consistency.** 159 unresolved = the record's 157 certified obstructions + the 2 descent-only solvable cubics. The descent part itself is **not** re-checked here: PARI was not used, and no 3-descent was written.
- **By construction, not evidence.** 0 verdict changes. The tri-seam folds back to the conjunctive verdict by definition (P1 in `docs/tri-seam.md`). The run confirms that the code implements that correctly. It says nothing about the world.
- **Answer to the question asked.** The tri-seam does **not** materially change any outcome in this box. It adds localisation only: 576 FAILs are A-face failures, with the failing prime named; 234 PASS; 159 are UNRESOLVED on L and Co_global. Moving the 157 from UNRESOLVED to FAIL still needs the descent witness.

## Still open

- Re-score the 780-case structural-witness set (30.95% coverage) with per-face verdicts. This is the only existing number the tri-seam could move: by recording a FAIL on one face where the old instrument abstained. Needs that data and its format.
- ~~Independent re-check of the 157 obstructions~~: **done**. 150 were re-certified by mwrank descent and 7 by the analytic rank-0 check (sections below).
- ~~Re-measure the |Sha[ψ]| group sizes~~: **done**. 315/315 agree with the record (section below).
- ~~Why every |Sha[ψ]| is a square~~: **explained, conditionally**. Sha(E′)[ψ̂] = 0 on all 315 curves, so Sha(E)[ψ] = Sha(E)[3], which Cassels–Tate makes a square whenever Sha(E)[3^∞] is finite (section below).
- ~~Make the square explanation unconditional~~: **done for 115 of 119**, via analytic rank ≤ 1 plus Kolyvagin (section below). Still conditional for the 4 rank-2 curves, D = 7590, 9570, 11730 and 14790.

## Constructed cases K1–K3 (run 2026-10-24, `constructed_cases.py`)

Status **CONSTRUCTED**: these pass by construction. They show the face checks match their definitions, not anything about the world.

| Case | Tri-seam verdict | Single-predicate verdict | Face the tri-seam names |
|---|---|---|---|
| K1 relation counterexample | FAIL | FAIL | Co (local and global) |
| K2 ℤ₃ cocycle, g₁₂+g₂₃+g₃₁ = 2 mod 3 | FAIL | FAIL | Co_global only |
| K3 wrong-referent proxy | FAIL | FAIL | A only |
| Passing control for each (added after preregistration) | PASS | PASS | none |

- All three preregistered predictions held. The single predicate gives FAIL in every case but cannot say which face failed. The tri-seam names it.
- K2 is the local-to-global gap in miniature. Each overlap is satisfiable on its own, but no global section exists. The obstruction is the cocycle class (2 mod 3), the counterpart of O in the Seam Obstruction Record.
- The controls (a monotone map, a cocycle summing to 0 mod 3, the correct referents) all PASS, so no face fails by accident.
- K1's Co_global equals Co_local by design: with a single chart, joint compatibility is just the conjunction of the local constraints.

## Independent 3-isogeny descent (run 2026-10-24, `descent_check.py`; predictions in `PREREG_descent.md`)

Run on DL's Minisforum: 32 workers, 47.8 s. Ranks and generators came from mwrank (eclib), via `passagemath-eclib` 10.8.13 in `~/Desktop/sshj/tri_seam/.venv-eclib`. No PARI was used. The harness checksum matched (`c5185fda…e5cc0`). The per-cubic results are in `descent_results.json` on that machine.

```json
{"admissible":393,"curves":315,"curves_undecided":[850,1012,1173,2300,3335,7337,12325],
 "D1_solvable_in_image":"236/236","D1_solvable_undecided":0,
 "D2_obstructed_confirmed":"150/157","D2_obstructed_undecided":7,"disagreements":[],
 "D3_obstructed_rank0":85,"D3_obstructed_rank_pos":65,"D4_decided_share":0.9822,
 "D5_tri_verdicts":{"PASS":234,"FAIL":150,"UNRESOLVED":9},"max_rank":3,"slowest_curve_secs":41.58,"secs":47.8}
```

| | Prediction | Outcome | Verdict |
|---|---|---|---|
| D1 | All 236 solvable cubics: m ∈ im δ | 236/236, none undecided | **Supported** (the method and conventions check out) |
| D2 | All decided obstructed cubics: m ∉ im δ | 150/150 decided agree; 7 undecided; **0 disagreements** | **Supported** |
| D3 | 92 rank-0 / 65 positive-rank companions among the 157 | 65 positive-rank (exact); 85 rank 0 certified + 7 where mwrank finds rank 0 but cannot prove it | **Supported for 65; 92 consistent but not certified** (85 + 7 uncertain) |
| D4 | ≥ 90% of the 393 decided unconditionally | 98.2% | **Supported** |
| D5 | Decided obstructed cubics → Co_global FAIL, seam FAIL; no PASS changes | 150 FAIL; 234 PASS unchanged | **Supported** |

### What this shows (each item labelled)

- **SOLID (independent re-check).** 150 of the record's 157 local-global failures are re-certified by a separate rank and saturation engine (mwrank), with the descent test written from scratch, and with no disagreement anywhere in the box. All 236 solvable cubics land in im δ, which confirms the shared conventions (δ and m = [b/c]).
- **UNRESOLVED, 7 cubics.** (2,17,25), (3,17,23), (4,11,23), (4,23,25), (5,23,29), (11,23,29), (17,25,29), with D = 850, 1173, 1012, 2300, 3335, 7337, 12325. mwrank finds rank 0 for each companion but cannot prove the upper bound. The likely cause is a non-trivial 2-part of Sha blocking its 2-descent. That cause is **not shown** here. These cases are not counted as agreement.
- **Tri-seam.** With the descent witness, the box reads 234 PASS / 150 FAIL / 9 UNRESOLVED. The 9 are the 7 above plus (1,25,29) and (19,25,29). For those two the descent agrees they are solvable, but this run holds no explicit point for face L. The record's points verify exactly (see the first run).
- **Not re-checked:** the |Sha[ψ]| group sizes (1, 9, 81) and why they are all squares.

### Correction (2026-10-24): what can close the 7

An earlier version of this note said a 3-isogeny Selmer bound would certify rank 0 for these curves. **That was wrong.** Each of the 7 cubics is a non-trivial element of Sha[ψ], and the record gives |Sha[ψ]| ≥ 9 on these curves. Those elements lie inside Sel^ψ, so the Selmer bound cannot go below rank ≤ 2. The 7 were closed analytically instead (next section).

## Analytic rank-0 check for the 7 (run 2026-10-24, `lfun_check.py`; predictions in `PREREG_analytic.md`)

Run on DL's Minisforum with system python3 and numpy 1.26.4. Nothing was installed. 32 workers, 11.1 s. The harness checksum matched (`d2064fdb…a9c6a6`). The self-test passed first (N = 36, 27, 27, 1728, 972, 10404). Coefficients ran to n = 20,129,571, using 638,989 split primes. The per-curve results are in `lfun_results.json` on that machine.

| Curve | N (found by functional equation) | w | FE residual / runner-up | L(E′, 1) | Error bound |
|---|---:|---:|---|---:|---:|
| target D = 850 | 780 300 | +1 | 2.7e-15 / 8.0e-04 | 6.71394 | 4.0e-14 |
| target D = 1012 | 6 912 972 | +1 | 2.5e-15 / 2.6e-04 | 6.33466 | 6.0e-14 |
| target D = 1173 | 37 150 083 | +1 | 2.4e-15 / 1.9e-03 | 6.03047 | 1.3e-13 |
| target D = 2300 | 1 428 300 | +1 | 2.5e-15 / 2.9e-03 | 4.81808 | 4.4e-14 |
| target D = 3335 | 300 300 075 | +1 | 3.7e-14 / 1.2e-03 | 4.25682 | 1.8e-13 |
| target D = 7337 | 484 484 121 | +1 | 3.4e-15 / 3.3e-04 | 6.54597 | 1.8e-13 |
| target D = 12325 | 164 058 075 | +1 | 5.5e-15 / 1.3e-03 | 2.75331 | 1.3e-13 |
| control D = 1, rank 0 | 27 | +1 | 1.8e-16 / 2.4e-03 | 0.58888 | 2.4e-15 |
| control D = 2, rank 0 | 36 | +1 | 7.3e-17 / 1.5e-02 | 0.701091 | 2.8e-15 |
| control D = 3, rank 0 | 243 | +1 | 2.6e-16 / 6.3e-04 | 1.22492 | 6.5e-15 |
| control D = 6, rank 1 | 972 | −1 | 2.0e-15 / 4.6e-04 | 0 (by sign) | — |
| control D = 7, rank 1 | 441 | −1 | 1.3e-15 / 4.3e-03 | 0 (by sign) | — |
| control D = 9, rank 1 | 243 | −1 | 1.3e-15 / 1.1e-03 | 0 (by sign) | — |
| control D = 19, rank 2 | 9 747 | +1 | 5.8e-16 / 2.5e-03 | 1.2e-17 | 1.8e-14 |
| control D = 30, rank 2 | 24 300 | +1 | 8.2e-16 / 3.1e-03 | 1.2e-16 | 1.6e-14 |
| control D = 65, rank 2 | 38 025 | +1 | 6.4e-16 / 3.1e-03 | 2.3e-17 | 2.2e-14 |
| control D = 1020, rank 3 | 7 022 700 | −1 | 3.6e-15 / 1.0e-02 | 0 (by sign) | — |

| | Prediction | Outcome | Verdict |
|---|---|---|---|
| V | The aₚ formula matches brute force on every curve | No mismatches on any of the 17 curves | **Supported** |
| F1 | A unique accepted (N, w) for each target | 7/7 | **Supported** |
| F2 | w = +1 for all 7 | 7/7 | **Supported** |
| F3 | L(E′, 1) > 1000 × error, hence rank 0 and the obstruction certified | 7/7; L(1) ranges 2.75–6.71, each at least 10¹³ × its error bound | **Supported** |
| C1 | Controls: w = (−1)^rank; L(1) clearly > 0 at rank 0 and ≈ 0 at rank ≥ 1 | 10/10 | **Supported** |

### What this shows (each item labelled)

- **NUMERICAL + THEOREM.** The 7 companion curves mwrank left open have rank 0. By rank 0 we get im δ = ⟨[D]⟩, and the exact cube test gives m ∉ im δ. So all **7 obstructions are certified**.
  - L(E′, 1) is non-zero by a margin of more than 10¹³ times the computed error bound.
  - Rank 0 then follows from Gross–Zagier–Kolyvagin together with modularity.
  - The conductors were identified numerically, by the functional equation. Residuals are 10⁻¹⁴ or smaller, and every runner-up is 10⁻⁴ or larger.
- **The controls discriminate.** Curves of known rank 1, 2 and 3 gave the expected sign and L(1) ≈ 0 (≤ 10⁻¹⁶). So a non-zero L(1) is not an artefact of the code.
- **Combined with the descent run:** all **157 of the record's 157** local-global failures are now independently re-certified, without PARI.
  - **150** by mwrank descent (SOLID).
  - **7** by the analytic route (NUMERICAL + THEOREM).
  - No disagreements anywhere.
- **Tri-seam, final for this box:** 234 PASS / 157 FAIL / 2 UNRESOLVED. The 2 are (1,25,29) and (19,25,29), which are solvable by descent; this pipeline holds no face-L point for them, but the record's points verify exactly.
- **Not re-checked:** the |Sha[ψ]| group sizes and why they are all squares. Consistent with the record, but not computed: L(1) values of size 3–7 on rank-0 curves are what you expect when Sha is non-trivial. No BSD quotient was computed.

## Independent re-measurement of |Sha(E/Q)[ψ]| (run 2026-10-24, `sha_check.py`; predictions in `PREREG_sha.md`)

Run on DL's Minisforum with system python3, 32 workers, 0.35 s. The harness checksum matched (`ba6b2488…32eb38`).

- **Sel^ψ:** the exact local test (`solvable_at`), after a p-adic normalisation. The normalisation was added after a slow development run and checked against the plain test on all 969 box cubics: 0 disagreements.
- **im δ:** from mwrank generators (308 curves) or from analytic rank 0 (7 curves).
- **Compared against:** the record's `~/Downloads/seam_sha_results.json`. Results are in `sha_results.json` on that machine.

```json
{"curves_measured":315,"curves_skipped":[],"S0_img_in_sel":"315/315","S0_power_of_3":"315/315",
 "S0_trivial_and_D_in_sel":"315/315","S0_generators_supported_on_3D":"315/315","S0_cubic_checks_failed":[],
 "local_tests_unresolved":0,"S1_distribution":{"1":196,"9":117,"81":2},"S1_size_81_D":[5610,20010],
 "S2_record":"316 per-D values read","S2_comparison":{"compared":315,"agree_as_order":315,"agree_as_dimension":0,"disagree_examples":[]},
 "S3_obstructed_D_with_sha_ge_9":"117/117","S4_all_squares":true,"S4_odd_dimension_D":[],"max_selmer_size":243,"secs":0.3}
```

| | Prediction | Outcome | Verdict |
|---|---|---|---|
| S0 | Consistency: im δ ⊆ Sel; powers of 3; 1 and [D] in Sel; 157 obstructed m ∈ Sel \ im δ; 236 solvable m ∈ im δ | Every check passes on 315/315 curves and all 393 cubics; 0 local tests unresolved | **Supported** |
| S1 | 196 × 1, 117 × 9, 2 × 81, with the 81s at D = 5610 and 20010 | Exactly that | **Supported** |
| S2 | Per-curve agreement with the record | **315/315 agree**, 0 disagreements | **Supported** |
| S3 | Every D carrying an obstructed cubic has \|Sha[ψ]\| ≥ 9 | 117/117 | **Supported** |
| S4 | All sizes are squares (re-observation only) | Yes; no odd dimension | **Supported as observation** |

### What this shows (each item labelled)

- **SOLID (independent re-measurement).** The record's |Sha(E/Q)[ψ]| values are reproduced on every one of the 315 companion curves. The Selmer groups use this project's own local test, and the images come from mwrank generators plus the 7 analytic rank-0 results. No PARI is used anywhere.
- **Observation.** The 117 curves of size 9 are exactly the 117 values of D that carry an obstructed cubic in the box. Both size-81 curves (D = 5610, 20010) carry none. Their Sha elements correspond to diagonal cubics outside the box's coefficient bound or normalisation; that is **not checked**.
- **Not investigated:** the record file holds 316 per-D entries, one more than the 315 curves of this box.
- **OPEN, unchanged:** *why* every size is a square. The Cassels–Tate pairing relates Sha(E)[ψ] to the dual Sha(E′)[ψ̂], not to itself, so squareness is not automatic for the ψ-part. This run confirms the pattern; it does not explain it.

## Dual group Sha(E′)[ψ̂] (run 2026-10-24, `dual_sha_check.py`; predictions in `PREREG_dual.md`)

Run on DL's Minisforum with system python3, 0.1 s. The harness checksum matched (`7c00ebcd…055e4`).

- **Method:** Cassels' Selmer-ratio formula. The local images |im δ_p| at every p | 3D come from this project's exact local test, and the global inputs from `sha_results.json`. No PARI, and no arithmetic over ℚ(√−3).

```json
{"curves":315,"errors":[],"T0_good_prime_checks":"315/315","T0_sel_hat_power_of_3":"315/315",
 "T0_sha_hat_power_of_3":"315/315","T0_D1":{"sel_hat":"3","sha_hat":"1"},
 "T1_sha_hat_trivial":"315/315","T1_nontrivial_D":[],
 "pairs_sha_vs_sha_hat":{"1 | 1":196,"81 | 1":2,"9 | 1":117},"secs":0.0}
```

| | Prediction | Outcome | Verdict |
|---|---|---|---|
| T0 | At good primes \|im δ_p\| = \|E(Q_p)[ψ]\|; both sizes powers of 3 on all curves; D = 1 gives 3 and 1 | 315/315, 315/315, 315/315; D = 1 gives 3 and 1 | **Supported** |
| T1 | Sha(E′)[ψ̂] = 0 on all 315 curves | **315/315 trivial** | **Supported** |

### What this shows (each item labelled)

- **SOLID, given Cassels' formula.** Sha(E′)[ψ̂] = 0 for all 315 companion curves. All the non-trivial Sha found in the box (117 curves of size 9, 2 of size 81) sits on the E side of the isogeny.
- **Consequence (exact).** Sha(E)[3] = Sha(E)[ψ] on every curve. Any x ∈ Sha(E)[3] has ψ(x) ∈ Sha(E′)[ψ̂] = 0, so x ∈ Sha(E)[ψ].
- **Explanation of the square pattern: THEOREM + condition.**
  - If Sha(E)[3^∞] is finite, the Cassels–Tate pairing is alternating and non-degenerate on it. Then Sha(E)[3^∞] ≅ M × M, and |Sha(E)[3]| = |M[3]|² is a square. That is exactly the observed 1, 9, 81.
  - The condition is proven (Kolyvagin) for the 7 curves with L(E′, 1) ≠ 0 computed above. For the other curves it is the standard expectation, not shown here.
  - This closes the record's OPEN item, conditionally.
- **Caveat on validation strength.** The "power of 3" check is weak: in the cloud test, an inverted formula failed it on only 2 of 68 curves. The formula's direction is pinned by the D = 1 anchor. E(Q) = ℤ/3 forces |Sel^ψ̂| ≥ 3; the correct direction gives exactly 3, and the inverted one gives 1/3, which is impossible. It is further pinned by the local checks at good primes, which pass on 315/315 curves.
- **Not a test of the tri-seam.** The powers of 3 come from using a degree-3 isogeny, not from any three-sided structure (see the discussion of 24 Oct). The seam-relevant shape is the three-term sequence (global | locally admissible | obstruction), which is independent of the degree.

## Analytic rank ≤ 1 for the curves with non-trivial Sha[ψ] (run 2026-10-24, `rank_check.py`; predictions in `PREREG_rank.md`)

Run on DL's Minisforum with system python3 and numpy, 16 workers, 13.9 s. The harness checksum matched (`d6cc9e43…ac830072`). The self-test passed first, 6/6 controls. E₁ was validated against mpmath, with max relative error 2.5e-16.

```
control D=6 rank=1     N=972 w=-1 L'(1)=2.37619 alt=2.37619 err=2.5e-14 rank_an=1
control D=7 rank=1     N=441 w=-1 L'(1)=1.65177 alt=1.65177 err=2.0e-14 rank_an=1
control D=9 rank=1     N=243 w=-1 L'(1)=1.29019 alt=1.29019 err=1.5e-14 rank_an=1
control D=19 rank=2    N=9747 w=1 L(1)=1.23625e-17 alt=1.41341e-16 err=4.4e-14 rank_an=>=2
control D=30 rank=2    N=24300 w=1 L(1)=1.20383e-16 alt=3.92074e-16 err=4.1e-14 rank_an=>=2
control D=65 rank=2    N=38025 w=1 L(1)=2.34122e-17 alt=3.45276e-17 err=5.5e-14 rank_an=>=2
{"errors":[],"E1_max_rel_err":2.488175462918802e-16,"R0_controls_ok":"6/6","R0_two_t0_agree":"119/119",
 "R1_fe_accepted":"119/119","R1_parity_w_eq_minus1_pow_r":"119/119","curves_by_algebraic_rank":{"0":71,"1":44,"2":4},
 "R2_finite_sha_proven":"115/119","R2_by_rank":{"0":"71/71","1":"44/44","2":"0/4"},
 "R3_not_provable_D":[7590,9570,11730,14790],"secs":13.8}
```

| | Prediction | Outcome | Verdict |
|---|---|---|---|
| R0 | Validation: aₚ, E₁, two-t₀ agreement; controls behave | No errors; E₁ 2.5e-16; 119/119 agree; controls 6/6 | **Supported** |
| R1 | A unique (N, w) with w = (−1)^r for every curve | 119/119 accepted; parity 119/119 | **Supported** |
| R2 | r = 0 ⇒ analytic rank 0; r = 1 ⇒ analytic rank 1; Sha finite | 71/71 and 44/44 | **Supported** |
| R3 | r ≥ 2 curves are not provable this way | All 4 rank-2 curves stay unprovable | **Supported (the stated limit)** |

### What this shows (each item labelled)

- **NUMERICAL + THEOREM.** For **115 of the 119** curves with non-trivial Sha[ψ], including both size-81 curves, ord_{s=1} L(E, s) equals the algebraic rank r ≤ 1. Gross–Zagier–Kolyvagin then makes **Sha(E) finite**.
- **Combined with the dual-Sha run (exact):** on these 115 curves, Sha(E)[3] = Sha(E)[ψ] and Sha(E)[3^∞] is finite. So the Cassels–Tate pairing **forces** |Sha(E)[ψ]| to be a square. The square pattern is now **explained unconditionally** for 115/119 non-trivial curves; the 196 curves of size 1 are squares trivially.
- **Still conditional:** D = 7590, 9570, 11730, 14790. All four have algebraic rank 2, where Kolyvagin does not apply. Finiteness of Sha there is the standard conjecture, not shown.
- **Status of the explanation:** this applies known theorems (Cassels–Tate, Gross–Zagier, Kolyvagin) to the record's data. It is new **to the record**, and is not claimed as new mathematics; the literature was not checked.

## Box widened to coefficients ≤ 50 (run 2026-10-24, `run_box.sh 50`; predictions in `PREREG_box50.md`)

Run on DL's Minisforum, about 52 minutes in total: point search 2.5 min, mwrank 41 min, rank ≤ 1 stage 7 min. The scripts were fetched from this repo at commit `eded06b1`, and all 9 checksums matched. Before the run, the whole pipeline was re-run in the cloud at bound 30 and reproduced every earlier box-30 result. Outputs are in `~/Desktop/sshj/tri_seam/box50/`.

```
{"box_bound":50,"triples":4624,"admissible":1398,
 "X0_nesting_box30":{"triples":969,"admissible":393,"with_point":234,"obstructed":157,"obstructed_set_equal_to_box30":true,
  "sha_per_curve":{"compared":315,"mismatches":0},"dual_per_curve":{"compared":315,"mismatches":0},"rank_per_curve":{"compared":119,"mismatches":0}},
 "X1_point_but_obstructed":[],"X2_failing_primes":[3,7,13,19,31,37,43],"X2_as_predicted":true,
 "X3_obstructed_share":0.4542,"X3_counts":{"with_point":741,"solvable_by_descent_only":18,"obstructed":635,"unresolved":4},
 "X4_sha_distribution":{"1":605,"3":4,"9":463,"81":11},"X4_all_squares":false,
 "X4_dual_trivial":"1079/1083","X4_dual_nontrivial_D":[473,2852,4042,31175],
 "X5_finite_sha_by_rank":{"0":"238/238","1":"212/212","2":"0/24"},
 "X6_nontrivial_curves":474,"X6_carrier_curves":461,"X6_nontrivial_and_carrier":457,"X6_nontrivial_not_carrier":17,
 "X6_carrier_not_nontrivial":[473,2852,4042,31175],"X7_decided_share":0.9971,
 "curves_still_undecided":[21199,25897,33511,58261]  (each: analytic rank 1, but mwrank found no generator)}
```

| | Prediction | Outcome | Verdict |
|---|---|---|---|
| X0 | Box 30 reproduced exactly inside box 50 | 969 / 393 / 234 / 157; same obstructed set; 0 mismatches on Sha (315), dual (315), rank (119) | **Supported** |
| X1 | No cubic with a point is classified obstructed | none | **Supported** |
| X2 | Local failures exactly at {3, 7, 13, 19, 31, 37, 43} | exactly that | **Supported** |
| X3 | Obstructed share (exploratory) | **45.4%**, against 39.9% in box 30 | reported |
| X4 | Every \|Sha[ψ]\| a square; dual Sha trivial everywhere | **4 curves have \|Sha[ψ]\| = 3**: D = 473, 2852, 4042, 31175. The same 4 are the only curves with non-trivial dual Sha (size 3) | **Not supported**: an informative failure, as anticipated in the prereg |
| X5 | Curves with \|Sha[ψ]\| ≥ 9 and rank ≤ 1: finite Sha | 238/238 at rank 0 and 212/212 at rank 1; 24 rank-2 curves not provable | **Supported** |
| X6 | "Non-trivial Sha ⇔ carries an obstruction" (exploratory) | See the correction below | reported |
| X7 | ≥ 95% decided | 99.7%; 4 cubics unresolved | **Supported** |

### The four size-3 curves, re-checked independently in the cloud (2026-10-24)

| D | Sel^ψ | im δ | \|Sha[ψ]\| | Sel^ψ̂ | \|Sha(E′)[ψ̂]\| | L(E′, 1), w = +1 |
|---|---:|---:|---:|---:|---:|---:|
| 473 | 9 | 3 | 3 | 3 | 3 | 6.12197 (err 2e-13) |
| 2852 | 9 | 3 | 3 | 3 | 3 | 10.0906 (err 2e-13) |
| 4042 | 9 | 3 | 3 | 3 | 3 | 8.98326 (err 4e-13) |
| 31175 | 9 | 3 | 3 | 3 | 3 | 4.54671 (err 5e-13) |

- **SOLID.** mwrank certifies rank 0 for all four, so im δ = ⟨[D]⟩ exactly and no generator can have been missed. Sel^ψ = 9 comes from the validated local test. Hence |Sha(E)[ψ]| = 3 is not an artefact.
- **NUMERICAL + THEOREM.** L(E′, 1) ≠ 0 on all four, so Sha is finite (Kolyvagin).
- **Consequence (exact, given finiteness).** |Sha(E)[ψ]| ≤ |Sha(E)[3]| ≤ |Sha(E)[ψ]| · |Sha(E′)[ψ̂]|, so 3 ≤ |Sha(E)[3]| ≤ 9. Cassels–Tate makes |Sha(E)[3]| a square, so **|Sha(E)[3]| = 9 exactly**. The 3-torsion splits as 3 on the ψ-side and 3 on the dual side.
- **What this changes.** The box-30 observation "every |Sha[ψ]| is a square" was a property of that box, holding because the dual Sha happened to be trivial there. **The invariant that is always a square (given finiteness) is |Sha(E)[3]|, not |Sha(E)[ψ]|.** The earlier explanation stands, but the claim it explains is now stated correctly.

### Correction to X6

The report counted "non-trivial" as |Sha[ψ]| ≥ 9, and that threshold misfiled the four size-3 curves as "carriers without non-trivial Sha". With non-trivial meaning |Sha[ψ]| ≥ 3:
- **Every curve carrying an obstructed cubic has non-trivial Sha[ψ]: 461/461.** This is forced by theory, since the cubic's class lies in Sel \ im δ.
- 17 curves have |Sha[ψ]| ≥ 9 but carry no obstructed cubic inside the box. In box 30 there were 2 such curves.

Because of the same threshold, `rank_check.py` skipped the four size-3 curves. They were checked separately above, and finite Sha is proven for all four.

### Still open from box 50

- **4 undecided curves:** D = 21199, 25897, 33511, 58261. Analytic rank 1 is proven, but mwrank found no generator. Needed: a point on E′, for instance from a larger search or a Heegner point.
- **18 cubics solvable by descent alone.** No point was found with |x|, |y| ≤ 3000. A larger search, or reconstruction from the descent, would give face L its explicit witness.
- **24 rank-2 curves.** Finiteness of Sha there stays conjectural, a limit of current theory.
