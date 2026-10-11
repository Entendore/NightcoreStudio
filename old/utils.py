import math


def calculate_filter_chain(settings: dict, total_duration: float) -> str:
    """
    Generates the FFmpeg -af filter string based on user settings.

    Fixes applied:
      - Skips atempo when correction ≈ 1.0 (was crashing Nightstep)
      - Uses short-delay reverb instead of 1000ms echo
      - Chains atempo for extreme speed values
      - Reverb applied before bass boost to avoid double-boosting
      - Stronger limiter at the end
    """
    filter_chain = []

    tempo = settings['speed'] / 100.0
    pitch_semitones = settings['pitch']

    # ── Pitch & Speed ──
    if settings.get('coupled'):
        # Coupled mode: speed change naturally shifts pitch
        if tempo > 0 and abs(tempo - 1.0) > 0.001:
            pitch_from_speed = 12 * math.log2(max(tempo, 0.01))
            total_pitch = pitch_from_speed + pitch_semitones
            rate_mult = 2 ** (total_pitch / 12)
            filter_chain.append(f"asetrate=44100*{rate_mult:.6f}")

            correction = rate_mult / max(tempo, 0.01)
            # FIX: skip atempo when correction ≈ 1.0 — FFmpeg rejects atempo=1.0
            if abs(correction - 1.0) > 0.001:
                filter_chain.extend(_atempo_chain(1.0 / correction))
        elif pitch_semitones != 0:
            # Speed is ~1.0 but user wants pitch shift
            pitch_mult = 2 ** (pitch_semitones / 12)
            filter_chain.append(f"asetrate=44100*{pitch_mult:.6f}")
            filter_chain.extend(_atempo_chain(1.0 / pitch_mult))
    else:
        # Custom mode: independent pitch and speed
        if pitch_semitones != 0:
            pitch_mult = 2 ** (pitch_semitones / 12)
            filter_chain.append(f"asetrate=44100*{pitch_mult:.6f}")
            filter_chain.extend(_atempo_chain(1.0 / pitch_mult))

        if tempo > 0 and abs(tempo - 1.0) > 0.001:
            filter_chain.extend(_atempo_chain(tempo))

    # ── Reverb (BEFORE bass boost to avoid boosting the reverb tail) ──
    reverb_amount = settings.get('reverb', 0)
    if reverb_amount > 0:
        mix = reverb_amount / 100.0
        # Short delays for a natural room-reverb feel, not a 1-second echo
        delay_ms = int(25 + 75 * mix)       # 25–100 ms
        out_gain = 0.30 + mix * 0.30        # 0.30–0.60  (keeps overall volume sane)
        decay    = 0.10 + mix * 0.25        # 0.10–0.35
        filter_chain.append(
            f"aecho=0.8:{out_gain:.2f}:{delay_ms}:{decay:.2f}"
        )

    # ── Bass Boost ──
    if settings.get('bass_boost'):
        filter_chain.append("bass=g=5:f=100:w=0.5")

    # ── Fade ──
    fade_in = settings.get('fade_in', 0)
    fade_out = settings.get('fade_out', 0)
    if fade_in > 0:
        filter_chain.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        start_t = max(0, total_duration - fade_out)
        filter_chain.append(f"afade=t=out:st={start_t:.3f}:d={fade_out}")

    # ── Limiter (always last — prevents clipping from any above filter) ──
    filter_chain.append("alimiter=limit=0.95:attack=5:release=50")

    return ",".join(filter_chain)


def _atempo_chain(rate: float) -> list:
    """
    FFmpeg atempo only accepts 0.5–100.0.  For values outside that range
    we chain multiple atempo filters.
    """
    if rate < 0.5:
        # Recursively halve until within range
        return _atempo_chain(rate / 0.5) + ["atempo=0.5"]
    if rate > 100.0:
        return _atempo_chain(rate / 100.0) + ["atempo=100.0"]
    return [f"atempo={rate:.6f}"]