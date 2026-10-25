"""Shared physics model and game settings for the 'Keep the Magic Alive' page."""
import numpy as np

H_OVER_K = 4.799e-11            # h / k_B in K*s  (so h*f/(k_B*T) = H_OVER_K * f / T)
FIDELITY_LOST = 0.9             # the qubit counts as "lost" below this fidelity
X_LOST = 2 * FIDELITY_LOST - 1  # equivalent Bloch-vector length (0.8)

# ILLUSTRATIVE orders of magnitude, not vendor specifications.
# One "operation" = one typical gate slot on that platform.
PRESETS = {
    "Superconducting circuit": dict(
        kind="decoherence", T1=150e-6, T2=100e-6, t_gate=100e-9, eps=1e-3,
        f=5e9, T_ref=0.02, thermal=True, ops_per_turn=8, target_turns=40,
        blurb="Artificial atoms on a chip, cooled to ~20 mK. Very fast gates, but "
              "the qubit only lives for ~100 microseconds.",
        temp_note="Fridge temperature. Warmer means thermal photons and faster decay.",
    ),
    "Trapped ion": dict(
        kind="decoherence", T1=10.0, T2=1.0, t_gate=50e-6, eps=1e-4,
        f=12.6e9, T_ref=300.0, thermal=False, ops_per_turn=100, target_turns=40,
        blurb="Single atoms held by electric fields in vacuum. Extremely long-lived, "
              "but each gate takes a long time.",
        temp_note="Apparatus temperature. Heating shakes the ion and spoils its phase.",
    ),
    "Neutral atom": dict(
        kind="decoherence", T1=10.0, T2=1.0, t_gate=500e-9, eps=1e-3,
        f=6.8e9, T_ref=1e-5, thermal=False, ops_per_turn=14, target_turns=30,
        blurb="Atoms in arrays of laser tweezers. Long-lived and easy to scale up, "
              "but laser noise limits the gates.",
        temp_note="Atom temperature in the tweezer. Hotter atoms dephase faster.",
    ),
    "Photonic": dict(
        kind="loss", loss_dB=0.05, vis_err=2e-3, t_gate=1e-9, ops_per_turn=2, target_turns=22,
        blurb="Qubits carried by light. Photons barely interact with the environment, "
              "so they do not decohere - they get lost instead.",
        temp_note="Optical photons are not affected by room temperature at all.",
    ),
}

CODES = {
    "3-qubit repetition code (fixes dephasing only)": dict(
        n_phys=3, overhead=4, covers_all=False, upkeep=1),
    "9-qubit Shor code (fixes any single error)": dict(
        n_phys=9, overhead=12, covers_all=True, upkeep=3),
}

# Fantasy casting of each hardware platform (used by the game and the study tab).
CRAFTS = {
    "Superconducting circuit": dict(
        emoji="🧪", name="Frostbrewed Potion",
        accent=[142, 222, 255],
        step="Stir the cauldron", fail="The brew has spoiled.",
        win="The potion shimmers, perfectly brewed. Your frozen crypt held just long enough.",
        loseText="The colour drains away and the potion turns to sludge before the last stir.",
        tip="Real chips decohere in about a hundred microseconds. Cold and shielding buy time, but the energy leak (T1) cannot be mended by the Apprentice.",
        why="Brewed in a deep-frozen crypt, like a chip in a dilution fridge. Stirring is quick, "
            "but the brew spoils within moments if the cold slips.",
        wards="Cauldron insulation", chaos="Stray spirits and tremors", heat="Crypt temperature",
    ),
    "Trapped ion": dict(
        emoji="🔮", name="Ritual of the Bound Spirits",
        accent=[190, 160, 255],
        step="Chant a verse", fail="The binding has broken.",
        win="The spirits stay bound to the final verse. Slow chants, steady hands.",
        loseText="One by one the spirits slip their bonds and the circle goes dark.",
        tip="Trapped ions live for seconds, but each gate is slow. Their errors are mostly dephasing, which is exactly what error-correcting helpers repair best.",
        why="Each spirit is a single ion, held in place by invisible fields inside a sealed circle "
            "(vacuum chamber). The chants are slow, but the binding holds for a very long time.",
        wards="Sealed circle", chaos="Restless spirits", heat="Warmth of the chamber",
    ),
    "Neutral atom": dict(
        emoji="✨", name="Star-Weaving",
        accent=[255, 214, 120],
        step="Weave a thread", fail="The constellation has unravelled.",
        win="The stars hold their pattern. A flawless constellation.",
        loseText="The threads fray and the stars drift apart before the pattern is complete.",
        tip="Neutral atoms are long-lived, but flicker in the laser beams limits the gates. Error correction pays off handsomely here.",
        why="Beams of light pin stars into constellations, just as laser tweezers pin atoms into "
            "arrays. Easy to weave many stars at once, but any flicker in the beams spoils the pattern.",
        wards="Dark vault", chaos="Flickering beams", heat="Heat of the stars",
    ),
    "Photonic": dict(
        emoji="🕊️", name="Spell of Winged Light",
        accent=[196, 226, 255],
        step="Send it on", fail="The light has faded away.",
        win="The messenger of light arrives, bright and whole.",
        loseText="Spark by spark the light leaks away along the road.",
        tip="Photons barely decohere; they get lost. Polishing the lenses is the way to keep more light, and a simple helper cannot restore light that is gone.",
        why="A messenger of light flies fast and does not mind the heat, but a little of it leaks away "
            "at every stop. It never spoils, it only gets lost.",
        wards="Polished lenses", chaos="Wind and jitter", heat="Heat (no effect on light)",
    ),
}
ASSISTANTS = {
    "3-qubit repetition code (fixes dephasing only)": dict(emoji="🧙", name="Apprentice"),
    "9-qubit Shor code (fixes any single error)": dict(emoji="🧙‍♂️", name="Circle of Nine"),
}

