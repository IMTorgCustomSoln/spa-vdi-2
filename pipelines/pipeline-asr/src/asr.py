#!/usr/bin/env python3
"""
Module Docstring

"""

__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"


from src.modules import config_env

import os
from pathlib import Path
import json




def run_workflow(sound_files, intermediate_save_dir=None):
    """..."""

    config_env.config()
    """
    #load data
    path_samples = Path('./samples')
    sound_files = [f'./samples/{file}' for file in 
                   os.listdir(path_samples)
                   if ( (os.path.splitext(file)[1] in ['.mp3','.wav'])  
                       and (os.path.basename(file) != 'NOT-AN-AUDIO-FILE.wav') 
                       and (os.path.basename(file) != 'taunt-FAILS.wav') 
                       ) 
                    ]
    #TODO:validate audio and remove failures

    #TODO:remove
    sound_files = sound_files       #[3:4] #fails
    """

    #prepare data
    from datasets import Dataset, Audio
    sound_filepath_strings = [str(file) for file in sound_files if file != None]

    '''
    #TODO:remove previously processed files
    json_files = [json for json in os.listdir(intermediate_save_dir) if (('.json' in json) and (json != 'file_list.json'))]
    previously_processed = [file for file in sound_filepath_strings if file in json_files]
    processed_dialogues = []
    for file in previously_processed:
        with open(file, 'r') as f:
            dialogue = json.load(f)
            processed_dialogues.append(dialogue)
    unprocessed = [file for file in sound_filepath_strings if file not in json_files]
    '''
    audio_dataset = Dataset.from_dict({'audio': sound_filepath_strings}).cast_column('audio', Audio())


    #transcribe sample
    from transformers import pipeline
    from transformers.pipelines.pt_utils import KeyDataset

    asr_pipeline = pipeline(
        task='automatic-speech-recognition', 
        model='openai/whisper-base',
        generate_kwargs={"language": "english"},
        )
    """
    sample = audio_dataset[0]['audio']
    dialogues = asr_pipeline(
        inputs=sample.copy(),
        generate_kwargs={'max_new_tokens': 256},
        return_timestamps=True
        )
    """
    dialogues = []
    gen = asr_pipeline(KeyDataset(audio_dataset, 'audio'), 
                       #generate_kwargs={'max_new_tokens': 256}, 
                       return_timestamps=True,
                       chunk_length_s=30        #batch processing of single file, [ref](https://huggingface.co/blog/asr-chunking)
                       )
    for idx, file in enumerate( gen ):
        file_path = audio_dataset[idx]['audio']['path']
        file_name = os.path.basename( file_path )
        sampling_rate = audio_dataset[idx]['audio']['sampling_rate']
        record = {
            'file_name': file_name,
            'file_path': file_path, 
            'sampling_rate': sampling_rate, 
            'chunks': file['chunks']
            }
        dialogues.append(record)


    #run classification models on each: chunk,item
    from src.classification import classifier

    for idx, dialogue in enumerate(dialogues):
        dialogues[idx]['classifier'] = []
        for chunk in dialogue['chunks']:
            results = classifier(chunk)
            for result in results:
                if result != None:
                    dialogues[idx]['classifier'].append(result)
                else:
                    dialogues[idx]['classifier'].append([])
               


    #save
    from src.modules import utils

    if intermediate_save_dir:
        for dialogue in dialogues:
            save_path = Path(intermediate_save_dir) / f'{dialogue["file_name"]}.json'
            try:
                with open(save_path, 'w') as f:
                    json.dump(dialogue, f)
            except Exception as e:
                print(e)
    #TODO:   dialogues.extend(processed_dialogues)   #combine records of previously processed dialogues 


    #format and output
    from src.modules import utils

    pdfs = []
    for dialogue in dialogues:
        '''
        #to file
        output_name = Path('./tests/results') / f"{dialogue['file_name']}.pdf"
        pdf = utils.output_to_pdf(
            lines=dialogue['chunks'], 
            filename=output_name,
            output_type='file'
        )
        '''
        #to string
        pdf = utils.output_to_pdf(
            dialogue=dialogue,
            output_type='str'
        )
        if pdf!=None:
            pdfs.append(pdf)

    #TODO:change to zip file
    '''
    * prepare output by loading Workspace, then extracting schema
    * fill-in key values
    * (later: use EnteroDoc to extract info)
    * 
    * export and zip
    '''
    #utils.export_to_vdi_workspace(pdfs)

    
    return pdfs