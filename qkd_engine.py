"""BB84 physics, round settings and bots for 'The Messenger Wisps' (session 3).

Story to science: a wisp is one photon. Its rune is the bit; its lens (Sun or Moon) is the measurement basis. A wrong lens
gives a random rune. Eve taps wisps with the intercept-resend attack: she measures with a lens of her choice and sends a fresh
wisp on to Bob. A storm flips Bob's result at random (honest noise). Everything here is plain Python so the game server
and the balance simulations run the same code.
"""
import random

SUN, MOON = 0, 1
PASS = -1                        # Eve lets a wisp go by
THRESHOLD = 0.11                 # asymptotic BB84 error bound; above it no secret can be distilled
SAMPLE_FRACTIONS = (0.25, 0.5, 0.75)
MIN_WISPS, MAX_WISPS_BOB, MAX_WISPS_ROOM = 8, 48, 32

# Solo as Bob: spy chance, share of wisps she taps, and storm noise per round. Rounds past the last repeat it.
BOB_ROUNDS = [
    dict(name="The Moor Road", spy=1.0, tap=1.0, storm=0.00,
         goal="A spy is on the road, and she taps every wisp. Compare a few bits and see what she leaves behind.",
         fact="An eavesdropper who measures with a random lens guesses the wrong one half the time, and a wrong lens scrambles the rune. "
              "Bob then disagrees with Alice on a quarter of the bits that survive sifting."),
    dict(name="The Quiet Pass", spy=0.0, tap=0.0, storm=0.00,
         goal="Nobody is listening this time. A clean line shows no errors at all.",
         fact="With no spy and no noise, Alice and Bob agree on every sifted bit. Any disagreement is a warning sign."),
    dict(name="The Weeping Fens", spy=0.5, tap=1.0, storm=0.02,
         goal="Mist adds honest mistakes. Is the spy there? She taps every wisp when she is.",
         fact="Real channels are noisy, so a few errors do not prove a spy. Past about 11% errors no secret can be made."),
    dict(name="The Ember Hills", spy=0.5, tap=0.75, storm=0.03,
         goal="She now taps three wisps in four. That is harder to see.",
         fact="If Eve taps a fraction f of the wisps she adds about f/4 errors, so a lighter touch is harder to spot but gives her less of the key."),
    dict(name="The Glass Marsh", spy=0.5, tap=0.5, storm=0.04,
         goal="Half the wisps tapped, and more storm. Check more bits.",
         fact="Checking more bits sharpens the test but shortens the key. Every sacrificed bit is a bit nobody will ever use."),
    dict(name="The Thundering Gap", spy=0.5, tap=0.5, storm=0.05,
         goal="The storm is loud now. Choose your wisps with care.",
         fact="Noise and spy produce the same symptom. A bigger sample is the only way to tell them apart."),
    dict(name="The Hollow Crown", spy=0.5, tap=0.4, storm=0.06,
         goal="A faint touch in a loud storm.",
         fact="The harder the spy hides in the noise, the more wisps it takes to catch her. That is why real QKD links send millions."),
    dict(name="The Last Light", spy=0.5, tap=0.35, storm=0.07,
         goal="The hardest road. How long can you last?",
         fact="From here every road is like this one. A short sample is a coin flip, a long one costs mana."),
]
MANA_START, MANA_PER_ROUND, MANA_CAP = 32, 24, 64

# Solo as Eve: Alice sends n wisps, then the towers compare a share of the sifted bits and abort when the sampled error rate is
# above their tolerance. Early towers are lenient (tol is high), later ones use the true 11% line.
EVE_ROUNDS = [
    dict(name="The Gatehouse", n=32, sample=0.25, storm=0.00, tol=0.25,
         goal="Tap a few wisps and stay quiet. The guards here barely check.",
         fact="Eve cannot copy a wisp (no cloning), so she must measure it, and a wrong lens leaves a mark on what she sends on."),
    dict(name="The Watch Tower", n=32, sample=0.25, storm=0.00, tol=0.20,
         goal="The guards check a little more.",
         fact="If Eve taps a share f of the wisps she adds about f/4 errors, and she learns about f/2 of the key."),
    dict(name="The Mist Bridge", n=40, sample=0.30, storm=0.02, tol=0.17,
         goal="Their own storm gives you cover.",
         fact="Noise is the spy's friend: honest errors use up part of the budget she could hide in."),
    dict(name="The Warded Hall", n=40, sample=0.40, storm=0.03, tol=0.14,
         goal="A bigger sample, and a stricter guard.",
         fact="Tapping every wisp gives Eve half the key, but it also makes the error rate 25%, far above any line."),
    dict(name="The Silver Court", n=48, sample=0.50, storm=0.04, tol=0.12,
         goal="The towers are listening carefully.",
         fact="The best tap rate depends on how big the sample is and how noisy the line is."),
    dict(name="The Moon Gate", n=48, sample=0.50, storm=0.05, tol=0.11,
         goal="Now they hold the true line: 11%.",
         fact="Above about 11% errors no secret key can be distilled from a BB84 exchange, however clever the towers are."),
    dict(name="The Crown Vault", n=48, sample=0.60, storm=0.06, tol=0.11,
         goal="Nearly the best defence they can build.",
         fact="Real systems send millions of wisps and tolerate no more than a few percent of errors."),
    dict(name="The Last Gate", n=48, sample=0.75, storm=0.07, tol=0.11,
         goal="The towers check three bits in four. How long can you last?",
         fact="From here every gate is like this one."),
]

