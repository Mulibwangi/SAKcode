#!/usr/bin/env python3
"""Tri-seam constructed cases K1-K3 (see PREREG.md), plus one passing control per case.

    python3 constructed_cases.py        # writes constructed_cases_results.json

Status: CONSTRUCTED. These pass by construction and show that the face checks match their definitions.
They are not evidence about the world.

A seam instance declares:
  items        source objects, each with a referent id and a value
  forward      F: source item -> target record
  recover      B: target record -> source item
  registry     independent witness: source referent id -> the target referent id it must map to
  relations    declared binary relations on source values that the target must preserve
  cover        optional: charts, overlaps and transition elements in Z_n (for joint compatibility)
"""
import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PASS, FAIL, UNRES = "PASS", "FAIL", "UNRESOLVED"


# ------------------------------------------------------------------ faces
def face_A(inst):
    """Admissibility: every crossing keeps the referent that the independent registry declares."""
    bad, missing = [], []
    for p in inst["items"]:
        want = inst["registry"].get(p["ref"])
        if want is None:
            missing.append(p["ref"])
        elif inst["forward"](p)["ref"] != want:
            bad.append(p["ref"])
    if bad:
        return FAIL, {"wrong_referent": bad}
    return (UNRES, {"no_registry_entry": missing}) if missing else (PASS, {})


def face_L(inst):
    """Lawful closure: B(F(p)) == p for every declared item."""
    bad = [p["ref"] for p in inst["items"] if inst["recover"](inst["forward"](p)) != p]
    return (FAIL, {"no_return": bad}) if bad else (PASS, {})


def co_local(inst):
    """Each declared constraint holds on its own: relation pairs, or each chart overlap separately."""
    if "cover" in inst:
        n, cov = inst["cover"]["n"], inst["cover"]
        bad = []
        for (i, j), g in cov["transitions"].items():                       # s_i = s_j + g (mod n)
            if not any((si - sj - g) % n == 0 for si in range(n) for sj in range(n)):
                bad.append([i, j])
        return (FAIL, {"unsatisfiable_overlaps": bad}) if bad else (PASS, {})
    bad = []
    for name, rel in inst["relations"].items():
        for p, q in itertools.permutations(inst["items"], 2):
            if rel(p["value"], q["value"]) and not rel(inst["forward"](p)["value"], inst["forward"](q)["value"]):
                bad.append([name, p["ref"], q["ref"]])
    return (FAIL, {"relation_violations": len(bad), "example": bad[:3]}) if bad else (PASS, {})


def co_global(inst):
    """Joint compatibility: one global assignment satisfies every constraint at once."""
    if "cover" in inst:
        n, cov = inst["cover"]["n"], inst["cover"]
        charts = cov["charts"]
        sols = [s for s in itertools.product(range(n), repeat=len(charts))
                if all((s[charts.index(i)] - s[charts.index(j)] - g) % n == 0 for (i, j), g in cov["transitions"].items())]
        obstruction = sum(cov["transitions"].values()) % n                  # cocycle class around the triangle
        info = {"global_sections": len(sols), "obstruction_class": obstruction}
        return (PASS, info) if sols else (FAIL, info)
    # Without a cover there is one chart, so joint compatibility is the conjunction of the local constraints
    return co_local(inst)


def tri_seam(inst):
    faces = {"A": face_A(inst), "L": face_L(inst), "Co_local": co_local(inst), "Co_global": co_global(inst)}
    v = [f[0] for f in faces.values()]
    verdict = FAIL if FAIL in v else (PASS if all(x == PASS for x in v) else UNRES)
    return verdict, {k: {"status": s, **d} for k, (s, d) in faces.items()}, [k for k, (s, _) in faces.items() if s == FAIL]


def conjunctive(inst):
    """Separate code path: one predicate over the same witnesses. Returns a verdict and nothing else."""
    ok_ref = all(inst["registry"].get(p["ref"]) == inst["forward"](p)["ref"] for p in inst["items"])
    ok_ret = all(inst["recover"](inst["forward"](p)) == p for p in inst["items"])
    if "cover" in inst:
        n, cov = inst["cover"]["n"], inst["cover"]
        ch = cov["charts"]
        ok_co = any(all((s[ch.index(i)] - s[ch.index(j)] - g) % n == 0 for (i, j), g in cov["transitions"].items())
                    for s in itertools.product(range(n), repeat=len(ch)))
    else:
        ok_co = all(not rel(p["value"], q["value"]) or rel(inst["forward"](p)["value"], inst["forward"](q)["value"])
                    for rel in inst["relations"].values() for p, q in itertools.permutations(inst["items"], 2))
    return PASS if (ok_ref and ok_ret and ok_co) else FAIL


