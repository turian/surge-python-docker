#!/usr/bin/env python3

import glob
import os
import random
from pathlib import Path

import tqdm
from slugify import slugify

paths = []
for fxp_path in glob.glob("/usr/local/share/surge-xt/**/*fxp", recursive=True):
    fxp_path = Path(fxp_path)

    # Extract the last directory and the filename (without extension)
    last_dir = fxp_path.parent.name
    filename_without_extension = fxp_path.stem

    # Combine, slugify, and append .wav extension
    combined_name = f"{last_dir}_{filename_without_extension}"
    slugified_name = slugify(combined_name)
    wavfilename = f"{slugified_name}"

    paths.append((fxp_path, wavfilename))

paths_and_i = []
for i in range(30):
    istr = f"{i:03d}"
    for fxp_path, wavfilename in paths:
        new_wavfilename = f"{wavfilename}_{istr}.wav"
        paths_and_i.append((fxp_path, new_wavfilename, istr))

random.shuffle(paths_and_i)
for fxp_path, wavfilename, istr in tqdm.tqdm(paths_and_i):
    oggfilename = wavfilename.replace(".wav", ".ogg")
    if not Path(oggfilename).exists():
        cmd = f"../playnote.py --fxppreset '{fxp_path}' -o '{wavfilename}' ; oggenc '{wavfilename}' ; rm '{wavfilename}'"
        os.system(cmd)
