#!/usr/bin/env python3

import glob
import hashlib
import os
import os.path
import random
from pathlib import Path

import tqdm
from slugify import slugify


def create_wav_filename(fxppath):
    fxp_path = Path(fxppath)

    # Extract names from the last two directories and the filename (without extension)
    if len(fxp_path.parts) >= 3:
        parent_dir = fxp_path.parent.name
        grandparent_dir = fxp_path.parent.parent.name
        combined_dir = f"{grandparent_dir}  {parent_dir}"
    else:
        combined_dir = fxp_path.parent.name

    filename_without_extension = fxp_path.stem

    # Combine, slugify, and append .wav extension
    combined_name = f"{combined_dir}  {filename_without_extension}"
    slugified_name = slugify(combined_name)
    wavfilename = f"{slugified_name}"

    return wavfilename


paths = []
wavfilenames = set()
for fxp_path in glob.glob("/usr/local/share/surge-xt/**/*fxp", recursive=True):
    fxp_path = Path(fxp_path)
    wavfilename = create_wav_filename(fxp_path)

    if wavfilename in wavfilenames:
        print("Skipping duplicate: " + wavfilename)
        continue
    assert wavfilename not in wavfilenames
    wavfilenames.add(wavfilename)

    paths.append((fxp_path, wavfilename))

    if not os.path.exists(wavfilename):
        os.mkdir(wavfilename)

paths.sort(key=lambda x: hashlib.sha1(str(x[0]).encode("utf-8")).hexdigest())
paths = paths[:50]

paths_and_i = []
for i in range(30):
    # for i in range(10):
    istr = f"{i:03d}"

    for fxp_path, wavfilename in paths:
        new_wavfilename = f"{wavfilename}/{wavfilename}_{istr}.wav"
        paths_and_i.append((fxp_path, new_wavfilename, istr))

random.shuffle(paths_and_i)
for fxp_path, wavfilename, istr in tqdm.tqdm(paths_and_i):
    oggfilename = wavfilename.replace(".wav", ".ogg")
    if not Path(oggfilename).exists():
        cmd = f"../playnote.py --fxppreset '{fxp_path}' -o '{wavfilename}' ; oggenc -Q '{wavfilename}' ; rm '{wavfilename}'"
        os.system(cmd)
