#!/usr/bin/env python3
"""Analytic rank <= 1 for the curves with non-trivial Sha[psi] (see PREREG_rank.md).

    python3 rank_check.py [--workers 16]          # the 119 curves with |Sha[psi]| >= 9, plus controls
    python3 rank_check.py --self-test             # controls only (rank 1: D = 6, 7, 9; rank 2: D = 19, 30, 65)

Reuses the validated pieces of lfun_check.py (CM a_p, brute-force validation, conductor candidates).
New here: theta sums grouped by (v2(n), v3(n)) with a coarse first pass, L'(1) via E1, and a two-t0 check.
numpy + standard library (+ mpmath only to validate E1, if present). Writes rank_results.json.
"""
import argparse
import json
import math
import os
import random
import sys
import time
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from lfun_check import (ACCEPT, CERTIFY_FACTOR, F2, F3, RUNNER_UP, T_VALUES, TERMS, ap_brute, ap_cm,  # noqa: E402
                        curve_info, eisenstein, n_max_for, sieve)

EULER = 0.57721566490153286061
COARSE_TERMS = 5.0
REFINE_TOP = 3
T0_ALT = 1.2
EIS = None
E1_REF = {1e-7: 15.540880086056784, 0.01: 4.037929576538114, 0.5: 0.5597735947761608, 1.0: 0.21938393439552029,
          5.0: 0.0011482955912753257, 10.0: 4.156968929685325e-06}      # mpmath 1.4.1 values


def e1(x):
    """Exponential integral E1(x), x > 0, vectorised: series below 1, continued fraction above, 0 beyond 700."""
    x = np.asarray(x, dtype=np.float64)
    out = np.zeros_like(x)
    s = x < 1.0
    if s.any():
        xs = x[s]
        term, acc = np.ones_like(xs), np.zeros_like(xs)
        for k in range(1, 40):
            term = term * (-xs) / k
            acc = acc + term / k
        out[s] = -EULER - np.log(xs) - acc
    c = (~s) & (x < 700)
    if c.any():
        xc = x[c]
        t = np.zeros_like(xc)
        for k in range(120, 0, -1):
            t = k * k / (xc + 2 * k + 1 - t)
        out[c] = np.exp(-xc) / (xc + 1 - t)
    return out


def e1_check():
    ref = dict(E1_REF)
    try:
        import mpmath
        ref = {x: float(mpmath.e1(x)) for x in (1e-7, 1e-3, 0.01, 0.3, 0.99, 1.0, 1.01, 2.0, 5.0, 10.0, 30.0, 60.0)}
    except ImportError:
        pass
    xs = np.array(sorted(ref))
    got = e1(xs)
    return float(np.max(np.abs(got - np.array([ref[x] for x in xs])) / np.array([ref[x] for x in xs])))


def local(p, f, apv, emax):
    if f:
        return np.array([1.0] + [0.0] * emax)
    c = [1.0, float(apv)]
    while len(c) <= emax:
        c.append(apv * c[-1] - p * c[-2])
    return np.array(c)


def psum(x):
    return math.fsum(float(np.sum(x[i:i + 200000])) for i in range(0, len(x), 200000))


