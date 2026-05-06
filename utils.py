# utils.py
import math

def calculate_filter_chain(settings: dict, total_duration: float) -> str:
    """
    Generates the FFmpeg filter_complex string based on user settings.
    """
    filter_chain = []
    
    tempo = settings['speed'] / 100.0
    pitch_semitones = settings['pitch']
    
    # --- Pitch & Speed Logic ---
    if settings['coupled']:
        # Nightcore Mode: Speed up naturally raises pitch
        if tempo > 0:
            pitch_shift_from_speed = 12 * math.log2(tempo)
            total_pitch_shift = pitch_shift_from_speed + pitch_semitones
            
            rate_mult = 2 ** (total_pitch_shift / 12)
            filter_chain.append(f"asetrate=44100*{rate_mult:.4f}")
            
            correction_factor = rate_mult / tempo
            # Prevent division by zero or extreme values
            if correction_factor > 0.01:
                filter_chain.append(f"atempo={1/correction_factor:.4f}")
    else:
        # Custom Mode: Independent pitch and speed
        if pitch_semitones != 0:
            pitch_mult = 2 ** (pitch_semitones / 12)
            filter_chain.append(f"asetrate=44100*{pitch_mult:.4f}")
            filter_chain.append(f"atempo={1/pitch_mult:.4f}")
        
        if tempo != 1.0 and tempo > 0:
            filter_chain.append(f"atempo={tempo:.4f}")

    # --- Effects ---
    if settings['bass_boost']:
        filter_chain.append("bass=g=6:f=110:w=0.6")

    if settings['reverb'] > 0:
        # Simple echo for reverb effect
        filter_chain.append("aecho=0.8:0.9:1000:0.3")
        
    # --- Fade ---
    if settings['fade_in'] > 0:
        filter_chain.append(f"afade=t=in:st=0:d={settings['fade_in']}")
    if settings['fade_out'] > 0:
        # Ensure we don't fade longer than the song
        start_time = max(0, total_duration - settings['fade_out'])
        filter_chain.append(f"afade=t=out:st={start_time}:d={settings['fade_out']}")

    # --- Limiter (Prevent clipping) ---
    filter_chain.append("alimiter=limit=0.9")

    return ",".join(filter_chain)