#!/usr/bin/env python3
"""
Module Docstring
"""

from src import prepare_models
from src import asr
from src.modules import utils
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