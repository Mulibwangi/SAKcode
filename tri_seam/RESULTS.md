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
- Independent 3-descent (Sage or Magma) on a sample of the 157, as in the record's next step 3.

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
