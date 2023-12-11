#!/usr/bin/env python3
"""
Generate all patches with all notes in the MIDI range of a grand
piano writing ogg files to output/
"""

import os
import os.path
import glob
import sys

import soundfile as sf
from slugify import slugify
from tqdm.auto import tqdm
import multiprocessing

import surgepy
import random

random.seed(0)

MAX_PATCHES = 1000000
SR = 44100
# Grand piano
NOTE_RANGE = [21, 108]

DURATION = 4
MAX_VELOCITY = 127


def pick_note_on_duration(lower=0.01, upper=DURATION):
    y = (upper - lower + 1.0) ** random.random() + lower - 1
    assert y >= lower
    assert y <= upper
    return y


s = surgepy.createSurge(SR)

patches = []
for patchdir in sorted(glob.glob(".local/share/surge/patches_*")):
    for root, dirs, files in os.walk(patchdir, topdown=False):
        for f in files:
            if not f.endswith(".fxp"):
                continue
            patches.append(os.path.join(root, f))
patches = sorted(patches)


def render(pnhv):
    patch, patchname, note, hold, velocity = pnhv

    slug = patchname.replace(".local/share/", "").replace(".fxp", "")
    slug = "output/%06d-%s-note=%d-velocity=%d-hold=%f.wav" % (
        patch,
        slugify(slug, lowercase=False),
        note,
        velocity,
        hold,
    )
    if os.path.exists(slug.replace(".wav", ".ogg")):
        return
    s.loadPatch(patchname)

    onesec = s.getSampleRate() / s.getBlockSize()
    buf = s.createMultiBlock(int(round(DURATION * onesec)))

    chd = [note]
    for n in chd:
        s.playNote(0, n, velocity, 0)
    s.processMultiBlock(buf, 0, int(round(hold * onesec)))

    for n in chd:
        s.releaseNote(0, n, 0)
    s.processMultiBlock(buf, int(round((DURATION - hold) * onesec)))

    # WHY? float round
    sf.write(slug, buf.T, int(round(s.getSampleRate())))
    # os.system(f"oggenc --quality 10 {slug}")
    os.system(f"oggenc -Q {slug} && rm {slug}")


npatches = len(patches)
ncores = multiprocessing.cpu_count()
print(f"{ncores} cores")
print(f"{len(patches)} patches")


def generate_patch_note_hold_and_velocity():
    for i in range(MAX_PATCHES):
        patchidx = random.randint(0, npatches - 1)
        patchname = patches[patchidx]
        note = random.randint(21, 108)
        hold = pick_note_on_duration()
        velocity = random.randint(1, MAX_VELOCITY)
        yield (patchidx, patchname, note, hold, velocity)


p = multiprocessing.Pool(ncores // 2)
r = list(
    tqdm(p.imap(render, generate_patch_note_hold_and_velocity()), total=MAX_PATCHES)
)