ROOM_STORM = 0.03


def rng_new(seed=None):
    return random.Random(seed)


def prepare(rng, n):
    """Alice's runes and lenses, chosen at random (the spell of the coins)."""
    return [rng.randint(0, 1) for _ in range(n)], [rng.randint(0, 1) for _ in range(n)]


def eve_bot(rng, n, tap):
    """Bot Eve taps exactly round(tap * n) wisps, chosen at random, each with a random lens."""
    k = round(tap * n)
    pick = set(rng.sample(range(n), k)) if k else set()
    return [rng.randint(0, 1) if i in pick else PASS for i in range(n)]


def wisp_journey(a_bit, a_lens, e_choice, b_lens, storm, rng):
    """One wisp from Alice to Bob. Returns (eve_result, bob_result); eve_result is None when she let it pass."""
    in_bit, in_lens, e_res = a_bit, a_lens, None
    if e_choice != PASS:
        e_res = a_bit if e_choice == a_lens else rng.randint(0, 1)
        in_bit, in_lens = e_res, e_choice            # Eve resends what she saw, in her own lens
    b_res = in_bit if in_lens == b_lens else rng.randint(0, 1)
    if rng.random() < storm:
        b_res ^= 1
    return e_res, b_res


def run_channel(a_bits, a_lens, e_choice, b_lens, storm, rng):
    e_res, b_res = [], []
    for a, al, ec, bl in zip(a_bits, a_lens, e_choice, b_lens):
        e, b = wisp_journey(a, al, ec, bl, storm, rng)
        e_res.append(e)
        b_res.append(b)
    return e_res, b_res


def sift(a_lens, b_lens):
    return [i for i, (x, y) in enumerate(zip(a_lens, b_lens)) if x == y]


def pick_sample(rng, sifted, fraction):
    m = len(sifted)
    if m == 0:
        return []
    k = min(m, max(1, round(fraction * m)))
    return sorted(rng.sample(sifted, k))


def tally(a_bits, b_res, a_lens, e_choice, sifted, sample):
    """Everything the verdict and the result screen need, from the full secret state."""
    sset = set(sample)
    key = [i for i in sifted if i not in sset]
    errors = sum(a_bits[i] != b_res[i] for i in sample)
    qber = errors / len(sample) if sample else 0.0
    eve_known = [i for i in key if e_choice[i] != PASS and e_choice[i] == a_lens[i]]
    return dict(
        sifted=list(sifted), sample=list(sample), key=key, errors=errors, qber=qber,
        key_errors=sum(a_bits[i] != b_res[i] for i in key),
        eve_known=eve_known,
        tapped=sum(c != PASS for c in e_choice),
    )


def bot_verdict(t, tol=THRESHOLD):
    """Bots abort when the sampled error rate is above their tolerance, or when there is nothing to keep."""
    if not t["key"]:
        return "abort"
    return "abort" if t["qber"] > tol else "keep"


def outcome(verdict, t):
    if not t["key"] and verdict == "abort":
        return "no_key" if t["tapped"] == 0 else "caught"
    if verdict == "abort":
        return "caught" if t["tapped"] else "false_alarm"
    return "breach" if t["eve_known"] else "safe"


def points(oc, t):
    """(Alice and Bob each, Eve) points for one round."""
    if oc == "safe":
        return len(t["key"]), 0
    if oc == "breach":
        return len(t["key"]) - len(t["eve_known"]), len(t["eve_known"])
    if oc == "caught":
        return 6, 0
    return 0, 0
