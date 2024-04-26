#!/usr/bin/env python3
"""
Module Docstring
"""

import os
from pathlib import Path

from main import main


def test_main():
    class Args:
        input=Path(os.getcwd()) / 'samples'
        prepare_models = False
    args = Args()
    main(args)

    #cleanup
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/gettysburg10.wav').unlink()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/tmp/gettysburg').rmdir()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/tmp/__MACOSX').rmdir()
    assert True == True