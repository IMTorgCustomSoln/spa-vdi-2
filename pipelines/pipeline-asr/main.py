#!/usr/bin/env python3
"""
Main entrypoint to the script
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

import os
import sys
import argparse
from pathlib import Path
import time
import json

from src.prepare_models import finetune
from src.asr import run_workflow
from src.modules import utils

sys.path.append(Path('config').absolute().as_posix() )
from _constants import (
    logger
)



def prepare(args, CONFIG):
    """Things you should only have to do once."""

    #prepare models
    if args.prepare_models:
        logger.info("Begin prepare_models")
        check_prepare = finetune()
        if not check_prepare: 
            logger.info(f"models failed to prepare")
            exit()
        logger.info("End prepare_models")

    #prepare schema
    if args.prepare_schema:
        filepath = Path('./tests/input') / 'VDI_ApplicationStateData_v0.2.1.gz'
        workspace_schema = utils.get_schema_from_workspace(filepath)
        schema = CONFIG['INTERMEDIATE_PATH'] / 'workspace_schema_v0.2.1.json'
        with open(schema, 'w') as f:
            json.dump(workspace_schema, f)

    #prepare file list, unzip files if needed
    if args.prepare_file_list:
        logger.info("Begin ingest file location")
        file_list_path = CONFIG['INTERMEDIATE_PATH'] / 'file_list.json'
        sound_files_list = None

        if file_list_path.is_file():
            logger.info(f"File {file_list_path} already exists.  Loading now... ")
            with open(file_list_path, 'r') as f:
                string_sound_files_list = json.load(f)
            sound_files_list = [Path(file) for file in string_sound_files_list if Path(file).is_file()]
        else:
            logger.info(f"File {file_list_path} does NOT exist.")
            zip_files = [CONFIG['INPUT_PATH'] / file for file 
                         in os.listdir(CONFIG['INPUT_PATH']) 
                         #if file=='gettysburg.zip'
                         #if REGEX_INPUT_FILES_NAMES in file
                         #if '.zip' in str(file)
                         ]
            sound_files_list = []
            for file in zip_files:
                extracted_sound_files = utils.get_decompressed_filepath(
                    filepath=file,
                    target_extension=['.wav','.mp3']
                    )
                sound_files_list.extend(extracted_sound_files)
            sound_files_list = [file for file in sound_files_list if file!=None]

            string_sound_files_list = [str(file) for file in sound_files_list]
            with open(file_list_path, 'w') as f:
                json.dump(string_sound_files_list, f)
            logger.info(f"End ingest file location from {CONFIG['INPUT_PATH']} with count of files: {len(sound_files_list)}")

    return True


def infer(CONFIG):
    """Run batches through model pipelines to get intermediate files."""
    #load sound files
    file_list_path = CONFIG['INTERMEDIATE_PATH'] / 'file_list.json'
    sound_files_list = None
    with open(file_list_path, 'r') as f:
        string_sound_files_list = json.load(f)
    sound_files_list = [Path(file) for file in string_sound_files_list]    

    #run workflow on batches
    logger.info("Begin workflow on each batch")
    batches = {}
    for idx, batch in enumerate( utils.get_next_batch(sound_files_list, CONFIG['BATCH_COUNT']) ):
        batch_files = [str(file) for file in batch]
        batches[idx] = batch_files
        check_batch = run_workflow(
            sound_files=batch, 
            intermediate_save_dir=CONFIG['INTERMEDIATE_PATH']
            )
        logger.info("End workflow")

        '''
        #export
        logger.info("Begin export")
        file_path = CONFIG['OUTPUT_PATH'] / f'VDI_ApplicationStateData_v0.2.1-{idx+1}.gz'
        check = utils.export_to_vdi_workspace(workspace_schema, pdfs, file_path)
        logger.info(f"Data processed for batch-{idx+1}: {check}")
        '''
    batch_list_path = CONFIG['INTERMEDIATE_PATH'] / 'batch_list.json'
    with open(batch_list_path, 'w') as f:
        json.dump(batches, f)
    return True


def output(CONFIG):
    """Output whatever current intermediate files exist."""
    #json files
    batch_list_path = CONFIG['INTERMEDIATE_PATH'] / 'batch_list.json'
    with open(batch_list_path, 'r') as f:
        batches = json.dump(f)

    #workspace
    schema = CONFIG['INTERMEDIATE_PATH'] / 'workspace_schema_v0.2.1.json'
    with open(schema, 'r') as f:
        workspace_schema = json.load(f)

    #run workflow on batches
    logger.info("Begin workflow on each batch")
    for idx, batch in batches.items():
        dialogues = []
        for file in batch:
            file_path = CONFIG['INTERMEDIATE_PATH'] / f'{file}.json'
            with open(file_path, 'r') as f:
                dialogue = json.load(file)
                dialogues.append(dialogue)

        #export
        logger.info("Begin export")
        file_path = CONFIG['OUTPUT_PATH'] / f'VDI_ApplicationStateData_v0.2.1-{idx+1}.gz'
        check = utils.export_to_vdi_workspace(workspace_schema, dialogues, file_path)
        logger.info(f"Data processed for batch-{idx+1}: {check}")



def main(args):
    """ Main entry point of the app. """
    logger.info("Begin process")
    start_time = time.time()

    CONFIG = {}
    try:
        CONFIG['INPUT_PATH'] = Path(args.input)
        #TODO:add UNZIPPED
        CONFIG['INTERMEDIATE_PATH'] = CONFIG['INPUT_PATH'] / 'PROCESSED'
        CONFIG['OUTPUT_PATH'] = CONFIG['INPUT_PATH'] / 'OUTPUT'
        CONFIG['BATCH_COUNT'] = int(args.batch_count)
        CONFIG['REGEX_INPUT_FILES_NAMES'] = '_Calls_'         #TODO:make argument

        CONFIG['INTERMEDIATE_PATH'].mkdir(parents=True, exist_ok=True)
        CONFIG['OUTPUT_PATH'].mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)
        sys.exit()

    if args.task == 'prepare':
        prepare(args, CONFIG)
    elif args.task == 'infer':
        infer(CONFIG)
    elif args.task == 'output':
        output(CONFIG)
    else:
        pass

    logger.info(f"End process, execution took: {round(time.time() - start_time, 3)}sec")
    return True






if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required (or with default) positional argument
    parser.add_argument("task", 
                        choices=['prepare', 'infer', 'output'],
                        help="Required positional argument")
    
    #if parser.parse_args().task in ['infer', 'output']:
    parser.add_argument("input", 
                        help="Required positional argument")
    parser.add_argument("batch_count", 
                        help="Required positional argument")

    # Optional argument flag to prepare the models (defaults to False)
    #if parser.parse_args().task=='prepare':
    parser.add_argument("-m", "--prepare_models", action="store_true", default=False)
    parser.add_argument("-s", "--prepare_schema", action="store_true", default=False)
    parser.add_argument("-f", "--prepare_file_list", action="store_true", default=False)

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)