#!/usr/bin/env python3
"""Tri-seam re-scoring of the diagonal-cubic box (see PREREG.md).

    python3 cubic_faces.py            # writes cubic_faces_results.json

Independent of DL's PARI harnesses: numpy and the standard library only.
Covers face A (exact local solvability) and face L (rational points found by search).
Face Co_global FAIL needs a descent certificate, which this harness does not compute.
"""
import json
import math
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BOX = 30
DEPTH_CAP = 24


# ------------------------------------------------------------------ box
def cube_free(n):
    return all(n % (p ** 3) for p in range(2, int(round(n ** (1 / 3))) + 2))


def primes_of(n):
    out, p = set(), 2
    while p * p <= n:
        while n % p == 0:
            out.add(p)
            n //= p
        p += 1
    if n > 1:
        out.add(n)
    return out


def box(pairwise=True):
    cf = [n for n in range(1, BOX + 1) if cube_free(n)]
    for a in cf:
        for b in cf:
            if b < a:
                continue
            for c in cf:
                if c < b:
                    continue
                if pairwise:
                    if math.gcd(a, b) > 1 or math.gcd(a, c) > 1 or math.gcd(b, c) > 1:
                        continue
                elif math.gcd(math.gcd(a, b), c) > 1:
                    continue
                yield a, b, c


# ------------------------------------------------------------------ face A: exact local test
def vp(n, p):
    if n == 0:
        return 10 ** 9
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def solvable_at(a, b, c, p):
    """True / False / None (depth cap). Rigorous: Hensel (v(f) >= 2 v(grad f) + 1) for True;
    an empty set of primitive residues mod p^k for False."""
    f = lambda x, y, z: a * x ** 3 + b * y ** 3 + c * z ** 3                     # noqa: E731
    grad_v = lambda x, y, z: min(vp(3 * a * x * x, p), vp(3 * b * y * y, p), vp(3 * c * z * z, p))  # noqa: E731
    # Charts of primitive points: (u, v, 1); (u, 1, p*w); (1, p*w, p*w')
    charts = [lambda u, v: (u, v, 1), lambda u, v: (u, 1, v), lambda u, v: (1, u, v)]
    level1 = [
        [(u, v) for u in range(p) for v in range(p)],
        [(u, 0) for u in range(p)],
        [(0, 0)],
    ]
    for chart, start in zip(charts, level1):
        cur = start
        for k in range(1, DEPTH_CAP + 1):
            pk = p ** k
            nxt = []
            for u, v in cur:
                x, y, z = chart(u, v)
                if f(x, y, z) % pk:
                    continue
                m = grad_v(x, y, z)
                if 2 * m + 1 <= k:
                    return True
                nxt.append((u, v))
            if not nxt:
                break
            if k == DEPTH_CAP:
                return None
            cur = [(u + pk * s, v + pk * t) for u, v in nxt for s in range(p) for t in range(p)]
            # chart constraints (v = 0 mod p, or u, v = 0 mod p) are kept by lifting
    return False


def face_A(a, b, c):
    """Over R a cubic always has a point. Primes not dividing 3abc are smooth reductions with points."""
    failing, unresolved = [], []
    for p in sorted({3} | primes_of(a * b * c)):
        r = solvable_at(a, b, c, p)
        if r is False:
            failing.append(p)
        elif r is None:
            unresolved.append(p)
    if failing:
        return "FAIL", failing
    return ("UNRESOLVED", unresolved) if unresolved else ("PASS", [])


# ------------------------------------------------------------------ face L: rational points
def icbrt(t):
    r = np.rint(np.cbrt(t.astype(np.float64))).astype(np.int64)
    for d in (-1, 0, 1):
        ok = (r + d) ** 3 == t
        r = np.where(ok, r + d, r)
    return r, r ** 3 == t


