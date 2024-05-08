#!/usr/bin/env python3
"""
Module Docstring
"""

from src import prepare_models
from src import asr
from src.modules import utils
import os
from pathlib import Path


def test_export_to_vdi_workspace():
    #assume: workspace comes from vdi import/export of file: `./tests/results/five-nights-spoken-pitched_71bpm_F_minor.wav.pdf`
    #load data
    path_samples = Path('./samples')
    sound_files = [f'./samples/{file}' for file in 
                   os.listdir(path_samples)
                   if ( os.path.basename(file) == 'five-nights-spoken-pitched_71bpm_F_minor.wav' ) 
                   ]
    #run workflow
    pdfs = asr.run_workflow(sound_files)
    check = utils.export_to_output(pdfs)

    assert check == True