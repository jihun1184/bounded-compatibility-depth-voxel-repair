# Reproducibility package

Code and reference data for the numeric claims in *"Bounded Compatibility
Depth in Local Repairs of P-Well-Composed Voxel Sets"* (submitted to
SIAM Journal on Imaging Sciences).

No external dependencies: Python ≥ 3.9 standard library only (see
`requirements.txt`).

## Quick start

```bash
cd scripts
python3 reproduce_depth_histogram.py       # <1s
python3 reproduce_bridge_lemma.py          # <1s
python3 reproduce_disjointness_L3_L5.py    # <5s
python3 reproduce_disjointness_L4.py       # <1s
python3 reproduce_section6_1_split.py      # <2s
python3 reproduce_walk_counts.py           # ~10 min (L=4 fresh brute force dominates)
```

Each script writes its output to `outputs/` as JSON and also prints a
human-readable summary to stdout. `MANIFEST.json` records a SHA-256
hash for every source file, script, and reference-result file in this
package, together with a table mapping each script to the specific
manuscript Table/Figure/Section it reproduces.

## What "fresh" vs. "stored" means here

Every script's docstring states explicitly which of the following applies,
and `MANIFEST.json`'s `claim_map` restates it in one place:

| Category | Meaning |
|---|---|
| **Fresh, this run** | The script performs the full enumeration or check itself, from the frozen oracle, when you run it. No prior computed answer is trusted. |
| **Stored + consistency-checked** | The script loads a previously computed result and verifies it (e.g., re-validates every element against the oracle, or re-aggregates raw per-instance records into the reported totals), but does not repeat the original combinatorial search. |

This distinction matters most for `reproduce_walk_counts.py`: the
`L=3` and `L=4` rows are freshly re-enumerated by brute force every
time you run it; the `L=5` row (`|M0(chain_5)|=324`) is loaded from
`reference_results/chain_L5_base_M0_reference.json` and only
consistency-checked, because a from-scratch brute force over its
candidate universe (`|U_5|=28`, `C(28,5)=98280` subsets to test at the
minimal size alone) is too expensive to run routinely. This is stated
in the script's own output, not just in this README.

Two results — the `L=4` row of Table 3 (decision-support disjointness)
and the Section 6.1 / Figure 4 worked example (27/9 split) — had **no
surviving generating script** anywhere in the project's working
history; only their recorded outcome was carried forward from an
earlier session. Both were independently re-derived from scratch for
this package (`reproduce_disjointness_L4.py`,
`reproduce_section6_1_split.py`) and matched the previously recorded
outcome exactly. This is noted explicitly in each script's docstring.

## Exhaustive vs. conditional-finite-family results

This distinction is a central scoping point of the manuscript itself
(see Section 3's "Scope remark" and Section 7), and is preserved here:

- **Exhaustive within the investigated setting**: the chain_5
  classification (`reproduce_depth_histogram.py`, 76 orbits / 528
  pairs, all Chebyshev-distance-2 isolated pairs at L=5) and the
  disjointness checks (`reproduce_disjointness_L3_L5.py`,
  `reproduce_disjointness_L4.py`, 21/21 instances across L=3,4,5) are
  complete enumerations over their stated finite candidate spaces —
  not samples.
- **Conditional theorem, finite-family applicability check**: Theorem
  5 (Bounded Compatibility Depth) is a conditional, deductive result —
  *if* the decision-support disjointness hypothesis holds, depth ≤ 3
  follows for any chain length, with no enumeration in the proof
  itself (see manuscript Section 4). The scripts in this package that
  touch disjointness are checking whether that *hypothesis* holds on
  the investigated L=3,4,5 families — they are applicability evidence
  for the theorem, not part of its proof, and they do **not**
  establish the hypothesis for arbitrary L. The manuscript states this
  explicitly (Section 5.2.1); this package does not extend that scope.
- Proposition 2 (the walk-bijection / prefix-count law used to explain
  `|M0(chain_L)|`) is likewise verified here only for L=3,4,5
  (`reproduce_walk_counts.py`); no code in this package claims a
  general-L result.

## Directory layout

```
reproducibility/
├── README.md                    (this file)
├── MANIFEST.json                (file hashes + script-to-claim map)
├── requirements.txt
├── src/                         frozen oracle + geometry/enumeration primitives
├── scripts/                     one script per manuscript claim, see MANIFEST.json
├── reference_results/           previously computed reference outputs, for comparison
└── outputs/                     scripts write their results here when you run them
```

## Correspondence to manuscript sections

| Script | Manuscript target |
|---|---|
| `reproduce_walk_counts.py` | Table 1, Proposition 2 |
| `reproduce_depth_histogram.py` | Table 2, Corollary 7 (sharpness) |
| `reproduce_bridge_lemma.py` | Lemma 3, Lemma 4 (consistency check) |
| `reproduce_disjointness_L3_L5.py` | Table 3 (L=3, L=5 rows), Section 5.2 |
| `reproduce_disjointness_L4.py` | Table 3 (L=4 row), Section 5.2 |
| `reproduce_section6_1_split.py` | Section 6.1, Figure 4 |

## License

MIT (see `LICENSE`), covering `src/`, `scripts/`, and `reference_results/`.
Please cite the accompanying manuscript when reusing this package.

## Citing

If you use this package, please cite the manuscript. An archival DOI
for this package will be added here upon acceptance.
