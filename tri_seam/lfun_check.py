#!/usr/bin/env python3
"""Analytic rank-0 check for the 7 companion curves mwrank left undecided (see PREREG_analytic.md).

    python3 lfun_check.py               # the 7 targets + controls chosen from descent_results.json
    python3 lfun_check.py --self-test   # known small curves only

numpy + standard library only; independent of PARI and eclib. Writes lfun_results.json next to this file.

For E: y^2 = x^3 + k (j = 0, CM by Z[w]):
  * a_p from the closed form a_p = -Tr(conj((4k/pi)_6) * pi), pi the primary prime above p = 1 (mod 3);
    a_p = 0 for good p = 2 (mod 3); additive (a_p = 0, exponent 2) at p >= 5 dividing k.
  * The form is checked against brute-force point counts before use (abort on any mismatch).
  * Conductor exponents and Euler factors at 2 and 3, and the root number, are found by testing the
    functional equation theta(1/t) = w t^2 theta(t), theta(t) = sum a_n exp(-2 pi n t / sqrt N).
  * L(E,1) = (1 + w) sum a_n / n exp(-2 pi n / sqrt N), with an explicit error bound.
If w = +1 and L(E,1) > 1000 x error, then rank E(Q) = 0 (Gross-Zagier-Kolyvagin with modularity).
"""
import argparse
import json
import math
import os
import random
import time
from fractions import Fraction
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS = {850: (2, 17, 25), 1012: (4, 11, 23), 1173: (3, 17, 23), 2300: (4, 23, 25),
           3335: (5, 23, 29), 7337: (11, 23, 29), 12325: (17, 25, 29)}
T_VALUES = (1.1, 1.25, 1.5)
TERMS = 11.0                 # n_max = TERMS * sqrt(N): slowest theta term at the cut is ~exp(-55)
ACCEPT, RUNNER_UP = 1e-9, 1e-6
CERTIFY_FACTOR = 1000.0
F2, F3 = (0, 2, 3, 4, 5, 6, 7, 8), (0, 2, 3, 4, 5)
EIS = None                   # (primes = 1 mod 3, r, a, b), shared with worker processes by fork


# ------------------------------------------------------------------ arithmetic helpers
def factor(n):
    n, f, p = abs(n), {}, 2
    while p * p <= n:
        while n % p == 0:
            f[p] = f.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def sixth_free(k):
    s, out = (1 if k > 0 else -1), 1
    for p, e in factor(k).items():
        out *= p ** (e % 6)
    return s * out


