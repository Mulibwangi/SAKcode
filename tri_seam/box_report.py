#!/usr/bin/env python3
"""Report the box-50 predictions X0-X7 (see PREREG_box50.md).

    python3 box_report.py [--ref ..]        # --ref: folder holding the box-30 results

Reads, from this folder: cubic_faces_results.json, descent_results.json (merged), sha_results.json,
dual_sha_results.json, rank_results.json (optional). From --ref: the same files for box 30, plus lfun_results.json.
Writes box_report.json.
"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(folder, name):
    p = os.path.join(folder, name)
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default=os.path.join(HERE, ".."))
    ap.add_argument("--old-bound", type=int, default=30)
    a = ap.parse_args()
    B = a.old_bound
    faces, desc = load(HERE, "cubic_faces_results.json"), load(HERE, "descent_results.json")
    sha, dual, rank = load(HERE, "sha_results.json"), load(HERE, "dual_sha_results.json"), load(HERE, "rank_results.json")
    rf, rd = load(a.ref, "cubic_faces_results.json"), load(a.ref, "descent_results.json")
    rs, rdu, rr = load(a.ref, "sha_results.json"), load(a.ref, "dual_sha_results.json"), load(a.ref, "rank_results.json")

    rows = faces["rows"]
    small = [r for r in rows if max(r["abc"]) <= B]
    cub = desc["cubics"]
    cub_small = [x for x in cub if max(x["abc"]) <= B]
    obs_small = {tuple(x["abc"]) for x in cub_small if x["descent"] == "obstructed"}
    ref_obs = None
    if rd:
        ref_obs = {tuple(x["abc"]) for x in rd["cubics"] if x["record"] == "obstructed"}
    shaD = {r["D"]: r for r in sha["curves"]}
    dualD = {r["D"]: r for r in dual["curves"]} if dual else {}
    rankD = {r["D"]: r for r in rank["results"] if r["label"].startswith("curve")} if rank else {}

    def cmp(ref, cur, key):
        if ref is None:
            return "reference missing"
        common = [D for D in ref if D in cur]
        bad = [D for D in common if str(ref[D].get(key)) != str(cur[D].get(key))]
        return {"compared": len(common), "mismatches": len(bad), "examples": bad[:10]}

    X0 = {
        "triples": len(small), "admissible": sum(r["A"] == "PASS" for r in small),
        "with_point": sum(r["A"] == "PASS" and r.get("point") is not None for r in small),
        "obstructed": len(obs_small),
        "obstructed_set_equal_to_box30": (obs_small == ref_obs) if ref_obs is not None else "reference missing",
        "sha_per_curve": cmp({r["D"]: r for r in rs["curves"]} if rs else None, shaD, "sha"),
        "dual_per_curve": cmp({r["D"]: r for r in rdu["curves"]} if rdu else None, dualD, "sha_hat"),
        "rank_per_curve": cmp({r["D"]: r for r in rr["results"] if r["label"].startswith("curve")} if rr else None,
                              rankD, "analytic_rank"),
    }
    adm = [x for x in cub]
    obstructed = [x for x in adm if x["descent"] == "obstructed"]
    sha_curves = [r for r in sha["curves"] if r["sha"]]
    nontriv = {r["D"] for r in sha_curves if r["sha"] >= 9}
    carriers = {x["D"] for x in obstructed}
    by_rank = {}
    for r in rankD.values():
        by_rank.setdefault(str(r["rank_alg"]), []).append(r)
    report = {
        "box_bound": faces["summary"].get("box_bound"), "triples": len(rows), "admissible": len(adm),
        "X0_nesting_box30": X0,
        "X1_point_but_obstructed": desc["summary"].get("point_but_descent_obstructed"),
        "X2_failing_primes": faces["summary"]["failing_primes"],
        "X2_as_predicted": faces["summary"]["failing_primes"] == [3, 7, 13, 19, 31, 37, 43],
        "X3_obstructed_share": round(len(obstructed) / len(adm), 4),
        "X3_counts": {"with_point": sum(x["point"] is not None for x in adm),
                      "solvable_by_descent_only": len(desc["summary"].get("no_point_descent_solvable", [])),
                      "obstructed": len(obstructed),
                      "unresolved": sum(x["descent"] == "UNRESOLVED" for x in adm)},
        "X4_sha_distribution": {str(k): sum(1 for r in sha_curves if r["sha"] == k)
                                for k in sorted({r["sha"] for r in sha_curves})},
        "X4_all_squares": all(r["sha_dim"] % 2 == 0 for r in sha_curves),
        "X4_dual_trivial": f"{sum(r.get('sha_hat') == '1' for r in dualD.values())}/{len(dualD)}" if dual else None,
        "X4_dual_nontrivial_D": sorted(D for D, r in dualD.items() if r.get("sha_hat") != "1")[:30],
        "X5_finite_sha_by_rank": {k: f"{sum(bool(r.get('finite_sha_proven')) for r in v)}/{len(v)}"
                                  for k, v in sorted(by_rank.items())},
        "X5_not_provable_D": sorted(D for D, r in rankD.items() if not r.get("finite_sha_proven"))[:40],
        "X6_nontrivial_curves": len(nontriv), "X6_carrier_curves": len(carriers),
        "X6_nontrivial_and_carrier": len(nontriv & carriers),
        "X6_nontrivial_not_carrier": len(nontriv - carriers), "X6_carrier_not_nontrivial": sorted(carriers - nontriv)[:20],
        "X7_decided_share": desc["summary"].get("decided_share"),
        "curves_still_undecided": desc["summary"].get("still_undecided_curves"),
    }
    json.dump(report, open(os.path.join(HERE, "box_report.json"), "w"), indent=1, default=str)
    print(json.dumps(report, indent=1, default=str))


if __name__ == "__main__":
    main()
