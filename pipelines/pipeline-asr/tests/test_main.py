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
    """
    Scenario:
    * prepare workspace_schema.json from client export
    * prepare `file_list.json` with list of all audio files found in all decompressed .zip files (now each is a directory)
    * run>>>  `python main.py prepare samples/ 4 -sf`
    """
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
    """
    Scenario:
    * prepare models by finetuning on train/test data
    * run>>>  `python main.py prepare samples/ 4 -m`
    """
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

def test_DEPRECATE_infer_audio_files():
    """
    Scenario:
    * ran `python main.py prepare samples/ 4 -sfm`
    * all .zip files decompressed and audio files listed in `file_list.json`
    * ready to apply pipeline inference to make intermediate files
    * run>>> `python main.py infer samples/ 4`
    """
    class Args:
        task='infer'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        infer_text_classify_only=False
        infer_from_remaining_list=False
    args = Args()
    main(args)
    assert True == True

#WORKS
def test_report_on_remaining_audio_files():
    """
    Scenario:
    * need `remaining_list.json` of unprocessed audio files
    * run>>> `python main.py report samples/ 4 --report_process_status`
    """
    class Args:
        task='report'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        prepare_models=False
        prepare_schema=False
        prepare_file_list=False
        infer_text_classify_only=False
        report_process_status=True
        report_text_classify=False
    args = Args()
    main(args)
    assert True == True

#WORKS
def test_reinfer_remaining_audio_files():
    """
    Scenario:
    * ran `python main.py infer samples/ 4`
    * process failed with no `batch_list.json`
    * create `remaining_list.json` with `python main.py report samples/ 4 --report_process_status`
    * run>>> `python main.py infer samples/ 4 --infer_from_remaining_list`
    """
    class Args:
        task='infer'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        infer_text_classify_only=False
        infer_from_remaining_list=True
    args = Args()
    main(args)
    assert True == True

def test_reinfer_text_classification_on_intermediate():
    """
    Scenario:
    * ran `python main.py infer samples/ 4`
    * process complete with `batch_list.json`
    * models are retrained with `python main.py prepare samples/ 4 --prepare_model`
    * do not perform audio transcription, but overwrite `dialogue['classifier]`
    * run>>> `python main.py infer samples/ 4 --infer_text_classify_only`
    """
    class Args:
        task='infer'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        infer_text_classify_only=True
        infer_from_remaining_list=False
    args = Args()
    main(args)
    assert True == True

def test_report_on_intermediate_classify_results():
    """
    Scenario:
    * ran `python main.py infer samples/ 4`
    * need to review `hit_list.csv` text classification model results
    * run>>> `python main.py report samples/ 4 --report_text_classify`
    """
    class Args:
        task='report'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        prepare_models=False
        prepare_schema=False
        prepare_file_list=False
        infer_text_classify_only=False
        report_process_status=False
        report_text_classify=True
    args = Args()
    main(args)
    assert True == True


#WORKS
def test_output_to_excel():
    """
    Scenario:
    * ~~need `batch_list.json` of processed audio files~~
    * need `remaining_list.json` of processed audio files
    * run>>> `python main.py output samples/ 4`
    """
    class Args:
        task='output'
        input=Path(os.getcwd()) / 'samples'
        batch_count=1
        output_type_excel=True
    args = Args()
    main(args)
    assert True == True

def test_output_batch_files():
    """
    Scenario:
    * ~~need `batch_list.json` of processed audio files~~
    * need `remaining_list.json` of processed audio files
    * run>>> `python main.py output samples/ 4`
    """
    class Args:
        task='output'
        input=Path(os.getcwd()) / 'samples'
        batch_count=1
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
        task='all'
        input=Path(os.getcwd()) / 'samples'
        batch_count=4
        prepare_models=False
        prepare_schema=False
        prepare_file_list=False
        infer_text_classify_only=False
        infer_from_remaining_list=False
        report_process_status=False
        report_text_classify=False
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