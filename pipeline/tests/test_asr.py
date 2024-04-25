#!/usr/bin/env python3
"""
Module Docstring
"""

from src import asr
import os
from pathlib import Path

def test_asr_workflow():
    #load data
    path_samples = Path('./samples')
    sound_files = [f'./samples/{file}' for file in 
                   os.listdir(path_samples)
                   if ( (os.path.splitext(file)[1] in ['.mp3','.wav'])  
                       and (os.path.basename(file) != 'NOT-AN-AUDIO-FILE.wav') 
                       and (os.path.basename(file) != 'taunt-FAILS.wav') 
                       ) 
                    ]
    #run workflow
    pdfs = asr.run_workflow(sound_files)
    assert len(pdfs) > 0


from src import prepare_models

def test_prepare_models():
    tmp = prepare_models.finetune()
    assert tmp == True


from src.modules import utils
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
    check = utils.export_to_vdi_workspace(pdfs)

    assert check == True