# Game settings (turn-based rite).
GAME = dict(
    manaStart=8, manaCap=10, manaRegen=3,
    boostCost=2, boostSize=12,   # spend mana to move a gauge this far in the good direction
    limit=30,             # a gauge can be pushed at most this far from 'typical' (50 +/- 30)
    drift=0.12,           # each gauge relaxes this fraction of the way back to "typical" per step
    eventChance=0.5, eventSize=22,
    codeInterval=5,       # operations between error-correction rounds
)


def knob_factor(v):
    """Slider 0-100 -> factor 0.1x ... 10x, with 50 = the preset's typical lab."""
    return 10 ** ((v - 50) / 50)


def platform_model(p, iso, noise, temp):
    """Per-operation decay numbers for a preset and the three knob positions."""
    F_iso, F_noise, F_T = knob_factor(iso), knob_factor(noise), knob_factor(temp)
    if p["kind"] == "loss":
        d_loss = np.log(10) / 10 * p["loss_dB"] / F_iso      # lost photon, per component
        d_vis = p["vis_err"] * F_noise                      # phase jitter / imperfect interference
        return dict(d_relax=d_loss, d_phase=d_vis, rate1=0.0, z_eq=0.0, p_th=0.0,
                    T=None, T2=None, t_gate=p["t_gate"], kind="loss")
    G1 = 1 / p["T1"] * F_T / F_iso
    Gphi0 = max(1 / p["T2"] - 1 / (2 * p["T1"]), 0.05 / p["T2"])
    Gphi = Gphi0 * F_noise * F_T / F_iso
    eps = p["eps"] * F_noise
    T = p["T_ref"] * F_T
    p_th = 1 / (1 + np.exp(H_OVER_K * p["f"] / T)) if p["thermal"] else 0.0
    return dict(
        d_relax=p["t_gate"] * G1 / 2,                 # energy relaxation (T1) share
        d_phase=p["t_gate"] * Gphi + 4 * eps / 3,     # dephasing + control error share
        rate1=p["t_gate"] * G1,                       # z relaxes toward z_eq at this rate per op
        z_eq=1 - 2 * p_th, p_th=p_th, T=T, T2=1 / (G1 / 2 + Gphi),
        t_gate=p["t_gate"], kind="decoherence",
    )


def ops_until_lost(delta):
    return np.log(1 / X_LOST) / delta


def qec_cycle(m, k, code):
    """Return (per-cycle logical Bloch decay factor, logical flip probability) for the chosen code."""
    s = code["overhead"]
    if code["covers_all"]:
        delta_corr, delta_left, expo = m["d_relax"] + m["d_phase"], 0.0, 0
    else:
        delta_corr, delta_left, expo = m["d_phase"], m["d_relax"], code["n_phys"]
    p = (1 - np.exp(-(k + s) * delta_corr)) / 2           # flip probability per data qubit per cycle
    if code["covers_all"]:
        p_b = (1 - (1 - 2 * p) ** 3) / 2                  # phase flip of a whole 3-qubit block
        p_L = 3 * p_b**2 - 2 * p_b**3 + 9 * p**2
    else:
        p_L = 3 * p**2 - 2 * p**3
    p_L = min(p_L, 0.5)
    return (1 - 2 * p_L) * np.exp(-max(expo, 1) * (k + s) * delta_left), p_L


def rite_config():
    """Everything the JS game engine needs, as plain JSON-able data."""
    presets = {}
    for name, p in PRESETS.items():
        q = {k: v for k, v in p.items() if isinstance(v, (int, float, str, bool))}
        q["opsPerTurn"] = p["ops_per_turn"]
        q["targetTurns"] = p["target_turns"]
        presets[name] = q
    codes = {name: dict(c) for name, c in CODES.items()}
    return dict(
        presets=presets, codes=codes, game=GAME, fLost=FIDELITY_LOST, xLost=X_LOST,
        crafts=CRAFTS, assistants=ASSISTANTS,
    )
