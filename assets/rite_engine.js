// Game engine for "Keep the Magic Alive". Pure logic, no DOM, so it can be tested in Node.
// Physics mirrors pages/2_Keep_the_Magic_Alive.py (platform_model, qec_cycle); all numbers come from CFG.
function makeEngine(CFG) {
  const G = CFG.game;

  const knobFactor = v => Math.pow(10, (v - 50) / 50);

  // Per-operation decay numbers for a platform and the three knob positions (wards = isolation).
  function platformModel(key, wards, chaos, heat) {
    const p = CFG.presets[key];
    const Fi = knobFactor(wards), Fn = knobFactor(chaos), Ft = knobFactor(heat);
    if (p.kind === 'loss') {
      return { dRelax: Math.LN10 / 10 * p.loss_dB / Fi, dPhase: p.vis_err * Fn };
    }
    const G1 = 1 / p.T1 * Ft / Fi;
    const Gphi0 = Math.max(1 / p.T2 - 1 / (2 * p.T1), 0.05 / p.T2);
    const Gphi = Gphi0 * Fn * Ft / Fi;
    const eps = p.eps * Fn;
    return { dRelax: p.t_gate * G1 / 2, dPhase: p.t_gate * Gphi + 4 * eps / 3 };
  }

  // Error-correction code: Bloch-vector factor per correction cycle.
  function qecCycle(m, codeKey, k) {
    const code = CFG.codes[codeKey], s = code.overhead;
    let dCorr, dLeft, expo;
    if (code.covers_all) { dCorr = m.dRelax + m.dPhase; dLeft = 0; expo = 0; }
    else { dCorr = m.dPhase; dLeft = m.dRelax; expo = code.n_phys; }
    const p = (1 - Math.exp(-(k + s) * dCorr)) / 2;
    let pL;
    if (code.covers_all) {
      const pb = (1 - Math.pow(1 - 2 * p, 3)) / 2;
      pL = 3 * pb * pb - 2 * pb * pb * pb + 9 * p * p;
    } else {
      pL = 3 * p * p - 2 * p * p * p;
    }
    pL = Math.min(pL, 0.5);
    const xCycle = (1 - 2 * pL) * Math.exp(-Math.max(expo, 1) * (k + s) * dLeft);
    return { xCycle, pL, lnPerOp: xCycle > 0 ? Math.log(xCycle) / k : -Infinity };
  }

  // Fading rate per operation (natural-log units of the Bloch vector) for the current state.
  function rates(st) {
    const m = platformModel(st.craft, st.wards, st.chaos, st.heat);
    const plain = m.dRelax + m.dPhase;
    let withCode = null;
    if (st.assistant !== 'none') {
      const q = qecCycle(m, st.assistant, G.codeInterval);
      withCode = -q.lnPerOp;                 // may be Infinity
    }
    const used = withCode === null ? plain : withCode;
    return { plain, withCode, used, helping: withCode !== null && withCode < plain };
  }

  // Operations a craft survives with nobody tending it, at typical conditions (50/50/50).
  function untendedOps(key) {
    const m = platformModel(key, 50, 50, 50);
    return Math.log(1 / CFG.xLost) / (m.dRelax + m.dPhase);
  }

  function rng(st) {                          // mulberry32, state kept in the game state
    st.seed = (st.seed + 0x6D2B79F5) | 0;
    let t = Math.imul(st.seed ^ (st.seed >>> 15), 1 | st.seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  function newGame(craft, seed) {
    const st = {
      craft, seed: (seed === undefined ? Date.now() : seed) | 0,
      turn: 0, ops: 0, essence: 1, mana: G.manaStart,
      wards: 50, chaos: 50, heat: 50, assistant: 'none',
      status: 'playing', log: [], lastEvent: null, wasHelping: 0, turnsHelped: 0,
    };
    return st;
  }

  const heatInert = st => CFG.presets[st.craft].kind === 'loss';
  const canAssist = st => CFG.presets[st.craft].kind !== 'loss';

  // Player actions. Returns {ok, msg}.
  function act(st, action) {
    if (st.status !== 'playing') return { ok: false, msg: 'The rite is over.' };
    if (action === 'wards' || action === 'chaos' || action === 'heat') {
      if (action === 'heat' && heatInert(st)) return { ok: false, msg: 'Light does not care about heat.' };
      if (st.mana < G.boostCost) return { ok: false, msg: 'Not enough mana.' };
      st.mana -= G.boostCost;
      if (action === 'wards') st.wards = Math.min(50 + G.limit, st.wards + G.boostSize);
      else st[action] = Math.max(50 - G.limit, st[action] - G.boostSize);
      return { ok: true };
    }
    if (action.startsWith('assist:')) {
      const which = action.slice(7);
      if (which !== 'none' && !canAssist(st)) return { ok: false, msg: 'Lost light cannot be mended by helpers.' };
      st.assistant = which;
      return { ok: true };
    }
    return { ok: false, msg: 'Unknown action.' };
  }

  // Continuous version of a boost, for dragging a gauge. Everything is recomputed from where the drag began
  // (baseVal, baseMana), so dragging back refunds the mana. Returns the units actually applied.
  function boostTo(st, which, baseVal, baseMana, units) {
    if (which === 'heat' && heatInert(st)) return 0;
    const room = which === 'wards' ? 50 + G.limit - baseVal : baseVal - (50 - G.limit);
    const affordable = baseMana * G.boostSize / G.boostCost;
    const u = Math.max(0, Math.min(units, room, affordable));
    st[which] = which === 'wards' ? baseVal + u : baseVal - u;
    st.mana = baseMana - u * G.boostCost / G.boostSize;
    return u;
  }

  // Perform one step of the rite (G.opsPerTurn[craft] operations), then let the world move on.
  function nextTurn(st) {
    if (st.status !== 'playing') return st;
    const B = CFG.presets[st.craft].opsPerTurn;
    const notes = [];
    // upkeep
    if (st.assistant !== 'none') {
      const up = CFG.codes[st.assistant].upkeep;
      if (st.mana >= up) st.mana -= up;
      else { notes.push('Your helper collapses from exhaustion and leaves.'); st.assistant = 'none'; }
    }
    // the step itself
    const r = rates(st);
    st.essence *= Math.exp(-B * r.used);
    if (!(st.essence > 0)) st.essence = 0;
    if (r.helping) st.turnsHelped++;
    st.ops += B; st.turn++;
    const F = (1 + st.essence) / 2;
    if (F < CFG.fLost) { st.status = 'lost'; return Object.assign(st, { lastNotes: notes }); }
    if (st.turn >= (CFG.presets[st.craft].targetTurns || G.targetTurns)) { st.status = 'won'; return Object.assign(st, { lastNotes: notes }); }
    // the world moves on: drift toward typical, random event, mana regen
    st.wards += (50 - st.wards) * G.drift;
    st.chaos += (50 - st.chaos) * G.drift;
    st.heat += (50 - st.heat) * G.drift;
    st.lastEvent = null;
    if (rng(st) < G.eventChance) {
      const kinds = [['chaos', 3], ['heat', 3], ['wards', 3], ['calm', 1]];
      let pool = kinds.filter(k => !(k[0] === 'heat' && heatInert(st)));
      const total = pool.reduce((a, k) => a + k[1], 0);
      let x = rng(st) * total, pick = pool[0][0];
      for (const k of pool) { if ((x -= k[1]) < 0) { pick = k[0]; break; } }
      const j = G.eventSize;
      if (pick === 'chaos') st.chaos = Math.min(100, st.chaos + j);
      else if (pick === 'heat') st.heat = Math.min(100, st.heat + j);
      else if (pick === 'wards') st.wards = Math.max(0, st.wards - j);
      else st.chaos = Math.max(0, st.chaos - j / 2);
      st.lastEvent = pick;
    }
    st.mana = Math.min(G.manaCap, st.mana + G.manaRegen);
    st.lastNotes = notes;
    return st;
  }

  return { knobFactor, platformModel, qecCycle, rates, untendedOps, newGame, act, boostTo, nextTurn };
}

if (typeof module !== 'undefined') module.exports = { makeEngine };
