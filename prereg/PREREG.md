# Pre-registrations: diagonal cubics

Written and committed **before** any per-cubic descent output (PARI) is
seen in this repo. The commit that adds this file is the timestamp.

Box: pairwise-coprime cube-free a ≤ b ≤ c ≤ 30 (969 cubics), as in
`harness/cubic_faces.py`. Its run gives 393 locally admissible cubics,
234 with a searched point, 2 with descent points, and **157 candidates** for
obstruction (no point to |x|,|y| ≤ 3000, not a descent case).

**Blinding caveat:** the aggregate 92 rigid / 65 twisted split is already
known from the record. Per-cubic labels are not. All predictions below are
per cubic.

---

## PREREG-1: Does the tri-seam predict rigid vs twisted?

**Why.** In `cubic_faces.py` the tri-seam verdict and the plain conjunctive
verdict agree on all 969 cubics. If the tri-seam is more than a relabelling,
it must predict something the baseline doesn't.

**Target.** For each of the 157 candidates: *twisted* if E′: η² = ξ³ + 16D²
has positive rank (δ(E′(ℚ)) larger than torsion), *rigid* if rank 0. Label
source: PARI descent harness (`ellrank`), with rank certified, i.e. lower
bound = upper bound. Cubics whose rank is not certified are excluded and
counted.

**Predictors** (frozen in `prereg/predictions.json`, computed by
`prereg/predict.py` from face-A data only):

- **T (tri-seam, local tension):** Σ over p ∈ {3} ∪ primes(D) of the
  Hensel depth, the smallest k at which a primitive point mod p^k meets the
  lift condition. Higher T predicts twisted.
- **B (baseline):** ω(D), the number of distinct primes dividing D.
  Higher B predicts twisted (more primes means a larger Selmer group).
- **R (strong baseline, computed with the labels):** root number of E′
  (`ellrootno`), where w = −1 predicts twisted. It is computed from D alone, not
  from descent, and the parity conjecture makes it the bar to beat.

**Primary metric.** AUC of T for twisted vs rigid.

**Success criterion for the tri-seam (all three required):**
1. AUC(T) ≥ 0.65
2. AUC(T) − AUC(B) ≥ 0.10
3. Permutation test (10,000 label shuffles): p < 0.01 for AUC(T)

**Secondary.** T adds information beyond R: in a logistic model of twisted
on R, adding T improves log-likelihood with likelihood-ratio p < 0.01.

**Outcomes stated in advance.**
- 1–3 met → the tri-seam's local face carries predictive signal; report it.
- 1–3 met but the secondary fails → the signal is a proxy for the root number;
  report that, not a new result.
- Otherwise → the tri-seam is a labelling scheme for this problem; report it so.

---

## PREREG-2: Consistency checks on |Ш[ψ]|

For each distinct D among the 157:

1. |Ш(E/ℚ)[ψ]| = |Sel^(ψ)| / |E′(ℚ)/ψE(ℚ)| is a power of 3.
2. Every cubic labelled obstructed has nonzero class O(C); every one of the
   236 cubics with a point has O(C) = 0. **Zero exceptions allowed.** Any
   exception is a harness bug and halts further claims.
3. Combining ψ and the dual ψ̂ sides, the order of Ш[3] implied for E
   (when finite) is a square (Cassels–Tate). A non-square result is a bug.

**Prediction:** every D with an obstructed cubic has |Ш[ψ]| ≥ 3.

---

## PREREG-3: Dual-seam asymmetry (SEM superordination)

Not testable yet. It needs reverse lifts F_{Q→S}, F_{GR→S} with computable
residuals. Registered here so the hypothesis can't be shaped after data:

- (A) residuals smallest starting from SEM → superordination holds
- (B) residuals symmetric → no privileged base

A test must be added to this file, and committed, before any residual is
computed.

---

## Frozen artefacts

| File | sha256 |
|------|--------|
| `prereg/predictions.json` | `3a87bd9a8ceb28d158b2ef334a7da28113a6d7bb4aa629f89d46f29d10e4f290` |

Changing a predictor, a threshold or the candidate set after this commit
voids that preregistration.
