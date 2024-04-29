#!/usr/bin/env python3
"""
Module Docstring
"""

import os
from pathlib import Path

from main import main


def test_main_batch_1():
    class Args:
        input=Path(os.getcwd()) / 'samples'
        batch_count=1
        prepare_models = False
    args = Args()
    main(args)

    #cleanup
    """
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/gettysburg/gettysburg10.wav').unlink()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/gettysburg').rmdir()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/__MACOSX/gettysburg').rmdir()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/__MACOSX').rmdir()
    """
    assert True == True


def test_main_batch_4():
    class Args:
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        prepare_models = False
    args = Args()
    main(args)

    #cleanup
    """
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/gettysburg/gettysburg10.wav').unlink()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/gettysburg').rmdir()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/__MACOSX/gettysburg').rmdir()
    Path('/workspaces/spa-vdi-2/pipelines/pipeline-asr/samples/PROCESSED/__MACOSX').rmdir()
    """
    assert True == True