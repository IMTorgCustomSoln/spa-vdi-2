#!/usr/bin/env python3
"""
Module Docstring
"""

from src import prepare_models
from src import asr
from src.modules import utils
import os
from pathlib import Path


def test_prepare_models():
    tmp = prepare_models.finetune()
    assert tmp == True