def analyse(job):
    label, D, rank_alg = job
    t0 = time.time()
    k, bad, nbad = curve_info(16 * D * D)
    M = n_max_for(nbad)
    P1, R, A_, B_ = EIS
    use = P1 <= M
    aps = {int(p): ap_cm(k, int(p), int(r), int(a), int(b))
           for p, r, a, b in zip(P1[use], R[use], A_[use], B_[use]) if k % int(p)}
    primes = sieve(M)
    small = [int(p) for p in primes if 5 <= p < 20000 and k % int(p)]
    pool = [int(p) for p in primes if p > 10 ** 6 and k % int(p)]
    large = random.Random(k).sample(pool, min(10, len(pool)))
    mism = [p for p in small + large if (aps.get(p, 0) if p % 3 == 1 else 0) != ap_brute(k, p)]
    if mism:
        return {"label": label, "D": D, "error": f"a_p mismatch at {mism[:10]}"}

    A0 = np.ones(M + 1)
    A0[0] = 0.0
    root = int(M ** 0.5)
    for p in primes:
        p = int(p)
        if p < 5:
            continue
        ap = 0 if k % p == 0 else (aps[p] if p % 3 == 1 else 0)
        if p <= root:
            coef = [1.0, float(ap)]
            pe = p * p
            while pe <= M:
                coef.append(0.0 if k % p == 0 else ap * coef[-1] - p * coef[-2])
                pe *= p
            m = np.arange(p, M + 1, p)
            v = np.ones(len(m), dtype=np.int64)
            q = p * p
            while q <= M:
                v[(m % q) == 0] += 1
                q *= p
            A0[m] *= np.array(coef)[v]
        elif ap != 1:
            A0[p::p] *= ap
    del aps, primes
    v2 = np.zeros(M + 1, dtype=np.int8)
    v3 = np.zeros(M + 1, dtype=np.int8)
    for base, arr in ((2, v2), (3, v3)):
        q = base
        while q <= M:
            arr[q::q] += 1
            q *= base
    E2, E3 = int(v2.max()), int(v3.max())
    g = (v2.astype(np.int32) * (E3 + 1) + v3).astype(np.int32)
    n_all = np.arange(M + 1, dtype=np.float64)

    def residuals(f2, f3, terms):
        N = 2 ** f2 * 3 ** f3 * nbad
        sN = math.sqrt(N)
        Mc = min(M, int(terms * sN) + 10)
        S = {}
        for t in T_VALUES:
            for x in (t, 1 / t):
                w = np.exp((-2 * math.pi * x / sN) * n_all[1:Mc + 1])
                S[x] = np.bincount(g[1:Mc + 1], weights=A0[1:Mc + 1] * w, minlength=(E2 + 1) * (E3 + 1))
        out = []
        for a2 in (range(-2, 3) if f2 == 0 else (0,)):
            for a3 in (range(-3, 4) if f3 == 0 else (0,)):
                T = np.outer(local(2, f2, a2, E2), local(3, f3, a3, E3)).ravel()
                th = {x: float(np.dot(T, s)) for x, s in S.items()}
                for w_ in (1, -1):
                    r = max(abs(th[1 / t] - w_ * t * t * th[t]) / (abs(th[1 / t]) + t * t * abs(th[t]) + 1e-300)
                            for t in T_VALUES)
                    out.append((r, f2, f3, a2, a3, w_, N))
        return out

    coarse = sorted(c for f2 in F2 for f3 in F3 for c in residuals(f2, f3, COARSE_TERMS))
    top = []
    for c in coarse:
        if (c[1], c[2]) not in top:
            top.append((c[1], c[2]))
        if len(top) == REFINE_TOP:
            break
    fine = sorted(c for f2, f3 in top for c in residuals(f2, f3, TERMS))
    refined = set(top)
    others = [c for c in coarse if (c[1], c[2]) not in refined]
    best = fine[0]
    runner = min([fine[1][0]] + [c[0] for c in others[:1]])
    res, f2, f3, a2, a3, w, N = best
    out = {"label": label, "D": D, "rank_alg": rank_alg, "k": k, "n_max": M,
           "validated_primes": len(small) + len(large),
           "best": dict(zip(("residual", "f2", "f3", "a2", "a3", "w", "N"), best)), "runner_up_residual": runner,
           "fe_accepted": res < ACCEPT and runner > RUNNER_UP}
    if out["fe_accepted"]:
        sN = math.sqrt(N)
        Mc = min(M, int(TERMS * sN) + 10)
        a = A0[1:Mc + 1] * local(2, f2, a2, E2)[v2[1:Mc + 1]] * local(3, f3, a3, E3)[v3[1:Mc + 1]]
        n = n_all[1:Mc + 1]
        al = 2 * math.pi / sN
        vals, sabs = {}, 0.0
        for tz in (1.0, T0_ALT):
            if w == 1:
                terms = a / n * (np.exp(-al * n * tz) + np.exp(-al * n / tz))
            else:
                terms = al * a * (sum((np.exp(-al * n * u) * math.log(u) + e1(al * n * u)) / (al * n) for u in (tz, 1 / tz)))
            vals[tz] = psum(terms)
            sabs = max(sabs, float(np.sum(np.abs(terms))))
        tail = 4 * math.exp(-al * Mc / max(T0_ALT, 1 / T0_ALT)) / (1 - math.exp(-al / max(T0_ALT, 1 / T0_ALT)))
        err = tail + 1e-14 * sabs
        value = vals[1.0]
        agree = abs(vals[1.0] - vals[T0_ALT]) <= max(1e-8 * abs(value), 10 * err)
        nonzero = abs(value) > CERTIFY_FACTOR * err
        arank = (0 if nonzero else ">=2") if w == 1 else (1 if nonzero else ">=3")
        out.update(quantity="L(1)" if w == 1 else "L'(1)", value=value, value_t0_alt=vals[T0_ALT],
                   error_bound=err, two_t0_agree=agree, analytic_rank=arank,
                   finite_sha_proven=agree and arank in (0, 1) and arank == rank_alg)
    out["secs"] = round(time.time() - t0, 1)
    return out


