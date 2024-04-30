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


def test_prepare_schema():
    filepath = Path('./tests/input/VDI_ApplicationStateData_v0.2.1.gz')
    documents_schema = utils.get_schema_from_workspace(filepath)
    assert len(documents_schema.items()) == 33