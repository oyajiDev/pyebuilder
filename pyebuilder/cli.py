# -*- coding: utf-8 -*-
import os, sys, argparse
from .builder import build


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default = "../build")
    parser.add_argument("--config-file", default = "pyebuilder.config.json")
    parser.add_argument("--release", action = "store_true")
    parser.add_argument("--python-version", default = f"{sys.version_info.major}.{sys.version_info.minor}")
    parser.add_argument("--node-version", default = "18.12.1")
    parser.add_argument("--icon", default = None)
    parser.add_argument("--installer", action = "store_true")

    args = parser.parse_args()

    build(
        os.getcwd(),
        os.path.realpath(args.dest),
        args.config_file,
        "release" if args.release else "debug",
        args.python_version, args.node_version,
        args.icon,
        args.installer
    )