def sieve(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return np.nonzero(s)[0]


def eisenstein(p):
    """Primitive cube root r of 1 mod p, and the primary pi = a + b w (a = 2, b = 0 mod 3), N(pi) = p, pi | (w - r)."""
    g = 2
    while pow(g, (p - 1) // 3, p) == 1:
        g += 1
    r = pow(g, (p - 1) // 3, p)
    Q = lambda u: u[0] * u[0] - u[0] * u[1] + u[1] * u[1]                    # noqa: E731
    B2 = lambda u, v: 2 * u[0] * v[0] - u[0] * v[1] - u[1] * v[0] + 2 * u[1] * v[1]   # noqa: E731
    u, v = (p, 0), (-r, 1)
    while True:
        if Q(u) < Q(v):
            u, v = v, u
        mu = (B2(u, v) + Q(v)) // (2 * Q(v))
        if mu == 0:
            break
        u = (u[0] - mu * v[0], u[1] - mu * v[1])
    a, b = v
    if Q(v) != p or (a + b * r) % p:
        raise RuntimeError(f"reduction failed at p={p}")
    for i in range(6):
        if a % 3 == 2 and b % 3 == 0:
            return r, a, b
        a, b = -b, a - b                 # multiply by w
        if i == 2:
            a, b = -a, -b
    raise RuntimeError(f"no primary associate at p={p}")


def ap_cm(k, p, r, a, b):
    """a_p = -Tr(conj(chi) * pi), chi = (4k / pi)_6 represented as c + d w."""
    z = pow((4 * k) % p, (p - 1) // 6, p)
    r2 = (r * r) % p
    chi = {1: (1, 0), r: (0, 1), r2: (-1, -1), p - 1: (-1, 0), p - r: (0, -1), (p - r2) % p: (1, 1)}[z]
    c, d = chi[0] - chi[1], -chi[1]                 # conj(c + d w) = (c - d) - d w
    e, f = c * a - d * b, c * b + d * a - d * b     # (c + d w)(a + b w)
    return -(2 * e - f)                              # Tr(e + f w) = 2e - f


def ap_brute(k, p):
    x = np.arange(p, dtype=np.int64)
    sq = np.zeros(p, dtype=bool)
    sq[(x * x) % p] = True
    v = ((x * x) % p * x + k) % p
    chi = np.where(v == 0, 0, np.where(sq[v], 1, -1))
    return -int(chi.sum())


# ------------------------------------------------------------------ one curve
def curve_info(k):
    k = sixth_free(k)
    bad = sorted(p for p in factor(k) if p >= 5)
    nbad = 1
    for p in bad:
        nbad *= p * p
    return k, bad, nbad


def n_max_for(nbad):
    return int(TERMS * math.sqrt(2 ** max(F2) * 3 ** max(F3) * nbad)) + 10


def analyse(job):
    label, k_in = job
    t0 = time.time()
    k, bad, nbad = curve_info(k_in)
    M = n_max_for(nbad)
    P1, R, A_, B_ = EIS
    use = P1 <= M
    aps = {int(p): ap_cm(k, int(p), int(r), int(a), int(b)) for p, r, a, b in zip(P1[use], R[use], A_[use], B_[use])
           if k % int(p)}

    # Validation: formula vs brute force at good primes below 20000 and 10 random large primes
    primes = sieve(M)
    small = [int(p) for p in primes if 5 <= p < 20000 and k % int(p)]
    rng = random.Random(k)
    large_pool = [int(p) for p in primes if p > 10 ** 6 and k % int(p)]
    large = rng.sample(large_pool, min(10, len(large_pool)))
    mism = [p for p in small + large if (aps.get(p, 0) if p % 3 == 1 else 0) != ap_brute(k, p)]
    if mism:
        return {"label": label, "k": k, "error": f"a_p formula mismatch at {mism[:10]}"}

    # Coefficients for n coprime to 6
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
    v2 = np.zeros(M + 1, dtype=np.int64)
    v3 = np.zeros(M + 1, dtype=np.int64)
    for base, arr in ((2, v2), (3, v3)):
        q = base
        while q <= M:
            arr[q::q] += 1
            q *= base

    def local(p, f, apv, emax):
        if f:
            return np.array([1.0] + [0.0] * emax)
        c = [1.0, float(apv)]
        while len(c) <= emax:
            c.append(apv * c[-1] - p * c[-2])
        return np.array(c)

    n_all = np.arange(M + 1, dtype=np.float64)
    cands = []
    for f2 in F2:
        for f3 in F3:
            N = 2 ** f2 * 3 ** f3 * nbad
            sN = math.sqrt(N)
            Mc = min(M, int(TERMS * sN) + 10)
            n = n_all[1:Mc + 1]
            wts = {x: np.exp((-2 * math.pi * x / sN) * n) for t in T_VALUES for x in (t, 1 / t)}
            for a2 in (range(-2, 3) if f2 == 0 else (0,)):
                for a3 in (range(-3, 4) if f3 == 0 else (0,)):
                    T2 = local(2, f2, a2, int(v2[:Mc + 1].max()))
                    T3 = local(3, f3, a3, int(v3[:Mc + 1].max()))
                    a = A0[1:Mc + 1] * T2[v2[1:Mc + 1]] * T3[v3[1:Mc + 1]]
                    th = {x: float(np.dot(a, w)) for x, w in wts.items()}
                    for w in (1, -1):
                        res = max(abs(th[1 / t] - w * t * t * th[t]) / (abs(th[1 / t]) + t * t * abs(th[t]) + 1e-300)
                                  for t in T_VALUES)
                        cands.append((res, f2, f3, a2, a3, w, N))
    cands.sort()
    best, second = cands[0], cands[1]
    out = {"label": label, "k": k, "bad_primes_ge5": bad, "validated_primes": len(small) + len(large),
           "n_max": M, "best": dict(zip(("residual", "f2", "f3", "a2", "a3", "w", "N"), best)),
           "runner_up_residual": second[0],
           "fe_accepted": best[0] < ACCEPT and second[0] > RUNNER_UP}
    res, f2, f3, a2, a3, w, N = best
    if out["fe_accepted"]:
        sN = math.sqrt(N)
        Mc = min(M, int(TERMS * sN) + 10)
        T2 = local(2, f2, a2, int(v2[:Mc + 1].max()))
        T3 = local(3, f3, a3, int(v3[:Mc + 1].max()))
        a = A0[1:Mc + 1] * T2[v2[1:Mc + 1]] * T3[v3[1:Mc + 1]]
        terms = a / n_all[1:Mc + 1] * np.exp((-2 * math.pi / sN) * n_all[1:Mc + 1])
        chunks = [float(np.sum(terms[i:i + 100000])) for i in range(0, len(terms), 100000)]
        s = math.fsum(chunks)
        s_abs = float(np.sum(np.abs(terms)))
        tail = 2 * math.exp(-2 * math.pi * Mc / sN) / (1 - math.exp(-2 * math.pi / sN))
        err = (1 + w) * (tail + 4e-15 * s_abs) if w == 1 else 0.0
        L1 = (1 + w) * s
        out.update(L1=L1, L1_error_bound=err, rank0_certified=(w == 1 and L1 > CERTIFY_FACTOR * err and L1 > 0))
    out["secs"] = round(time.time() - t0, 1)
    return out


# ------------------------------------------------------------------ main
def is_cube(q):
    q = Fraction(q)
    n, d = abs(q.numerator), q.denominator
    rt = lambda x: round(x ** (1 / 3)) if x else 0                                # noqa: E731
    return all(any((rt(x) + e) ** 3 == x for e in (-1, 0, 1)) for x in (n, d))


def main():
    global EIS
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--descent", default=os.path.join(HERE, "descent_results.json"))
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    t0 = time.time()

    jobs, roles = [], {}
    if a.self_test:
        for k in (1, -432, 16, -2, 9, 17):
            jobs.append((f"selftest k={k}", k))
    else:
        for D in TARGETS:
            jobs.append((f"target D={D}", 16 * D * D))
            roles[f"target D={D}"] = ("target", D)
        if os.path.exists(a.descent):
            curves = json.load(open(a.descent))["curves"]
            ok = {int(D): c["rank"] for D, c in curves.items()
                  if "error" not in c and c["certain"] and c["n_gens"] == c["rank"]}
            for r, howmany in ((0, 3), (1, 3), (2, 3), (3, 1)):
                for D in sorted(d for d, rk in ok.items() if rk == r)[:howmany]:
                    jobs.append((f"control D={D} rank={r}", 16 * D * D))
                    roles[f"control D={D} rank={r}"] = ("control", D, r)
        else:
            print("descent_results.json not found: running targets without controls", flush=True)

    M = max(n_max_for(curve_info(k)[2]) for _, k in jobs)
    P = sieve(M)
    P1 = P[(P % 3 == 1)]
    eis = [eisenstein(int(p)) for p in P1]
    EIS = (P1, np.array([e[0] for e in eis], dtype=object), np.array([e[1] for e in eis], dtype=object),
           np.array([e[2] for e in eis], dtype=object))
    print(f"[{time.time() - t0:6.1f}s] {len(jobs)} curves, coefficients to n = {M:,} ({len(P1):,} split primes)", flush=True)

    with get_context("fork").Pool(min(a.workers, len(jobs))) as pool:
        results = pool.map(analyse, jobs, chunksize=1)
    print(f"[{time.time() - t0:6.1f}s] analysis done", flush=True)

    summary = {"curves": len(results), "errors": [r["label"] for r in results if "error" in r]}
    for r in results:
        role = roles.get(r["label"])
        if role and role[0] == "target" and r.get("rank0_certified"):
            D = role[1]
            aa, b, c = TARGETS[D]
            m = Fraction(b, c)
            r["obstruction_certified"] = not any(is_cube(m * Fraction(D) ** e) for e in range(3))
        if role and role[0] == "control":
            rank = role[2]
            r["control_ok"] = (r.get("best", {}).get("w") == (-1) ** rank and r.get("fe_accepted", False) and
                               ((rank == 0 and r.get("rank0_certified")) or (rank > 0 and abs(r.get("L1", 1)) < 1e-8)))
    tg = [r for r in results if roles.get(r["label"], ("",))[0] == "target"]
    ct = [r for r in results if roles.get(r["label"], ("",))[0] == "control"]
    summary.update({
        "V_validation_passed": all("error" not in r for r in results),
        "F1_fe_accepted": f"{sum(r.get('fe_accepted', False) for r in tg)}/{len(tg)}",
        "F2_w_plus": f"{sum(r.get('best', {}).get('w') == 1 for r in tg)}/{len(tg)}",
        "F3_rank0_certified": f"{sum(bool(r.get('rank0_certified')) for r in tg)}/{len(tg)}",
        "obstructions_certified": f"{sum(bool(r.get('obstruction_certified')) for r in tg)}/{len(tg)}",
        "C1_controls_ok": f"{sum(bool(r.get('control_ok')) for r in ct)}/{len(ct)}",
        "secs": round(time.time() - t0, 1),
    })
    for r in results:
        b = r.get("best", {})
        print(f"{r['label']:24s} N={b.get('N')} w={b.get('w')} res={b.get('residual', float('nan')):.1e} "
              f"next={r.get('runner_up_residual', float('nan')):.1e} L1={r.get('L1', float('nan')):.6g} "
              f"err={r.get('L1_error_bound', float('nan')):.1e} {r.get('error', '')}", flush=True)
    json.dump({"summary": summary, "results": results},
              open(os.path.join(HERE, "lfun_results.json" if not a.self_test else "lfun_selftest.json"), "w"),
              indent=1, default=str)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
