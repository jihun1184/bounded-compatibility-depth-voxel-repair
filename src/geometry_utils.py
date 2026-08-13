"""
geometry_utils.py

Small geometry helpers used throughout this package: the 20-cell
vertex/edge neighborhood N(v) of a voxel, pairwise displacement
classification, translation, and the two canonical chain seeds.
"""
from itertools import product


def N(v):
    """
    N(v) := {g : v in candidate_voxels(g), dim(g) in {0,1}}.
    Always exactly 20 cells (8 dim-0 vertices + 12 dim-1 edges);
    translation-invariant (this is the geometric content behind the
    manuscript's Local Delta Lemma / Column Intersection Lemma).
    """
    result = set()
    # dim-0 cells: vertices g=2p with p_i in {v_i, v_i+1}
    for offs in product([0, 1], repeat=3):
        p = tuple(v[i] + offs[i] for i in range(3))
        result.add(tuple(2 * x for x in p))
    # dim-1 cells: for each free axis a, c_a=2*v[a]+1 fixed;
    # other two axes even, 2 choices each
    for a in range(3):
        other_axes = [i for i in range(3) if i != a]
        for offs in product([0, 1], repeat=2):
            g = [0, 0, 0]
            g[a] = 2 * v[a] + 1
            for idx, ax in enumerate(other_axes):
                g[ax] = 2 * (v[ax] + offs[idx])
            result.add(tuple(g))
    return result


def geom_type(u, w):
    """
    Classify the displacement u-w by the necessary condition that a
    nonzero candidate-voxel overlap requires ||u-w||_inf = 1. Returns
    (type, delta) where type in {"face","edge","corner","OUT_OF_RANGE"}:
      face   (2 zero coords)  -- raw |N(u) cap N(w)| = 8
      edge   (1 zero coord)   -- raw |N(u) cap N(w)| = 3
      corner (0 zero coords)  -- raw |N(u) cap N(w)| = 1
    "OUT_OF_RANGE" should never occur for a genuine overlapping pair;
    treat as a red flag, not a normal case.
    """
    d = tuple(u[i] - w[i] for i in range(3))
    cheb = max(abs(x) for x in d)
    if cheb != 1:
        return "OUT_OF_RANGE", d
    zeros = sum(1 for x in d if x == 0)
    if zeros == 2:
        return "face", d
    if zeros == 1:
        return "edge", d
    return "corner", d


def column(px, py, z_lo=-1, z_hi=0):
    """A length-(z_hi-z_lo+1) voxel column at fixed (px,py); default
    length 2 matches the SEED block's own column length."""
    return frozenset((px, py, z) for z in range(z_lo, z_hi + 1))


def shift(vs, d):
    """Translate a voxel set by integer offset d=(dx,dy,dz)."""
    return frozenset((x + d[0], y + d[1], z + d[2]) for (x, y, z) in vs)


# The two canonical seeds used to build the chain_L family (manuscript
# Section 3.1); SEED2 is the antidiagonal reflection of SEED.
SEED = frozenset([(-1, -1, -1), (-1, -1, 0), (0, 0, -1), (0, 0, 0)])
SEED2 = frozenset([(-1, 0, -1), (-1, 0, 0), (0, -1, -1), (0, -1, 0)])  # antidiagonal reflection of SEED
