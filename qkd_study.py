"""Teaching helpers for the 'Study the craft' tab of The Messenger Wisps: error correction and privacy amplification, worked on a
key like the one the player just made. Pure Python, no Streamlit, so the steps can be tested."""
import random


def demo_key(seed=7, length=16, errors=2, known=3):
    """A stand-in key for players who have not finished a round yet."""
    r = random.Random(seed)
    a = [r.randint(0, 1) for _ in range(length)]
    b = list(a)
    for i in r.sample(range(length), errors):
        b[i] ^= 1
    return a, b, sorted(r.sample(range(length), known))


def parity(bits):
    return sum(bits) & 1


def cascade_trace(a, b, block=4):
    """One pass of parity-based error correction (the first pass of Cascade).

    Alice and Bob compare the parity of each block aloud. When a block disagrees, they halve it again and again until the
    faulty bit is found, and Bob flips it. Every parity spoken aloud is a bit Eve hears too. Returns a list of steps.
    """
    b = list(b)
    leaked = 0
    steps = [dict(text="Alice and Bob each hold the same-length key, but a few of Bob's bits were flipped by the storm. "
                       "They cannot compare the whole key aloud, because Eve would hear it.",
                  b=list(b), leaked=0, marks={}, fixed=[])]
    fixed = []
    for start in range(0, len(a), block):
        idx = list(range(start, min(start + block, len(a))))
        pa, pb = parity([a[i] for i in idx]), parity([b[i] for i in idx])
        leaked += 1
        tag = "block %d" % (start // block + 1)
        if pa == pb:
            steps.append(dict(text="%s: the parities match (both %d). Nothing to fix, as far as one parity can tell." % (tag.capitalize(), pa),
                              b=list(b), leaked=leaked, marks={i: "ok" for i in idx}, fixed=list(fixed)))
            continue
        steps.append(dict(text="%s: Alice's parity is %d and Bob's is %d. An odd number of bits differ here, so they hunt for one." % (tag.capitalize(), pa, pb),
                          b=list(b), leaked=leaked, marks={i: "bad" for i in idx}, fixed=list(fixed)))
        lo = idx
        while len(lo) > 1:
            half = lo[:len(lo) // 2]
            ha, hb = parity([a[i] for i in half]), parity([b[i] for i in half])
            leaked += 1
            if ha != hb:
                lo = half
                where = "first half"
            else:
                lo = lo[len(half):]
                where = "second half"
            steps.append(dict(text="They compare the parity of the half: it disagrees in the %s, so the fault is there." % where,
                              b=list(b), leaked=leaked, marks={i: "bad" for i in lo}, fixed=list(fixed)))
        i = lo[0]
        b[i] ^= 1
        fixed.append(i)
        steps.append(dict(text="One bit left: bit %d. Bob flips it." % (i + 1), b=list(b), leaked=leaked, marks={i: "fix"}, fixed=list(fixed)))
    left = [i for i in range(len(a)) if a[i] != b[i]]
    steps.append(dict(text=("The two keys now agree." if not left else
                            "%d bit(s) still differ. A block with two errors has an even parity and slips through; real protocols "
                            "reshuffle the key and repeat the pass until none are left." % len(left)) +
                           " They spoke %d parity bits aloud, so the key is now %d bits shorter in secrecy." % (leaked, leaked),
                      b=list(b), leaked=leaked, marks={}, fixed=list(fixed)))
    return steps


def gf2_rank(rows):
    """Rank of a binary matrix given as a list of integer bitmasks."""
    rows = [r for r in rows if r]
    rank = 0
    while rows:
        pivot = rows.pop()
        if pivot == 0:
            continue
        rank += 1
        low = pivot & -pivot
        rows = [r ^ pivot if r & low else r for r in rows]
        rows = [r for r in rows if r]
    return rank


def hash_matrix(length, out, seed=11):
    """`out` random subsets of the key positions; each output bit is the XOR (parity) of its subset."""
    r = random.Random(seed)
    rows = []
    for _ in range(out):
        m = 0
        while m == 0:
            m = r.getrandbits(length)
        rows.append(m)
    return rows


def amplify(key, rows):
    return [bin(sum(1 << i for i, k in enumerate(key) if k) & m).count("1") & 1 for m in rows]


def eve_uncertainty(rows, length, known):
    """How many of the output bits Eve cannot determine from the key bits she holds.

    Treat her known bits as fixed. What she cannot pin down is the part of each output bit that depends on the unknown bits,
    so her uncertainty is the rank of the matrix restricted to those unknown columns.
    """
    mask = 0
    for i in range(length):
        if i not in set(known):
            mask |= 1 << i
    return gf2_rank([r & mask for r in rows])
