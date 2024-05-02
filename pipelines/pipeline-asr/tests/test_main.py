#!/usr/bin/env python3
"""
Module Docstring
"""

import os
from pathlib import Path

from main import main


def test_entrypoint():
    exit_status = os.system('pipenv run python main.py --version')
    assert exit_status == 0

def test_prepare_files():
    #exit_status = os.system('main.py prepare samples/ 4 -msf')
    class Args:
        task='prepare'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        prepare_models=False
        prepare_schema=True
        prepare_file_list=True
    args = Args()
    main(args)
    assert True == True

def test_prepare_model():
    #exit_status = os.system('main.py prepare samples/ 4 -msf')
    class Args:
        task='prepare'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        prepare_models=True
        prepare_schema=False
        prepare_file_list=False
    args = Args()
    main(args)
    assert True == True

def test_infer():
    #exit_status = os.system('main.py prepare samples/ 4 -msf')
    class Args:
        task='infer'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
    args = Args()
    main(args)
    assert True == True




def test_main_batch_1():
    class Args:
        input=Path(os.getcwd()) / 'samples'
        batch_count=1
        prepare_models=False
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
        prepare_models=False
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