// Engine for "The Gates of Kvantyus" (session 4, quantum machine learning). Pure logic, no DOM, so it can be tested in Node.
// The sentinel is a variational quantum classifier on n qubits (one per feature the player chose):
//   2 layers of [ RY(x_i) data upload, then trainable RY(a_i) RZ(b_i) on every qubit, then a ring of CZ ],
//   verdict = average of <Z_i> over all qubits + a trainable bias (>= 0 means friend).
// Mirrors session4/qml.py (checked to machine precision). Features are angles in [0, pi].
const GATE = (function () {
  const LAYERS = 2;
  const FEATURES = ['skin', 'hair', 'ears', 'horns', 'glow', 'strength'];

  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function gauss(rnd) { return Math.sqrt(-2 * Math.log(1 - rnd())) * Math.cos(2 * Math.PI * rnd()); }
  function hash(str) { let h = 2166136261; for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }

  const nParams = n => 2 * n * LAYERS + 1;

  // Single-qubit gates on qubit q of an n-qubit state (qubit 0 is the most significant bit, as in the numpy code).
  function ry(re, im, q, n, a) {
    const c = Math.cos(a / 2), s = Math.sin(a / 2), bit = 1 << (n - 1 - q);
    for (let i = 0; i < re.length; i++) if (!(i & bit)) {
      const j = i | bit, r0 = re[i], i0 = im[i], r1 = re[j], i1 = im[j];
      re[i] = c * r0 - s * r1; im[i] = c * i0 - s * i1;
      re[j] = s * r0 + c * r1; im[j] = s * i0 + c * i1;
    }
  }
  function rz(re, im, q, n, a) {
    const c = Math.cos(a / 2), s = Math.sin(a / 2), bit = 1 << (n - 1 - q);
    for (let i = 0; i < re.length; i++) {
      const sg = (i & bit) ? s : -s;               // multiply by e^{-i a/2} (bit 0) or e^{+i a/2} (bit 1)
      const r = re[i], m = im[i];
      re[i] = c * r - sg * m; im[i] = c * m + sg * r;
    }
  }
  function cz(re, im, a, b, n) {
    const ba = 1 << (n - 1 - a), bb = 1 << (n - 1 - b);
    for (let i = 0; i < re.length; i++) if ((i & ba) && (i & bb)) { re[i] = -re[i]; im[i] = -im[i]; }
  }

  // Sentinel's raw verdict for one creature x (array of n angles).
  function forward1(theta, x) {
    const n = x.length, dim = 1 << n, re = new Float64Array(dim), im = new Float64Array(dim);
    re[0] = 1;
    let k = 0;
    for (let l = 0; l < LAYERS; l++) {
      for (let q = 0; q < n; q++) ry(re, im, q, n, x[q]);
      for (let q = 0; q < n; q++) { ry(re, im, q, n, theta[k++]); rz(re, im, q, n, theta[k++]); }
      if (n === 2) cz(re, im, 0, 1, n);
      else if (n > 2) for (let q = 0; q < n; q++) cz(re, im, q, (q + 1) % n, n);
    }
    let z = 0;
    for (let i = 0; i < dim; i++) {
      const p = re[i] * re[i] + im[i] * im[i];
      let s = 0; for (let q = 0; q < n; q++) s += (i >> (n - 1 - q)) & 1 ? -1 : 1;
      z += p * s / n;
    }
    return z + theta[k];
  }
  const forward = (theta, X) => X.map(x => forward1(theta, x));

  function loss(theta, X, y) {
    let s = 0; for (let i = 0; i < X.length; i++) { const d = forward1(theta, X[i]) - y[i]; s += d * d; }
    return s / X.length;
  }

  // Parameter-shift gradient of the mean squared error.
  function grad(theta, X, y) {
    const P = theta.length, g = new Float64Array(P), out = forward(theta, X), tp = theta.slice(), tm = theta.slice();
    for (let k = 0; k < P - 1; k++) {
      tp[k] = theta[k] + Math.PI / 2; tm[k] = theta[k] - Math.PI / 2;
      let s = 0;
      for (let i = 0; i < X.length; i++) s += 2 * (out[i] - y[i]) * 0.5 * (forward1(tp, X[i]) - forward1(tm, X[i]));
      g[k] = s / X.length;
      tp[k] = theta[k]; tm[k] = theta[k];
    }
    let s = 0; for (let i = 0; i < X.length; i++) s += 2 * (out[i] - y[i]);
    g[P - 1] = s / X.length;
    return g;
  }

  // A trainer you can step one Adam update at a time (the page animates it).
  function trainer(X, y, seed, opts) {
    opts = opts || {};
    const lr = opts.lr || 0.15, rnd = mulberry32(seed), P = nParams(X[0].length);
    const theta = Array.from({ length: P }, () => 0.3 * gauss(rnd));
    const m = new Float64Array(P), v = new Float64Array(P);
    let t = 0;
    return {
      theta, steps: opts.steps || 80,
      get t() { return t; },
      step() {
        t++;
        const g = grad(theta, X, y);
        for (let k = 0; k < P; k++) {
          m[k] = 0.9 * m[k] + 0.1 * g[k];
          v[k] = 0.999 * v[k] + 0.001 * g[k] * g[k];
          theta[k] -= lr * (m[k] / (1 - Math.pow(0.9, t))) / (Math.sqrt(v[k] / (1 - Math.pow(0.999, t))) + 1e-8);
        }
        return loss(theta, X, y);
      },
    };
  }

  const project = (cards, feats) => cards.map(c => feats.map(f => c[f]));
  const labelOf = c => (c.label === 'friend' ? 1 : -1);

  // Verdicts for a queue of creatures with a trained theta.
  function judge(theta, cards, feats) {
    return forward(theta, project(cards, feats)).map(v => ({ v, friend: v >= 0 }));
  }

  // City outcome from the gate counts. Lost when too many of those who entered were foes,
  // or when too few friends were let in (the rule in the lore, read as "or").
  function outcome(rows, rules) {
    let tp = 0, fp = 0, fn = 0, tn = 0;
    for (const r of rows) {
      const friend = r.truth === 'friend';
      if (r.admit && friend) tp++; else if (r.admit && !friend) fp++; else if (!r.admit && friend) fn++; else tn++;
    }
    const entered = tp + fp, friends = tp + fn;
    const contamination = entered ? fp / entered : 0, rescued = friends ? tp / friends : 1;
    return { tp, fp, fn, tn, entered, friends, contamination, rescued,
             saved: contamination <= rules.maxFoes && rescued >= rules.minFriends };
  }

  // Train a sentinel to the end (used by the balance simulation and by the page when skipping).
  function trainFull(cards, feats, seed) {
    const X = project(cards, feats), y = cards.map(labelOf), tr = trainer(X, y, seed);
    while (tr.t < tr.steps) tr.step();
    return tr.theta;
  }

  return { LAYERS, FEATURES, mulberry32, hash, nParams, forward1, forward, loss, grad, trainer, project, labelOf, judge, outcome, trainFull };
})();
if (typeof module !== 'undefined') module.exports = GATE;
