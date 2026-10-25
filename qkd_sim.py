"""Balance simulations for 'The Messenger Wisps': bot players against the real Game. Run: python qkd_sim.py"""
import sys
import qkd_engine as E
from qkd_game import Game


def bob_policy(g, n, frac, detect_at):
    """A careful Bob: n wisps, random lenses, sample `frac`, abort when the sampled error rate exceeds `detect_at`."""
    g.act("bob", "set_n", dict(n=n))
    g.act("bob", "bob_lock", dict(lens=[g.rng.randint(0, 1) for _ in range(n)]))
    g.act("bob", "set_sample", dict(fraction=frac))
    v = g.view("bob")
    g.act("bob", "verdict", dict(choice="abort" if v["qber"] > detect_at or not v["sifted"] else "keep"))


def run_bob(policy, games=2000, seed=1):
    wins = [0] * 12
    reach = [0] * 12
    pts = 0
    for k in range(games):
        g = Game("bob", {"bob"}, seed=seed * 100003 + k)
        while g.alive and g.round < 12:
            if g.phase == "over":
                break
            reach[g.round] += 1
            n = policy["n"](g)
            if n is None:
                break
            bob_policy(g, n, policy["frac"], policy["detect"])
            if g.alive:
                wins[g.round] += 1
                g.act("bob", "next", {})
        pts += g.score
    return wins, reach, pts / games


def run_eve(tap, games=2000, seed=1, rounds=8):
    """Eve taps a fixed share every round; reports the share of runs surviving each round and the points per run."""
    surv = [0] * rounds
    pts = 0
    for k in range(games):
        g = Game("eve", {"eve"}, seed=seed * 100003 + k)
        while g.alive and g.round < rounds:
            n = g.n
            ch = E.eve_bot(g.rng, n, tap)
            g.act("eve", "eve_lock", dict(choice=ch))
            if g.alive:
                surv[g.round] += 1
                g.act("eve", "next", {})
        pts += g.score
    return [s / games for s in surv], pts / games


if __name__ == "__main__":
    print("Solo Bob, careful policy, mana spent on a fixed n per round (cap by mana)")
    for n0, frac, det in [(16, .5, .11), (24, .5, .11), (32, .5, .11), (32, .5, .15), (40, .5, .11)]:
        pol = dict(n=lambda g, n0=n0: min(n0, g.mana) if g.mana >= E.MIN_WISPS else None, frac=frac, detect=det)
        w, r, p = run_bob(pol)
        print(f"n={n0:2d} frac={frac} detect>{det:.2f}  survive per round:",
              " ".join(f"{w[i]/max(1,r[i]):.2f}" for i in range(8)), f" mean points {p:.1f}")
    print("\nSolo Eve, fixed tap rate")
    for tap in (0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0):
        s, p = run_eve(tap)
        print(f"tap={tap:4.2f} survive per round:", " ".join(f"{x:.2f}" for x in s), f" mean points {p:.1f}")
