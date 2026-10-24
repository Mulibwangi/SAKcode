#!/usr/bin/env python3
"""Freeze PREREG-1 predictions before any descent output is seen.

    python3 prereg/predict.py      # writes prereg/predictions.json

Reads harness/cubic_faces_results.json. Uses face A / face L data only.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "harness"))
import cubic_faces as cf  # noqa: E402

DESCENT_POINTS = ([1, 25, 29], [19, 25, 29])


def hensel_depth(a, b, c, p):
    """Smallest k at which a primitive point mod p^k satisfies Hensel's lift
    condition (v(f) >= 2 v(grad) + 1). Same search as cf.solvable_at."""
    f = lambda x, y, z: a * x ** 3 + b * y ** 3 + c * z ** 3                     # noqa: E731
    g = lambda x, y, z: min(cf.vp(3 * a * x * x, p), cf.vp(3 * b * y * y, p), cf.vp(3 * c * z * z, p))  # noqa: E731
    charts = [lambda u, v: (u, v, 1), lambda u, v: (u, 1, v), lambda u, v: (1, u, v)]
    starts = [[(u, v) for u in range(p) for v in range(p)], [(u, 0) for u in range(p)], [(0, 0)]]
    best = None
    for chart, cur in zip(charts, starts):
        for k in range(1, cf.DEPTH_CAP + 1):
            pk, nxt, hit = p ** k, [], False
            for u, v in cur:
                x, y, z = chart(u, v)
                if f(x, y, z) % pk:
                    continue
                if 2 * g(x, y, z) + 1 <= k:
                    hit = True
                    break
                nxt.append((u, v))
            if hit:
                best = k if best is None else min(best, k)
                break
            if not nxt:
                break
            cur = [(u + pk * s, v + pk * t) for u, v in nxt for s in range(p) for t in range(p)]
    return best


def main():
    rows = json.load(open(os.path.join(HERE, "..", "harness", "cubic_faces_results.json")))["rows"]
    cand = [r for r in rows if r["A"] == "PASS" and r["point"] is None and r["abc"] not in DESCENT_POINTS]
    assert len(cand) == 157, len(cand)
    out = []
    for r in cand:
        a, b, c = r["abc"]
        D = a * b * c
        places = sorted({3} | cf.primes_of(D))
        depth = {p: hensel_depth(a, b, c, p) for p in places}
        T = sum(depth.values())                       # tri-seam: local tension
        B = len(cf.primes_of(D))                      # baseline: omega(D)
        out.append({"abc": [a, b, c], "D": D, "depth": depth, "T": T, "B": B})
    for key in ("T", "B"):
        med = sorted(o[key] for o in out)[len(out) // 2]
        for o in out:
            o["pred_" + key] = "twisted" if o[key] > med else "rigid"
        print(key, "median", med, "predicted twisted", sum(o["pred_" + key] == "twisted" for o in out))
    json.dump({"n": len(out), "rows": out}, open(os.path.join(HERE, "predictions.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
