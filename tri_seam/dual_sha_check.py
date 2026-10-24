#!/usr/bin/env python3
"""Dual group Sha(E')[psi-hat] for the 315 companion curves via Cassels' Selmer ratio (see PREREG_dual.md).

    python3 dual_sha_check.py [--workers 32]

Reads sha_results.json, descent_results.json and lfun_results.json from this folder; reuses this project's
validated local test (solvable_normalised, cube_free in sha_check.py). No PARI. Writes dual_sha_results.json.

  |Sel^psihat(E')| = 3 * |Sel^psi(E)| * prod_{p | 3D} |E(Q_p)[psi]| / |im delta_p|
  |Sha(E')[psihat]| = |Sel^psihat(E')| * |im delta| / 3^(r+1)
"""
import argparse
import json
import os
import sys
import time
from collections import Counter
from fractions import Fraction
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cubic_faces import primes_of                          # noqa: E402
from sha_check import cube_free, solvable_normalised      # noqa: E402


def local_reps(p):
    """Representatives of Q_p* / Q_p*^3 as positive integers."""
    if p == 3:
        units = [1, 2, 4]                                   # 2 = 2 (mod 9) is not a cube in Q_3
    elif p % 3 == 1:
        u = next(g for g in range(2, p) if pow(g, (p - 1) // 3, p) != 1)
        units = [1, u, u * u]
    else:
        units = [1]                                         # every unit is a cube when p = 2 (mod 3)
    return [p ** i * w for i in range(3) for w in units]


def local_image(D, p):
    n = 0
    for q in local_reps(p):
        r = solvable_normalised((cube_free(D * q * q), cube_free(q), 1), p)
        if r is None:
            return None
        n += bool(r)
    return n


def kernel(p):
    return 3 if p % 3 == 1 else 1                          # E(Q_p)[psi] is rational iff -3 is a square in Q_p


def power_of_3(x):
    x = Fraction(x)
    if x <= 0 or x.denominator != 1:
        return None
    n, e = x.numerator, 0
    while n % 3 == 0:
        n //= 3
        e += 1
    return e if n == 1 else None


def good_primes(D, count_each=1):
    out, p = {1: [], 2: []}, 2
    while len(out[1]) < count_each or len(out[2]) < count_each:
        if all(p % d for d in range(2, int(p ** 0.5) + 1)) and (3 * D) % p:
            k = 1 if p % 3 == 1 else 2
            if len(out[k]) < count_each:
                out[k].append(p)
        p += 1
    return out[1] + out[2]


def analyse(job):
    D, sel, img, rank = job
    bad = sorted(primes_of(3 * D))
    loc = {p: local_image(D, p) for p in bad}
    checks = {p: (local_image(D, p), kernel(p)) for p in good_primes(D)}
    good_ok = all(a == b for a, b in checks.values())
    if any(v is None for v in loc.values()):
        return {"D": D, "error": f"local test unresolved at {[p for p, v in loc.items() if v is None]}"}
    ratio = Fraction(1)
    for p in bad:
        ratio *= Fraction(kernel(p), loc[p])
    sel_hat = 3 * sel * ratio
    sha_hat = sel_hat * img / Fraction(3) ** (rank + 1)
    sha = Fraction(sel, img)
    return {"D": D, "rank": rank, "sel": sel, "img": img, "sha": int(sha) if sha.denominator == 1 else str(sha),
            "local_image": {str(p): loc[p] for p in bad}, "local_kernel": {str(p): kernel(p) for p in bad},
            "good_prime_checks": {str(p): list(v) for p, v in checks.items()}, "good_ok": good_ok,
            "sel_hat": str(sel_hat), "sha_hat": str(sha_hat),
            "sel_hat_pow3": power_of_3(sel_hat), "sha_hat_pow3": power_of_3(sha_hat)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    t0 = time.time()
    sha = {r["D"]: r for r in json.load(open(os.path.join(HERE, "sha_results.json")))["curves"]}
    curves = json.load(open(os.path.join(HERE, "descent_results.json")))["curves"]
    rank0 = set()
    lf = os.path.join(HERE, "lfun_results.json")
    if os.path.exists(lf):
        rank0 = {int(r["label"].split("=")[1]) for r in json.load(open(lf))["results"]
                 if r.get("label", "").startswith("target D=") and r.get("rank0_certified")}
    jobs = []
    for D, r in sha.items():
        c = curves[str(D)]
        rank = 0 if D in rank0 else c["rank"]
        jobs.append((D, r["sel"], r["img"], rank))
    with get_context("fork").Pool(a.workers) as pool:
        rows = pool.map(analyse, sorted(jobs, key=lambda j: -j[0]), chunksize=1)
    ok = [r for r in rows if "error" not in r]
    pair = Counter((r["sha"], int(Fraction(r["sha_hat"])) if r["sha_hat_pow3"] is not None else r["sha_hat"]) for r in ok)
    d1 = next((r for r in ok if r["D"] == 1), None)
    summary = {
        "curves": len(rows), "errors": [r["D"] for r in rows if "error" in r],
        "T0_good_prime_checks": f"{sum(r['good_ok'] for r in ok)}/{len(ok)}",
        "T0_sel_hat_power_of_3": f"{sum(r['sel_hat_pow3'] is not None for r in ok)}/{len(ok)}",
        "T0_sha_hat_power_of_3": f"{sum(r['sha_hat_pow3'] is not None for r in ok)}/{len(ok)}",
        "T0_D1": {"sel_hat": d1["sel_hat"], "sha_hat": d1["sha_hat"]} if d1 else None,
        "T1_sha_hat_trivial": f"{sum(r['sha_hat'] == '1' for r in ok)}/{len(ok)}",
        "T1_nontrivial_D": sorted(r["D"] for r in ok if r["sha_hat"] != "1")[:50],
        "pairs_sha_vs_sha_hat": {f"{k[0]} | {k[1]}": v for k, v in sorted(pair.items(), key=str)},
        "secs": round(time.time() - t0, 1),
    }
    json.dump({"summary": summary, "curves": rows}, open(os.path.join(HERE, "dual_sha_results.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
