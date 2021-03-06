#!/usr/bin/env python3

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

SR = 44100
# Grand piano
NOTE_RANGE = [21, 108]

DURATION = 4
NOTE_ON = 3
VELOCITY = 127

s = surgepy.createSurge(SR)

patches = []
for patchdir in glob.glob(".local/share/surge/patches_*"):
    for root, dirs, files in os.walk(patchdir, topdown=False):
        for f in files:
            if not f.endswith(".fxp"):
                continue
            patches.append(os.path.join(root, f))


def render(patch_and_note):
    patch, note = patch_and_note
    slug = patch.replace(".local/share/", "").replace(".fxp", "")
    slug = slugify(slug, lowercase=False) + f"-{note}.wav"
    slug = f"output/{slug}"
    if os.path.exists(slug.replace(".wav", ".ogg")):
        return
    # print(slug)
    s.loadPatch(patch)

    onesec = s.getSampleRate() / s.getBlockSize()
    buf = s.createMultiBlock(int(round(DURATION * onesec)))

    chd = [note]
    for n in chd:
        s.playNote(0, n, VELOCITY, 0)
    s.processMultiBlock(buf, 0, int(round(NOTE_ON * onesec)))

    for n in chd:
        s.releaseNote(0, n, 0)
    s.processMultiBlock(buf, int(round((DURATION - NOTE_ON) * onesec)))

    # WHY? float round
    sf.write(slug, buf.T, int(round(s.getSampleRate())))
    # os.system(f"oggenc --quality 10 {slug}")
    os.system(f"oggenc -Q {slug} && rm {slug}")


ncores = multiprocessing.cpu_count()
print(f"{ncores} cores")
patch_and_notes = []
for patch in patches:
    for note in range(NOTE_RANGE[0], NOTE_RANGE[1] + 1):
        patch_and_notes.append((patch, note))
random.shuffle(patch_and_notes)
with multiprocessing.Pool(ncores) as p:
    r = list(tqdm(p.imap(render, patch_and_notes), total=len(patch_and_notes)))