# ------------------------------------------------------------------ cases
def items(n):
    return [{"ref": f"p{i}", "value": i} for i in range(n)]


def relabel(perm, refmap=None):
    """Forward map sending value v -> perm[v]; target referent from refmap (default: the declared one)."""
    inv = {b: a for a, b in enumerate(perm)}
    unref = {v: k for k, v in (refmap or {}).items()}
    fwd = lambda p: {"ref": (refmap or {}).get(p["ref"], "t" + p["ref"][1:]), "value": perm[p["value"]]}   # noqa: E731
    rec = lambda c: {"ref": unref.get(c["ref"], "p" + c["ref"][1:]), "value": inv[c["value"]]}           # noqa: E731
    return fwd, rec


def case_K1():
    """Exact round trip through a non-monotone permutation: order is not preserved."""
    fwd, rec = relabel([3, 0, 5, 1, 4, 2])
    return {"items": items(6), "forward": fwd, "recover": rec,
            "registry": {f"p{i}": f"t{i}" for i in range(6)}, "relations": {"<": lambda a, b: a < b}}


def control_K1():
    fwd, rec = relabel([0, 1, 2, 3, 4, 5])
    return {**case_K1(), "forward": fwd, "recover": rec}


def case_K2(transitions=None):
    """Three charts on a triangle with Z_3 transition elements; each overlap is satisfiable on its own,
    but g12 + g23 + g31 = 2 (mod 3) != 0, so no global section exists."""
    fwd, rec = relabel([0, 1, 2])
    return {"items": items(3), "forward": fwd, "recover": rec,
            "registry": {f"p{i}": f"t{i}" for i in range(3)}, "relations": {},
            "cover": {"n": 3, "charts": [1, 2, 3],
                      "transitions": transitions or {(1, 2): 1, (2, 3): 1, (3, 1): 0}}}


def control_K2():
    return case_K2({(1, 2): 1, (2, 3): 1, (3, 1): 1})                      # sum 3 = 0 (mod 3): glues


def case_K3():
    """Proxy that keeps values, order and an exact round trip, but swaps two referent ids."""
    fwd, rec = relabel([0, 1, 2, 3], refmap={"p0": "t1", "p1": "t0", "p2": "t2", "p3": "t3"})
    return {"items": items(4), "forward": fwd, "recover": rec,
            "registry": {f"p{i}": f"t{i}" for i in range(4)}, "relations": {"<": lambda a, b: a < b}}


def control_K3():
    fwd, rec = relabel([0, 1, 2, 3])
    return {**case_K3(), "forward": fwd, "recover": rec}


# Preregistered predictions (PREREG.md). Controls were added afterwards and are labelled as such.
PRED = {
    "K1": {"A": PASS, "L": PASS, "Co": FAIL},
    "K2": {"Co_local": PASS, "Co_global": FAIL},
    "K3": {"A": FAIL, "L": PASS, "Co": PASS},
}


def co(faces):
    s = [faces["Co_local"]["status"], faces["Co_global"]["status"]]
    return FAIL if FAIL in s else (PASS if all(x == PASS for x in s) else UNRES)


def main():
    cases = {"K1": case_K1(), "K2": case_K2(), "K3": case_K3(),
             "K1_control": control_K1(), "K2_control": control_K2(), "K3_control": control_K3()}
    out, all_ok = {}, True
    for name, inst in cases.items():
        verdict, faces, failing = tri_seam(inst)
        conj = conjunctive(inst)
        rec = {"tri_verdict": verdict, "conjunctive_verdict": conj, "failing_faces": failing, "faces": faces}
        if name in PRED:
            got = {k: (co(faces) if k == "Co" else faces[k]["status"]) for k in PRED[name]}
            rec["prediction"] = PRED[name]
            rec["prediction_held"] = got == PRED[name] and conj == FAIL and verdict == FAIL
        else:
            rec["prediction"] = "control (added after preregistration): expect all faces PASS"
            rec["prediction_held"] = verdict == PASS and conj == PASS
        rec["verdicts_agree"] = verdict == conj
        all_ok &= rec["prediction_held"] and rec["verdicts_agree"]
        out[name] = rec
        print(f"{name:11s} tri={verdict:5s} conj={conj:5s} failing={failing or '-'}  held={rec['prediction_held']}")
    out["all_held"] = all_ok
    json.dump(out, open(os.path.join(HERE, "constructed_cases_results.json"), "w"), indent=1, default=str)
    print("all predictions held:", all_ok)


if __name__ == "__main__":
    main()
