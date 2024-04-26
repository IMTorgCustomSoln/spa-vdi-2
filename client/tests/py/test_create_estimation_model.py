#!/usr/bin/env python3
"""
Test estimation model creation
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from tests.py.create_estimation_model import main


class Args:
    pass

def test_main():
    args = Args()
    args.input_dir = "./tests/logs/"
    args.plots = True
    args.estimate_model = True
    main(args)