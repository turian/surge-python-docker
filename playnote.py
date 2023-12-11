#!/usr/bin/env python3
"""
Play a Surge vstpreset with specified note in the MIDI range and
settings, writing a 32-bit WAV file to the specified output.
"""

import argparse
import os
import sys
import numpy as np

import soundfile as sf
import surgepy


def play_and_record(fxppreset, note, duration, hold, velocity, output, sr):
    s = surgepy.createSurge(sr)

    # Load the specified FXP preset file
    if not s.loadPatch(fxppreset):
        raise ValueError("Failed to load the preset file: " + fxppreset)

    blocks_per_second = sr / s.getBlockSize()
    total_blocks = int(round(duration * blocks_per_second + 0.5))
    hold_blocks = int(round(hold * blocks_per_second + 0.5))
    release_blocks = total_blocks - hold_blocks  # Adjust release blocks to match total

    buf = s.createMultiBlock(total_blocks)

    s.playNote(0, note, velocity, 0)
    s.processMultiBlock(buf, 0, hold_blocks)

    s.releaseNote(0, note, 0)
    s.processMultiBlock(buf, hold_blocks)

    max_abs_value = np.max(np.abs(buf))
    if max_abs_value > 1.0:
        buf /= max_abs_value
        max_abs_value = np.max(np.abs(buf))
    sf.write(output, buf.T, sr, subtype="FLOAT")  # Save as 32-bit float

    # Output diagnostics to stderr
    sys.stderr.write(f"blocks_per_second: {blocks_per_second}\n")
    sys.stderr.write(
        f"Total blocks: {total_blocks}, Hold blocks: {hold_blocks}, Release blocks: {release_blocks}\n"
    )
    sys.stderr.write(f"Max absolute buffer value: {max_abs_value}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a single MIDI note from a Surge patch."
    )
    parser.add_argument(
        "--note",
        type=int,
        default=42,
        choices=range(0, 128),
        help="MIDI note number (default 42)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=2.0,
        help="Duration of the note in seconds (default 2.0)",
    )
    parser.add_argument(
        "--hold_duration",
        type=float,
        default=0.5,
        help="Hold duration of the note in seconds (default 0.5)",
    )
    parser.add_argument(
        "--velocity",
        type=int,
        default=100,
        choices=range(0, 128),
        help="Velocity of the note (default 100)",
    )
    parser.add_argument(
        "--fxppreset", type=str, required=True, help="Path to the .fxp preset file"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output file path for the WAV file",
    )
    parser.add_argument(
        "--sampling_rate",
        type=int,
        default=48000,
        help="Sampling rate in Hz (default 48000)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.fxppreset):
        raise ValueError("FXP preset file does not exist: " + args.fxppreset)

    play_and_record(
        args.fxppreset,
        args.note,
        args.duration,
        args.hold_duration,
        args.velocity,
        args.output,
        args.sampling_rate,
    )


if __name__ == "__main__":
    main()
