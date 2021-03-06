#!/usr/bin/env python3

import sys
# Replace this with a path to the built surgepy
sys.path.append("surge/buildpy/")

import surgepy

print(surgepy.getVersion())
