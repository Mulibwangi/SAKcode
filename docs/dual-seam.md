# The Dual Seam (CPMF)

## Where this starts

The shared covariant grammar (Feb 7 notes) makes **SEM superordinate**: SEM
(semantic ontology) is the base category `C_S`, and QM and GR are fibers over
it, reached by one-way lift functors

    F_Q  : C_S → C_Q        F_GR : C_S → C_GR

with the rule "u admissible in SEM ⟹ F_Q(u), F_GR(u) admissible."

## The insight: the seam is dual

CPMF is already dual at the operator layer: every transport `T : M_P → M_C`
has an adjoint `T† : M_C → M_P`, and meaning exists only when both residuals
`r_C = ‖C − T(P)‖` and `r_P = ‖P − T†(C)‖` are small.

The ontology seam has to obey the same law. A one-way lift is half a seam.
So each ontology must be worked toward the other two:

| Start | Lifts | Functors |
|-------|-------|----------|
| SEM | → QM + GR | `F_{S→Q}`, `F_{S→GR}` (existing) |
| QM  | → SEM + GR | `F_{Q→S}`, `F_{Q→GR}` (new) |
| GR  | → SEM + QM | `F_{GR→S}`, `F_{GR→Q}` (new) |

That's six directed lifts: three adjoint pairs.

## 1. Adjoint pairs (the duality)

For each pair of ontologies a, b ∈ {S, Q, GR}:

    F_{a→b} ⊣ F_{b→a}

with unit `η_a : id → F_{b→a} ∘ F_{a→b}` and counit
`ε_b : F_{a→b} ∘ F_{b→a} → id`.

Seam residuals, the T/T† closure law lifted to the ontology level:

    r_{a→b→a}(x_a) = ‖ F_{b→a} F_{a→b} x_a − x_a ‖_a
    r_{b→a→b}(x_b) = ‖ F_{a→b} F_{b→a} x_b − x_b ‖_b

**Dual-seam closure:** `r_{a→b→a}² + r_{b→a→b}² ≤ ϵ_seam` for all three pairs.

The descent maps should be what each fiber naturally "projects down" to:
- `F_{Q→S}`: coarse-graining / decoherence / measurement record → semantic field f
- `F_{GR→S}`: curvature invariants / causal structure → semantic field f
- `F_{Q→GR}`, `F_{GR→Q}`: the QM↔GR seam proper (e.g. stress-energy expectation
  ⟨T_μν⟩_ρ as Q→GR; QFT on a curved background as GR→Q)

## 2. Triangle coherence (holonomy round the seam)

With three ontologies, two routes connect each pair:

    F_{Q→GR} ∘ F_{S→Q}  ≅?  F_{S→GR}

Define the **seam holonomy** for each start point, e.g.

    Hol_seam(S) = ‖ F_{GR→S} F_{Q→GR} F_{S→Q} f − f ‖
    Hol_seam(S)' = the same loop traversed the other way (S→GR→Q→S)

and likewise from Q and from GR. Six loops, three per orientation. This
extends the existing SEM holonomy probe (refinement order) to ontology
order.

## 3. Consequence for SEM superordination

Duality challenges the one-way picture. There are two readings:

- **(A) Superordination survives.** SEM still owns the gate `Q = τασ·Π`, and
  the reverse lifts must land inside `Γ_τ`. Duality then works as a consistency
  check on SEM: if `F_{Q→S}` or `F_{GR→S}` lands outside admissibility, SEM is
  mis-specified.
- **(B) Superordination dissolves.** No ontology is the base. The seam itself
  (the system of adjunctions plus the triangle) is the base object, and SEM,
  QM and GR are three charts on it.

Which reading holds is an empirical question for the probes: (A) predicts the
residuals are asymmetric and smallest when starting from SEM; (B) predicts
they're symmetric.

## 4. Gate extension

Add the seam probes to Π:

    Π = exp(−λ_Db Db − λ_Hol Hol − λ_DPI DPI − λ_seam Σ r − λ_tri Σ Hol_seam)

## Duality check table

| Pair | Forward | Reverse | Round-trip residual | Notes |
|------|---------|---------|---------------------|-------|
| SEM ↔ QM | F_{S→Q} | F_{Q→S} | ? | |
| SEM ↔ GR | F_{S→GR} | F_{GR→S} | ? | |
| QM ↔ GR  | F_{Q→GR} | F_{GR→Q} | ? | the classical QG seam |

## Open questions
- Adjunction (⊣) or full equivalence? An adjunction allows information loss
  in one direction, which seems right for Q→S (decoherence loses phase).
- Does the triangle commute up to a natural isomorphism, or is non-zero seam
  holonomy itself the physical content (e.g. where gravity/quantum tension lives)?
