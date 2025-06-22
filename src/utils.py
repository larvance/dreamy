from time import time
from typing import List

import pyo

notes_x = [.164, .29, .60, .694, .88, 1]


def get_note_from_x(x):
    x *= 100
    return 290.278 + 0.104563890431105 * x + 0.032837040477757 * x ** 2 - 0.000245894267150 * x ** 3 + 0.000000841872518 * x ** 4


# this is to make it so that when the user moves their hand, the sound further away is blurry/vibrating
def modulate_running_frequencies(plucked, x):
    target_freq = get_note_from_x(x)

    for freq, (envs, rev, mod, lfo, freq_sig, mul_sig) in plucked.items():
        distance = abs(freq - target_freq)
        if distance < 5:
            continue

        mod_depth = min(1.5, 0.1 + 0.01 * distance)
        mod_rate = min(6.0, 1.0 + 0.1 * distance)

        if mod is None:
            freq_sig = pyo.Sig(mod_rate)
            mul_sig = pyo.Sig(mod_depth)
            lfo = pyo.Sine(freq=freq_sig, mul=mul_sig).play()
            shift = pyo.FreqShift(rev, shift=lfo).out()
            plucked[freq] = (envs, rev, shift, lfo, freq_sig, mul_sig)
        else:
            freq_sig.value = mod_rate
            mul_sig.value = mod_depth


def excite_string(plucked, last_trigger_time, x, brightness=0.8):
    freq = get_note_from_x(x)
    now = time()

    if freq in plucked:
        envs = plucked[freq][0]
        if any(env.isPlaying() for env in envs) and now - last_trigger_time.get(freq, 0) < 0.1:
            return

    noise = pyo.BrownNoise(mul=brightness)
    detune = freq * 0.01
    noise_band = pyo.ButBR(noise, freq=freq + detune, q=5).mix(1)
    mixed_exc = noise + 0.2 * noise_band

    string = pyo.Waveguide(mixed_exc, freq=freq, dur=4.0, minfreq=freq)

    base_mul = 0.3
    attack_time = 0.01 + 0.05 * brightness
    envs: List[pyo.Adsr] = []
    voices = []
    for div in range(1, 11):
        env = pyo.Adsr(
            attack=attack_time,
            decay=0.1,
            sustain=0.7,
            release=1.5,
            dur=2.0,
            mul=base_mul / div
        )
        sig = string * env
        envs.append(env)
        voices.append(sig)

    combo = sum(voices)

    chorus = pyo.Chorus(combo, depth=0.3, feedback=0.15, bal=0.3)
    rev = pyo.Freeverb(chorus, size=0.85, damp=0.3, bal=0.4).out()

    for env in envs:
        env.play()

    plucked[freq] = (envs, rev, None, None, None, None)
    last_trigger_time[freq] = now
    # for debug: print(f"Playing {freq:.1f} Hz at x={x:.3f}, brightness={brightness:.2f}")


def cleanup_plucked(plucked, last_trigger_time):
    to_delete = []
    for freq, item in plucked.items():
        envs = item[0]
        if not any(env.isPlaying() for env in envs):
            to_delete.append(freq)
    for freq in to_delete:
        del plucked[freq]
        last_trigger_time.pop(freq, None)