def main():
    global EIS
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    t0 = time.time()
    e1_err = e1_check()
    if e1_err > 1e-12:
        raise SystemExit(f"E1 validation failed: max relative error {e1_err:.2e}")
    curves = json.load(open(os.path.join(HERE, "descent_results.json")))["curves"]
    rank_of = {int(D): c["rank"] for D, c in curves.items()}
    lf = os.path.join(HERE, "lfun_results.json")
    if os.path.exists(lf):
        for r in json.load(open(lf))["results"]:
            if r.get("label", "").startswith("target D=") and r.get("rank0_certified"):
                rank_of[int(r["label"].split("=")[1])] = 0
    controls = [("control D=%d rank=%d" % (D, r), D, r) for D, r in ((6, 1), (7, 1), (9, 1), (19, 2), (30, 2), (65, 2))]
    jobs = list(controls)
    if not a.self_test:
        sha = json.load(open(os.path.join(HERE, "sha_results.json")))["curves"]
        jobs += [(f"curve D={r['D']}", r["D"], rank_of[r["D"]]) for r in sha if (r["sha"] or 0) >= 9]
    M = max(n_max_for(curve_info(16 * D * D)[2]) for _, D, _ in jobs)
    P = sieve(M)
    P1 = P[P % 3 == 1]
    del P
    eis = [eisenstein(int(p)) for p in P1]
    EIS = (P1, np.array([e[0] for e in eis], dtype=object), np.array([e[1] for e in eis], dtype=object),
           np.array([e[2] for e in eis], dtype=object))
    del eis
    jobs.sort(key=lambda j: -curve_info(16 * j[1] * j[1])[2])
    print(f"[{time.time() - t0:6.1f}s] E1 max rel err {e1_err:.1e}; {len(jobs)} curves; coefficients to n = {M:,}",
          flush=True)
    results = []
    with get_context("fork").Pool(min(a.workers, len(jobs))) as pool:
        for r in pool.imap_unordered(analyse, jobs, chunksize=1):
            results.append(r)
            if len(results) % 10 == 0:
                print(f"[{time.time() - t0:6.1f}s] {len(results)}/{len(jobs)} done", flush=True)

    ct = [r for r in results if r["label"].startswith("control")]
    cv = [r for r in results if r["label"].startswith("curve")]

    def ctl_ok(r):
        if not r.get("fe_accepted") or not r.get("two_t0_agree"):
            return False
        if r["rank_alg"] == 1:
            return r["best"]["w"] == -1 and r["analytic_rank"] == 1
        return r["best"]["w"] == 1 and abs(r["value"]) < 1e-8
    by_rank = {}
    for r in cv:
        by_rank.setdefault(r["rank_alg"], []).append(r)
    summary = {
        "errors": [r["label"] for r in results if "error" in r],
        "E1_max_rel_err": e1_err,
        "R0_controls_ok": f"{sum(ctl_ok(r) for r in ct)}/{len(ct)}",
        "R0_two_t0_agree": f"{sum(bool(r.get('two_t0_agree')) for r in cv)}/{len(cv)}",
        "R1_fe_accepted": f"{sum(bool(r.get('fe_accepted')) for r in cv)}/{len(cv)}",
        "R1_parity_w_eq_minus1_pow_r": f"{sum(r.get('best', {}).get('w') == (-1) ** r['rank_alg'] for r in cv)}/{len(cv)}",
        "curves_by_algebraic_rank": {str(k): len(v) for k, v in sorted(by_rank.items())},
        "R2_finite_sha_proven": f"{sum(bool(r.get('finite_sha_proven')) for r in cv)}/{len(cv)}",
        "R2_by_rank": {str(k): f"{sum(bool(r.get('finite_sha_proven')) for r in v)}/{len(v)}" for k, v in sorted(by_rank.items())},
        "R3_not_provable_D": sorted(r["D"] for r in cv if not r.get("finite_sha_proven"))[:60],
        "secs": round(time.time() - t0, 1),
    }
    for r in sorted(ct, key=lambda r: r["D"]):
        print(f"{r['label']:22s} N={r.get('best', {}).get('N')} w={r.get('best', {}).get('w')} "
              f"{r.get('quantity')}={r.get('value', float('nan')):.6g} alt={r.get('value_t0_alt', float('nan')):.6g} "
              f"err={r.get('error_bound', float('nan')):.1e} rank_an={r.get('analytic_rank')}", flush=True)
    json.dump({"summary": summary, "results": sorted(results, key=lambda r: r["D"])},
              open(os.path.join(HERE, "rank_selftest.json" if a.self_test else "rank_results.json"), "w"),
              indent=1, default=str)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
