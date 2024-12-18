"""
Rebin all mac or mythen files in directories

May need to adjust the regexs used for finding the files for your data

This script essentially does the following
find <directory> -type f -maxdepth 1 | grep -E <regex> | xargs ./rebin -p -d 2 -d 3 -d 5 [-r] [+s] [-m]
"""

import argparse
import os
import re

from . import maincmd


# List of delta values to rebin to
DELTAS = [2, 3, 5]
# Regex finds mac data filenames
mac_reg = re.compile(r"mac.*\.dat")
# Regex finds files of the form <number>.dat
scan_reg = re.compile(r"(\/|^)\d{6,}.dat")


def run_rebin(files, angle=0.0, delta=[0.1], rebin=True, sum=False, mythen=None):
    args = argparse.Namespace()
    args.angle = angle
    args.delta = delta
    args.rebin = rebin
    args.sum = sum
    args.mythen = mythen
    args.output = args.year = args.visit = None
    args.processed = True
    args.files = files
    maincmd.process(args)


def _re_find(reg, files):
    return [f for f in files if reg.search(f)]


def mac_find(files):
    return _re_find(mac_reg, files)


def mythen_find(files):
    return _re_find(scan_reg, files)


def _listdir(dir):
    return [os.path.join(dir, file) for file in os.listdir(dir)]


def main(args=None):
    parser = argparse.ArgumentParser(
        usage="%(prog)s -mac|-mythen [-r] directory",
        description="Process all mac or mythen files in a directory or several",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        action="store_true",
        default=False,
        dest="recursive",
        help="Look through subdirectories for files to process",
    )
    parser.add_argument(
        "-mac", action="store_true", default=False, help="Look for mac data to process"
    )
    parser.add_argument(
        "-mythen",
        action="store_true",
        default=False,
        help="Look for mythen data to process",
    )
    parser.add_argument(
        "-i",
        "--individual",
        action="store_true",
        default=False,
        help="Load and process one file at a time while rebinning",
    )
    parser.add_argument("directories", nargs="+")
    args = parser.parse_args(args)

    ndirs = args.directories[:]
    if args.recursive:
        for dir in args.directories:
            ndirs.extend([x[0] for x in os.walk(dir)])

    ndirs = set(ndirs)
    for dir in ndirs:
        if args.mac:
            mac_files = mac_find(_listdir(dir))
            if args.individual:
                for file in mac_files:
                    run_rebin([file], delta=DELTAS, rebin=True, sum=False)
            else:
                run_rebin(mac_files, delta=DELTAS, rebin=True, sum=False)
        if args.mythen:
            run_rebin(
                mythen_find(_listdir(dir)),
                delta=DELTAS,
                rebin=True,
                sum=True,
                mythen=True,
            )


if __name__ == "__main__":
    main()
