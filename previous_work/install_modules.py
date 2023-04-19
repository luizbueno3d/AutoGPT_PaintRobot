#!/usr/bin/env python

import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--tkinter", help="install Tkinter using pip", action="store_true")
parser.add_argument("--pillow", help="install Pillow using pip", action="store_true")

args = parser.parse_args()

if args.tkinter:
    os.system('pip install tk')
    print('Tkinter installed successfully...')

if args.pillow:
    os.system('pip install pillow')
    print('Pillow installed successfully...')
