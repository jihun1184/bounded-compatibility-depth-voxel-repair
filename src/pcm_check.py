"""
pcm_check.py

Faithful, recursive implementation of the poset-theoretic
P-well-composedness definitions of Boutry (2024), transcribed directly
from the manuscript's own Section 2 notation (not reconstructed from
OCR of the original PDF). Definitions implemented:

  - theta'_X(h): strict neighborhood (elements strictly comparable to h,
    above or below), §2.2.
  - is_surface(cells, rank): recursive discrete n-surface test, §2.3.
      rank -1: empty poset.
      rank  0: exactly two elements (no further condition; incomparability
               is automatic since both have the same dimension in every
               use here, but we assert it defensively).
      rank >0: connected, and every element's strict neighborhood is an
               (rank-1)-surface.
  - border_of(cells, rank) = Delta X: {h : |theta'_X(h)| is NOT an
    (rank-1)-surface}, §2.4 (Definition of border; this is the SAME
    operator used for both n-PCM's border and for PWC-ness, since both
    are phrased in terms of Delta X).
  - is_pcm(cells, rank): recursive n-PCM test, §2.4.
      rank -1: empty. rank 0: exactly one element. rank>0: connected,
      Delta X nonempty, and for every h: if h in Delta X then theta'(h)
      is an (rank-1)-PCM, else theta'(h) is an (rank-1)-surface.
      NOTE: this is the PLAIN n-PCM (Boutry 2024 Definition 23 / 2025
      Definition 3), NOT the smooth n-PCM (Definition 24/4). The plain
      version does not require Delta X itself to be surface-like as a
      whole -- only that each border element's OWN neighborhood is a
      (possibly non-smooth) (rank-1)-PCM.
  - is_pwc(cells, rank): Delta X is a disjoint union of connected
    components, each of which is an (rank-1)-surface (Definition 21).
    An empty border is treated as vacuously PWC (a discrete surface has
    empty border and is PWC, Boutry 2024 Prop. 6 / Remark 9 context).

All functions are memoized on (frozenset(cells), rank) so repeated
sub-poset checks inside a single top-level call are not recomputed.

IMPORTANT SCOPE NOTE: this module intentionally checks the exact
poset-theoretic definitions by brute-force recursion. It is NOT meant to
scale -- it exists to run small exhaustive searches (2D grids up to
about 3x3-4x4 pixels), not to replace the existing embedded 3D
checker (check_embedded_cubical_normality.py), which uses a much
faster single-level ridge-degree combinatorial shortcut proven
equivalent to (plain) cubical normality in the accompanying JMIV paper,
for rank>=2 -- but only tests the four cubical-normality conditions,
not PWC-ness or smoothness.
"""

from itertools import product

# ---------------------------------------------------------------------
# Cell geometry (doubled-coordinate convention, generalized to any
# dimension d; identical conventions to check_embedded_cubical_normality.py)
# ---------------------------------------------------------------------

def voxel_to_cell(v):
    """Integer voxel coordinate tuple -> doubled-coordinate top cell."""
    return tuple(2 * x + 1 for x in v)


def dim(cell):
    """Dimension of a cell = number of odd (free) coordinates."""
    return sum(1 for c in cell if c % 2 == 1)


def is_face(sub, sup):
    """True iff `sub` is a face of `sup` (sub == sup counts as a face)."""
    for s, S in zip(sub, sup):
        if S % 2 == 0:
            if s != S:
                return False
        else:
            if abs(s - S) > 1:
                return False
    return True


def closure(cell):
    """All faces of `cell`, including itself."""
    options = []
    for c in cell:
        if c % 2 == 1:
            options.append([c - 1, c, c + 1])
        else:
            options.append([c])
    return set(product(*options))


def build_complex(voxels):
    """
    voxels: iterable of integer coordinate tuples (top-cell / pixel
    coordinates, NOT doubled). Returns (top_cells, all_cells) as sets
    of doubled-coordinate cells.
    """
    top_cells = set(voxel_to_cell(v) for v in voxels)
    all_cells = set()
    for c in top_cells:
        all_cells |= closure(c)
    return top_cells, all_cells


# ---------------------------------------------------------------------
# Poset primitives (Section 2.2 of the manuscript)
# ---------------------------------------------------------------------

def strictly_comparable(a, b):
    """True iff a < b or b < a (a != b and one is a face of the other)."""
    if a == b:
        return False
    return is_face(a, b) or is_face(b, a)


def theta_prime(cells, h):
    """
    Strict neighborhood of h within the induced sub-poset `cells`:
    elements of `cells` strictly comparable to h (above or below).
    theta'_X(h) in the manuscript's Section 2.2/2.3 notation.
    """
    return frozenset(x for x in cells if x != h and strictly_comparable(x, h))


