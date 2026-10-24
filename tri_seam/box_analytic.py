#!/usr/bin/env python3
"""Close the curves mwrank left undecided with an analytic rank, then merge (see PREREG_box50.md, step 3).

    python3 box_analytic.py [--workers 8]

Reads descent_results.json and cubic_faces_results.json from this folder. On first run it saves the raw mwrank output as descent_raw.json.
  analytic rank 0                      -> rank 0, im delta = <[D]>
  analytic rank 1 and one mwrank gen   -> rank 1, im delta from that saturated generator
  otherwise                            -> stays undecided
Then re-evaluates every cubic and writes the merged descent_results.json plus analytic_results.json.
"""
import argparse
import json
import os
import shutil
import sys
import time
from fractions import Fraction
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rank_check as RC                                     # noqa: E402
from descent_check import DESCENT_ONLY, delta, in_image     # noqa: E402
from lfun_check import curve_info, eisenstein, n_max_for, sieve   # noqa: E402


def decided(c):
    return "error" not in c and c["certain"] and c["n_gens"] == c["rank"]


def evaluate_cubics(cubics, curves):
    out = []
    for r in cubics:
        aa, b, c = r["abc"]
        D = aa * b * c
        cv = curves[str(D)]
        pt = r.get("point") is not None
        rec = {"abc": r["abc"], "D": D, "record": "solvable" if (pt or r["abc"] in DESCENT_ONLY) else "obstructed"}
        if not decided(cv):
            rec.update(descent="UNRESOLVED", why=cv.get("error") or f"certain={cv['certain']} rank={cv['rank']} gens={cv['n_gens']}")
        else:
            deltas = [delta((Fraction(x), Fraction(y)), D) for x, y in cv["gens"]]
            hit, expo = in_image(Fraction(b, c), D, deltas)
            rec.update(descent="solvable" if hit else "obstructed", rank=cv["rank"], exponents=expo,
                       decided_by=cv.get("decided_by", "mwrank"))
        rec["agrees"] = rec["descent"] == rec["record"] if rec["descent"] != "UNRESOLVED" else None
        co_g = "PASS" if (pt or rec["descent"] == "solvable") else ("FAIL" if rec["descent"] == "obstructed" else "UNRESOLVED")
        rec["faces"] = {"A": "PASS", "L": "PASS" if pt else "UNRESOLVED", "Co_global": co_g}
        rec["tri"] = "FAIL" if co_g == "FAIL" else ("PASS" if pt else "UNRESOLVED")
        rec["point"] = r.get("point")
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    t0 = time.time()
    raw_path, cur_path = os.path.join(HERE, "descent_raw.json"), os.path.join(HERE, "descent_results.json")
    if not os.path.exists(raw_path):
        shutil.copy(cur_path, raw_path)
    raw = json.load(open(raw_path))
    curves = raw["curves"]
    undecided = sorted(int(D) for D, c in curves.items() if not decided(c))
    print(f"{len(undecided)} curves undecided by mwrank", flush=True)

    results = []
    if undecided:
        M = max(n_max_for(curve_info(16 * D * D)[2]) for D in undecided)
        P = sieve(M)
        P1 = P[P % 3 == 1]
        del P
        eis = [eisenstein(int(p)) for p in P1]
        RC.EIS = (P1, np.array([e[0] for e in eis], dtype=object), np.array([e[1] for e in eis], dtype=object),
                  np.array([e[2] for e in eis], dtype=object))
        del eis
        jobs = sorted(((f"undecided D={D}", D, None) for D in undecided), key=lambda j: -curve_info(16 * j[1] ** 2)[2])
        print(f"[{time.time() - t0:6.1f}s] coefficients to n = {M:,}", flush=True)
        with get_context("fork").Pool(min(a.workers, len(jobs))) as pool:
            results = list(pool.imap_unordered(RC.analyse, jobs, chunksize=1))

    closed, still = [], []
    for r in results:
        D = r["D"]
        c = dict(curves[str(D)])
        ok = r.get("fe_accepted") and r.get("two_t0_agree")
        ar = r.get("analytic_rank") if ok else None
        if ar == 0:
            c.update(rank=0, gens=[], n_gens=0, certain=True, decided_by="analytic rank 0")
            c.pop("error", None)
            closed.append(D)
        elif ar == 1 and "error" not in c and c["n_gens"] == 1:
            c.update(rank=1, certain=True, decided_by="analytic rank 1 + mwrank generator")
            closed.append(D)
        else:
            still.append({"D": D, "analytic_rank": ar, "mwrank": {k: c.get(k) for k in ("rank", "certain", "n_gens", "error")}})
        curves[str(D)] = c

    faces_rows = [r for r in json.load(open(os.path.join(HERE, "cubic_faces_results.json")))["rows"] if r["A"] == "PASS"]
    cubics = evaluate_cubics(faces_rows, curves)
    n = lambda f: sum(1 for x in cubics if f(x))                       # noqa: E731
    summary = dict(raw["summary"])
    summary.update({
        "analytic_closed_curves": closed, "still_undecided_curves": still,
        "decided_share": round(n(lambda x: x["descent"] != "UNRESOLVED") / len(cubics), 4),
        "solvable_with_point": n(lambda x: x["point"] is not None),
        "point_but_descent_obstructed": [x["abc"] for x in cubics if x["point"] is not None and x["descent"] == "obstructed"],
        "no_point_descent_solvable": [x["abc"] for x in cubics if x["point"] is None and x["descent"] == "solvable"],
        "obstructed": n(lambda x: x["descent"] == "obstructed"),
        "unresolved": n(lambda x: x["descent"] == "UNRESOLVED"),
        "tri_verdicts": {v: n(lambda x, v=v: x["tri"] == v) for v in ("PASS", "FAIL", "UNRESOLVED")},
        "box_analytic_secs": round(time.time() - t0, 1),
    })
    json.dump({"summary": summary, "curves": curves, "cubics": cubics}, open(cur_path, "w"), indent=1, default=str)
    json.dump({"results": results}, open(os.path.join(HERE, "analytic_results.json"), "w"), indent=1, default=str)
    print(json.dumps({k: summary[k] for k in ("analytic_closed_curves", "still_undecided_curves", "decided_share",
                                               "obstructed", "unresolved", "tri_verdicts")}, indent=1, default=str))


if __name__ == "__main__":
    main()
