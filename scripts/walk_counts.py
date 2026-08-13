"""
Reproduces manuscript Table 1: |M0(chain_L)| and m0 for L = 3, 4, 5.

Expected output:
    L=3: |U_3|=20, m0=3, |M0|=36
    L=4: |U_4|=24, m0=4, |M0|=108
    L=5: |U_5|=28, m0=5, |M0|=324  
"""
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from geometry_utils import SEED, shift  # noqa: E402
from repair_enumeration_core import universe_for  # noqa: E402
from stage2_repair_core import pwc_verdict  # noqa: E402

REF_DIR = os.path.join(os.path.dirname(__file__), "..", "reference_results")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def chain(length):
    obj = set(SEED)
    for k in range(1, length - 1):
        obj |= shift(SEED, (0, 0, k))
    return frozenset(obj)


def brute_force_M0(F0, universe, max_size):
    universe = sorted(universe)
    for size in range(0, max_size + 1):
        winners = []
        for combo in itertools.combinations(universe, size):
            Z = F0.symmetric_difference(combo)
            if pwc_verdict(Z):
                winners.append(sorted(combo))
        if winners:
            return size, winners
    return None, []


def run_fresh(L, max_size):
    F0 = chain(L)
    universe, defects = universe_for(F0)
    print(f"L={L}: |U_L|={len(universe)}  |Def|={len(defects)}")
    t0 = time.time()
    m0, M0 = brute_force_M0(F0, universe, max_size)
    print(f"L={L}: m0={m0}  |M0|={len(M0)}  (fresh brute force, {time.time()-t0:.1f}s)")
    return {"L": L, "universe_size": len(universe), "m0": m0, "M0_size": len(M0),
            "method": "fresh_brute_force"}


def run_stored_consistency_check(L, ref_file, expected_size):
    F0 = chain(L)
    data = json.load(open(ref_file))
    M0 = [frozenset(tuple(v) for v in B) for B in data["M0"]]
    ok = True
    for B in M0:
        Z = F0.symmetric_difference(B)
        if not pwc_verdict(Z):
            ok = False
            break
    consistent_size = (len(M0) == expected_size)
    print(f"L={L}: |M0| in stored reference = {len(M0)} "
          f"(expected {expected_size}, match={consistent_size}); "
          f"every stored element verified pwc-valid under this run's oracle = {ok} "
          f"(method: stored + consistency-checked, NOT freshly re-enumerated)")
    return {"L": L, "M0_size": len(M0), "expected_M0_size": expected_size,
            "all_elements_pwc_valid_this_run": ok, "method": "stored_plus_consistency_check"}


if __name__ == "__main__":
    results = []
    results.append(run_fresh(3, max_size=3))
    results.append(run_fresh(4, max_size=4))
    results.append(run_stored_consistency_check(
        5, os.path.join(REF_DIR, "chain_L5_base_M0_reference.json"), expected_size=324))

    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(results, open(os.path.join(OUT_DIR, "walk_counts_result.json"), "w"), indent=2)
    print("\nSaved outputs/walk_counts_result.json")