def connected_components(cells):
    """
    Connected components of the poset induced on `cells`, using strict
    comparability (covering-relation-closure, i.e. the usual comparability
    graph restricted to this cell set) as adjacency.
    Returns a list of frozensets.
    """
    cells = list(cells)
    parent = {c: c for c in cells}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    n = len(cells)
    for i in range(n):
        for j in range(i + 1, n):
            if strictly_comparable(cells[i], cells[j]):
                union(cells[i], cells[j])

    groups = {}
    for c in cells:
        groups.setdefault(find(c), []).append(c)
    return [frozenset(g) for g in groups.values()]


def is_connected(cells):
    if len(cells) <= 1:
        return True
    return len(connected_components(cells)) == 1


# ---------------------------------------------------------------------
# Recursive surface / PCM / PWC tests (Sections 2.3, 2.4)
# ---------------------------------------------------------------------

_surface_cache = {}
_pcm_cache = {}


def is_surface(cells, rank):
    """
    Discrete n-surface test (Sec. 2.3), n = `rank`.
    rank == -1: empty poset.
    rank ==  0: exactly two elements (the 0-sphere).
    rank  >  0: connected, and every element's strict neighborhood is
                an (rank-1)-surface.
    """
    cells = frozenset(cells)
    key = (cells, rank)
    if key in _surface_cache:
        return _surface_cache[key]

    if rank == -1:
        result = (len(cells) == 0)
    elif rank == 0:
        result = (len(cells) == 2)
    else:
        if not is_connected(cells):
            result = False
        else:
            result = all(
                is_surface(theta_prime(cells, h), rank - 1) for h in cells
            )
    _surface_cache[key] = result
    return result


def border_of(cells, rank):
    """
    Delta X = {h in cells : theta'_X(h) is NOT an (rank-1)-surface}.
    This is THE SAME border operator used both for n-PCM's recursive
    definition and for PWC-ness (Definition 19/21 identified in the
    manuscript's Sec. 2.4).
    """
    cells = frozenset(cells)
    return frozenset(
        h for h in cells if not is_surface(theta_prime(cells, h), rank - 1)
    )


def is_pcm(cells, rank):
    """
    Plain n-PCM test (Sec. 2.4). NOT the smooth n-PCM.
    rank == -1: empty. rank == 0: exactly one element.
    rank  >  0: connected, Delta X nonempty, and for every h:
                h in Delta X  => theta'(h) is an (rank-1)-PCM
                h not in Delta X => theta'(h) is an (rank-1)-surface
    """
    cells = frozenset(cells)
    key = (cells, rank)
    if key in _pcm_cache:
        return _pcm_cache[key]

    if rank == -1:
        result = (len(cells) == 0)
    elif rank == 0:
        result = (len(cells) == 1)
    else:
        if not is_connected(cells):
            result = False
        else:
            border = border_of(cells, rank)
            if not border:
                result = False
            else:
                ok = True
                for h in cells:
                    nb = theta_prime(cells, h)
                    if h in border:
                        if not is_pcm(nb, rank - 1):
                            ok = False
                            break
                    else:
                        if not is_surface(nb, rank - 1):
                            ok = False
                            break
                result = ok
    _pcm_cache[key] = result
    return result


def is_pwc(cells, rank):
    """
    P-well-composedness test (Definition 21): Delta X is a disjoint
    union of connected components, each an (rank-1)-surface.
    Empty border => vacuously PWC.
    """
    cells = frozenset(cells)
    border = border_of(cells, rank)
    if not border:
        return True, []
    components = connected_components(border)
    verdicts = [is_surface(comp, rank - 1) for comp in components]
    return all(verdicts), list(zip(components, verdicts))


# ---------------------------------------------------------------------
# Facet-adjacency connectivity of the TOP CELLS ONLY (the notion used
# by the JMIV submission's cubical-normality theorem), as distinct from
# is_connected(all_cells) (poset connectivity of the WHOLE face poset).
# ---------------------------------------------------------------------

def facet_adjacency_components(top_cells, rank):
    """
    Union-find over top_cells using shared codimension-1 faces
    (facets) as adjacency. Returns list of frozensets of top cells.
    """
    facet_parents = {}
    for c in top_cells:
        for f in closure(c):
            if dim(f) == rank - 1:
                facet_parents.setdefault(f, []).append(c)

    parent = {c: c for c in top_cells}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for f, parents in facet_parents.items():
        if len(parents) == 2:
            union(parents[0], parents[1])

    groups = {}
    for c in top_cells:
        groups.setdefault(find(c), []).append(c)
    return [frozenset(g) for g in groups.values()], facet_parents
