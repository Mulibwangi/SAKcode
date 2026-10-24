#!/usr/bin/env python3
"""Independent re-measurement of |Sha(E/Q)[psi]| for the 315 companion curves (see PREREG_sha.md).

    python3 sha_check.py [--record ~/Downloads/seam_sha_results.json] [--workers 32]

Reads descent_results.json and lfun_results.json from this folder, and reuses this project's validated code:
solvable_at (exact Hensel local test, cubic_faces.py) and in_image / delta (exact cube-class test,
descent_check.py). No PARI. Writes sha_results.json.

  Sel^psi = { q supported on primes of 3D : C_q: cf(D q^2) x^3 + cf(q) y^3 + z^3 = 0 locally solvable }
  im delta = < [D], delta(generators) >      |Sha[psi]| = |Sel| / |im delta|
"""
import argparse
import itertools
import json
import os
import sys
import time
from collections import Counter
from fractions import Fraction
from multiprocessing import get_context

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cubic_faces import primes_of, solvable_at          # noqa: E402
from descent_check import delta, in_image, is_cube      # noqa: E402


def cube_free(n):
    out, p = 1, 2
    while p * p <= n:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        out *= p ** (e % 3)
        p += 1
    return out * n


def vp(n, p):
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def solvable_normalised(coefs, p):
    """Local solvability at p after rescaling so at most one coefficient is divisible by p.
    Multiplying the equation by p and absorbing cubes into the variables keeps solvability.
    If the three valuations are distinct mod 3, the three terms always have distinct valuations: no point."""
    vals = [vp(x, p) for x in coefs]
    units = [x // p ** v for x, v in zip(coefs, vals)]
    res = [v % 3 for v in vals]
    if len(set(res)) == 3:
        return False
    rep = next(r for r in res if res.count(r) >= 2)
    new = [u * p ** ((r - rep) % 3) for u, r in zip(units, res)]
    return solvable_at(*new, p)


def class_of(x, G):
    """The q in G with x / q a cube, or None if x is not supported on the primes of G."""
    for q in G:
        if is_cube(Fraction(x) / q):
            return q
    return None


def measure(job):
    D, gens, source = job
    t0 = time.time()
    S = sorted(primes_of(3 * D))
    G = []
    for e in itertools.product(range(3), repeat=len(S)):
        q = 1
        for p, k in zip(S, e):
            q *= p ** k
        G.append(q)
    deltas = [delta((Fraction(x), Fraction(y)), D) for x, y in gens]
    sel, unres = set(), []
    for q in G:
        A, B = cube_free(D * q * q), cube_free(q)
        status = True
        for p in sorted({3} | primes_of(A * B)):
            r = solvable_normalised((A, B, 1), p)
            if r is False:
                status = False
                break
            if r is None:
                status = None
        if status is True:
            sel.add(q)
        elif status is None:
            unres.append(q)
    img = {q for q in G if in_image(Fraction(q), D, deltas)[0]}
    gens_supported = all(class_of(dl, G) is not None for dl in deltas)
    ratio = len(sel) / len(img) if img else float("nan")
    size = int(round(ratio)) if ratio == ratio else None
    dim = None
    if size:
        dim = 0
        while 3 ** dim < size:
            dim += 1
    return {"D": D, "source": source, "primes": S, "sel": len(sel), "img": len(img), "sha": size, "sha_dim": dim,
            "unresolved_q": unres, "img_in_sel": img <= sel, "power_of_3": size is not None and 3 ** dim == size and ratio == size,
            "trivial_and_D_in_sel": 1 in sel and class_of(D, G) in sel, "gens_supported_on_3D": gens_supported,
            "sel_classes": sorted(sel), "img_classes": sorted(img), "secs": round(time.time() - t0, 2)}


def extract_record(path):
    """Best-effort reader for the record's per-D Sha sizes. Returns {D: size} or None, plus a format note."""
    try:
        data = json.load(open(os.path.expanduser(path)))
    except Exception as exc:                                     # noqa: BLE001
        return None, f"could not read: {exc}"
    pairs = {}

    def sha_value(d):
        for k, v in d.items():
            if "sha" in k.lower() and isinstance(v, int) and not isinstance(v, bool):
                return v
        return None

    def walk(o):
        if isinstance(o, dict):
            for dk in ("D", "d", "Dval", "D_value"):
                if isinstance(o.get(dk), int):
                    v = sha_value(o)
                    if v is not None:
                        pairs[o[dk]] = v
            for k, v in o.items():
                if isinstance(k, str) and k.isdigit():
                    if isinstance(v, int) and not isinstance(v, bool):
                        pairs.setdefault(int(k), v)
                    elif isinstance(v, dict) and sha_value(v) is not None:
                        pairs[int(k)] = sha_value(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    if not pairs:
        top = list(data)[:20] if isinstance(data, dict) else type(data).__name__
        return None, f"no per-D Sha values recognised; top-level keys: {top}"
    return pairs, f"{len(pairs)} per-D values read"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--descent", default=os.path.join(HERE, "descent_results.json"))
    ap.add_argument("--lfun", default=os.path.join(HERE, "lfun_results.json"))
    ap.add_argument("--record", default="~/Downloads/seam_sha_results.json")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    a = ap.parse_args()
    t0 = time.time()

    dres = json.load(open(a.descent))
    rank0_analytic = set()
    if os.path.exists(a.lfun):
        for r in json.load(open(a.lfun))["results"]:
            if r.get("label", "").startswith("target D=") and r.get("rank0_certified"):
                rank0_analytic.add(int(r["label"].split("=")[1]))
    jobs, skipped = [], []
    for Ds, c in dres["curves"].items():
        D = int(Ds)
        if "error" not in c and c["certain"] and c["n_gens"] == c["rank"]:
            jobs.append((D, c["gens"], "mwrank"))
        elif D in rank0_analytic:
            jobs.append((D, [], "analytic rank 0"))
        else:
            skipped.append(D)
    print(f"{len(jobs)} curves to measure, {len(skipped)} without a certified rank", flush=True)
    with get_context("fork").Pool(a.workers) as pool:
        res = {r["D"]: r for r in pool.map(measure, sorted(jobs, key=lambda j: -j[0]), chunksize=1)}
    print(f"[{time.time() - t0:6.1f}s] measured", flush=True)

    # Cubic-level consistency
    cub_bad = []
    for x in dres["cubics"]:
        aa, b, c = x["abc"]
        r = res.get(x["D"])
        if r is None:
            continue
        S = r["primes"]
        G = [q for q in r["sel_classes"]] + [q for q in r["img_classes"]]
        allG = []
        for e in itertools.product(range(3), repeat=len(S)):
            q = 1
            for p, k in zip(S, e):
                q *= p ** k
            allG.append(q)
        qm = class_of(Fraction(b, c), allG)
        sel, img = set(r["sel_classes"]), set(r["img_classes"])
        ok = (qm in sel and qm not in img) if x["record"] == "obstructed" else (qm in img)
        if not ok:
            cub_bad.append(x["abc"])
        del G

    rows = list(res.values())
    dist = Counter(r["sha"] for r in rows)
    obstructed_D = {x["D"] for x in dres["cubics"] if x["record"] == "obstructed"}
    record, note = extract_record(a.record)
    cmp = None
    if record:
        common = [D for D in res if D in record]
        agree = [D for D in common if record[D] == res[D]["sha"]]
        agree_dim = [D for D in common if record[D] == res[D]["sha_dim"]]
        cmp = {"compared": len(common), "agree_as_order": len(agree), "agree_as_dimension": len(agree_dim),
               "disagree_examples": [(D, record[D], res[D]["sha"]) for D in common
                                     if record[D] != res[D]["sha"] and record[D] != res[D]["sha_dim"]][:10]}
    summary = {
        "curves_measured": len(rows), "curves_skipped": skipped,
        "S0_img_in_sel": f"{sum(r['img_in_sel'] for r in rows)}/{len(rows)}",
        "S0_power_of_3": f"{sum(r['power_of_3'] for r in rows)}/{len(rows)}",
        "S0_trivial_and_D_in_sel": f"{sum(r['trivial_and_D_in_sel'] for r in rows)}/{len(rows)}",
        "S0_generators_supported_on_3D": f"{sum(r['gens_supported_on_3D'] for r in rows)}/{len(rows)}",
        "S0_cubic_checks_failed": cub_bad,
        "local_tests_unresolved": sum(len(r["unresolved_q"]) for r in rows),
        "S1_distribution": {str(k): v for k, v in sorted(dist.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))},
        "S1_size_81_D": sorted(r["D"] for r in rows if r["sha"] == 81),
        "S2_record": note, "S2_comparison": cmp,
        "S3_obstructed_D_with_sha_ge_9": f"{sum(1 for D in obstructed_D if D in res and (res[D]['sha'] or 0) >= 9)}/{len(obstructed_D)}",
        "S4_all_squares": all(r["sha_dim"] is not None and r["sha_dim"] % 2 == 0 for r in rows),
        "S4_odd_dimension_D": sorted(r["D"] for r in rows if r["sha_dim"] is not None and r["sha_dim"] % 2),
        "max_selmer_size": max(r["sel"] for r in rows),
        "secs": round(time.time() - t0, 1),
    }
    json.dump({"summary": summary, "curves": rows}, open(os.path.join(HERE, "sha_results.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
