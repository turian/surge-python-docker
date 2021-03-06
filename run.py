#!/usr/bin/env python3

import os
import os.path
import glob
import sys

import soundfile as sf

sys.path.append("surge/buildpy")
import surgepy

s = surgepy.createSurge( 44100 )

patches = []
for patchdir in glob.glob("surge/resources/data/patches_*"):
    for root, dirs, files in os.walk(patchdir, topdown=False):
        for f in files:
            if not f.endswith(".fxp"):
                continue
            patches.append(os.path.join(root, f))

patch = patches[-1]
s.loadPatch(patch)

onesec = int(s.getSampleRate() / s.getBlockSize())
buf = s.createMultiBlock( 2 * onesec)

chd = [ 60, 63, 67, 71 ]
for n in chd:
    s.playNote( 0, n, 127, 0 )
s.processMultiBlock( buf, 0, onesec )

for n in chd:
    s.releaseNote( 0, n, 0 )
s.processMultiBlock( buf, onesec )

# WHY? float round
sf.write('output/example.wav', buf.T, int(round(s.getSampleRate())))