def find_point(a, b, c, bound, start=0):
    """Primitive (x, y, z) with |x|, |y| <= bound (z free, as in the record's harness 1).
    Skips y < start (already searched). Returns the first point found, or None."""
    xs = np.arange(-bound, bound + 1, dtype=np.int64)
    for y in range(start, bound + 1):
        s = a * xs ** 3 + b * np.int64(y) ** 3
        div = (s % c) == 0
        t = np.where(div, -s // c, 0)
        z, cube = icbrt(t)
        hit = div & cube & ~((xs == 0) & (y == 0))
        if hit.any():
            i = int(np.argmax(hit))
            x, zz = int(xs[i]), int(z[i])
            assert a * x ** 3 + b * y ** 3 + c * zz ** 3 == 0
            return (x, y, zz)
    # The y-loop with start > 0 misses new |x| in (start, bound] for old y; cover that strip too
    if start:
        xs2 = np.concatenate([np.arange(-bound, -start, dtype=np.int64), np.arange(start + 1, bound + 1, dtype=np.int64)])
        for y in range(0, start):
            s = a * xs2 ** 3 + b * np.int64(y) ** 3
            div = (s % c) == 0
            t = np.where(div, -s // c, 0)
            z, cube = icbrt(t)
            hit = div & cube
            if hit.any():
                i = int(np.argmax(hit))
                x, zz = int(xs2[i]), int(z[i])
                assert a * x ** 3 + b * y ** 3 + c * zz ** 3 == 0
                return (x, y, zz)
    return None


# ------------------------------------------------------------------ verdicts
def tri_verdict(faces):
    v = list(faces.values())
    if "FAIL" in v:
        return "FAIL"
    return "PASS" if all(x == "PASS" for x in v) else "UNRESOLVED"


def conjunctive_verdict(local_ok, point):
    """Separate code path: one predicate, three-valued (strong baseline)."""
    if local_ok is False:
        return "FAIL"
    if local_ok is True and point is not None:
        return "PASS"
    return "UNRESOLVED"


def main():
    t0 = time.time()
    rows = []
    for a, b, c in box(pairwise=True):
        A, places = face_A(a, b, c)
        rows.append({"abc": [a, b, c], "A": A, "A_places": places})
    adm = [r for r in rows if r["A"] == "PASS"]
    print(f"[{time.time() - t0:5.1f}s] box {len(rows)} cubics, face A PASS {len(adm)}", flush=True)

    for r in adm:
        r["point"], r["found_at"] = None, None
        pt = find_point(*r["abc"], 60)
        if pt:
            r["point"], r["found_at"] = list(pt), 60
    left = [r for r in adm if r["point"] is None]
    print(f"[{time.time() - t0:5.1f}s] points with |x|,|y|<=60: {len(adm) - len(left)}", flush=True)
    for r in left:
        pt = find_point(*r["abc"], 3000)
        if pt:
            r["point"], r["found_at"] = list(pt), 3000
    print(f"[{time.time() - t0:5.1f}s] search to 3000 done", flush=True)

    changes = 0
    for r in rows:
        pt = r.get("point")
        faces = {"A": r["A"],
                 "L": "PASS" if pt else "UNRESOLVED",
                 "Co_global": "PASS" if pt else "UNRESOLVED"}
        r["faces"] = faces
        r["tri"] = tri_verdict(faces)
        local_ok = {"PASS": True, "FAIL": False}.get(r["A"])
        r["conj"] = conjunctive_verdict(local_ok, pt)
        changes += r["tri"] != r["conj"]

    trivial = [r for r in adm if r["abc"][0] == 1 and r["abc"][1] == 1]
    fail_primes = sorted({p for r in rows if r["A"] == "FAIL" for p in r["A_places"]})
    unres = [r for r in adm if r["point"] is None]
    summary = {
        "box_primary": len(rows),
        "A_PASS": len(adm),
        "A_FAIL": sum(r["A"] == "FAIL" for r in rows),
        "A_UNRESOLVED": sum(r["A"] == "UNRESOLVED" for r in rows),
        "trivial_family": len(trivial),
        "point_le_60": sum(r.get("found_at") == 60 for r in adm),
        "point_le_3000": sum(r.get("point") is not None for r in adm),
        "no_point_to_3000": len(unres),
        "failing_primes": fail_primes,
        "verdict_changes_tri_vs_conj": changes,
        "tri_verdicts": {v: sum(r["tri"] == v for r in rows) for v in ("PASS", "FAIL", "UNRESOLVED")},
        "descent_only_cases_unresolved": [r["abc"] for r in unres if r["abc"] in ([1, 25, 29], [19, 25, 29])],
        "secondary_box_gcd_only": sum(1 for _ in box(pairwise=False)),
        "secs": round(time.time() - t0, 1),
    }
    # Exact check of the record's two descent-found points
    rec = {"1,25,29": ((1, 25, 29), (820743421091604, -306235555265591, 178560217998019)),
           "19,25,29": ((19, 25, 29), (129, 9965, -9484))}
    summary["record_points_verify"] = {k: sum(c * v ** 3 for c, v in zip(*pq)) == 0 for k, pq in rec.items()}
    json.dump({"summary": summary, "rows": rows}, open(os.path.join(HERE, "cubic_faces_results.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
