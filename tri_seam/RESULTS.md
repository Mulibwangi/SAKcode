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
| K1–K3 | Constructed logic cases | Not implemented yet | **Not run** |

## What this shows (each item labelled)

- **SOLID (independent reproduction).** Code written from scratch reproduces, exactly, the record's locally admissible count (393) and the points at bounds 60 and 3000 (26 + 201, plus 7). It also reproduces the search plateau (159) and the failing primes (3, 7, 13, 19). The local test (exact Hensel lifting) and the point search (numpy) share no code with DL's PARI harnesses.
  This also pins down the box convention: 1 ≤ a ≤ b ≤ c ≤ 30, each coefficient cube-free, pairwise coprime.
- **Consistency.** 159 unresolved = the record's 157 certified obstructions + the 2 descent-only solvable cubics. The descent part itself is **not** re-checked here: PARI was not used, and no 3-descent was written.
- **By construction, not evidence.** 0 verdict changes. The tri-seam folds back to the conjunctive verdict by definition (P1 in `docs/tri-seam.md`). The run confirms that the code implements that correctly. It says nothing about the world.
- **Answer to the question asked.** The tri-seam does **not** materially change any outcome in this box. It adds localisation only: 576 FAILs are A-face failures, with the failing prime named; 234 PASS; 159 are UNRESOLVED on L and Co_global. Moving the 157 from UNRESOLVED to FAIL still needs the descent witness.

## Still open

- Re-score the 780-case structural-witness set (30.95% coverage) with per-face verdicts. This is the only existing number the tri-seam could move: by recording a FAIL on one face where the old instrument abstained. Needs that data and its format.
- Implement K1–K3.
- Independent 3-descent (Sage or Magma) on a sample of the 157, as in the record's next step 3.
