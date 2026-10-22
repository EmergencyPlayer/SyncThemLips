import math

import aud
import numpy as np


def load_envelope(filepath, fps, low_hz=0.0, high_hz=0.0,
                  attack=0.0, release=0.0, normalize=True):
    """Return a per-frame amplitude envelope (numpy array) for an audio file."""
    snd = aud.Sound(filepath)
    rate, _channels = snd.specs
    if low_hz > 0:
        snd = snd.highpass(low_hz)
    if high_hz > 0:
        snd = snd.lowpass(high_hz)

    data = np.abs(np.asarray(snd.data(), dtype=np.float32))
    if data.ndim == 2:
        data = data.max(axis=1)  # peak across channels

    spf = rate / fps  # samples per frame
    n_frames = max(1, math.ceil(len(data) / spf))
    edges = np.minimum((np.arange(n_frames + 1) * spf).astype(np.int64), len(data))
    peaks = np.array([
        data[edges[i]:edges[i + 1]].max() if edges[i + 1] > edges[i] else 0.0
        for i in range(n_frames)
    ], dtype=np.float32)

    env = _follow(peaks, fps, attack, release)
    if normalize:
        peak = float(env.max())
        if peak > 0:
            env = env / peak
    return env


def _follow(values, fps, attack, release):
    """Simple attack/release envelope follower (times in seconds)."""
    def coef(t):
        return 1.0 if t <= 0 else 1.0 - math.exp(-1.0 / max(t * fps, 1e-6))

    a_att, a_rel = coef(attack), coef(release)
    out = np.empty_like(values)
    cur = 0.0
    for i, v in enumerate(values):
        cur += (v - cur) * (a_att if v > cur else a_rel)
        out[i] = cur
    return out


def slope_targets(env, closed, open_, threshold):
    """Original rule: open when the envelope is rising AND above threshold.

    Returns len(env) + 1 values; the last key always closes the mouth.
    """
    out = []
    prev = float(env[0])
    for v in env:
        v = float(v)
        out.append(open_ if (v - prev > 0 and v > threshold) else closed)
        prev = v
    out.append(closed)
    return out
