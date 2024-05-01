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


def get_next_batch(lst, batch_count):
    """...."""
    final_idx = int(len(lst)/batch_count-1)
    index_list = list(range( final_idx + 1  ))
    remainder = len(lst)%batch_count
    for idx in index_list:
        init = idx * batch_count
        if remainder>0 and idx==final_idx:
            batch = lst[init: (idx+1) * batch_count+remainder]
        else:
            batch = lst[init: (idx+1) * batch_count]
        yield batch




def main(args):
    """ Main entry point of the app. """
    logger.info("Begin process")
    start_time = time.time()

    try:
        INPUT_PATH = Path(args.input)
        #TODO:add UNZIPPED
        INTERMEDIATE_PATH = INPUT_PATH / 'PROCESSED'
        OUTPUT_PATH = INPUT_PATH / 'OUTPUT'
        BATCH_COUNT = int(args.batch_count)
        REGEX_INPUT_FILES_NAMES = '_Calls_'         #TODO:make argument

        INTERMEDIATE_PATH.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(e)
        logger.info(f"End process, execution took: {round(time.time() - start_time, 3)}sec")
        sys.exit()

    #prepare models
    if args.prepare_models:
        logger.info("Begin prepare_models")
        check_prepare = finetune()
        if not check_prepare: 
            logger.info(f"models failed to prepare")
            exit()
        logger.info("End prepare_models")

    #prepare schema
    filepath = Path('./tests/input/VDI_ApplicationStateData_v0.2.1.gz')
    workspace_schema = utils.get_schema_from_workspace(filepath)

    #prepare file list
    logger.info("Begin ingest file location")
    file_list_path = INTERMEDIATE_PATH / 'file_list.json'
    sound_files_list = None

    if file_list_path.is_file():
        logger.info(f"File {file_list_path} already exists.  Loading now... ")
        with open(file_list_path, 'r') as f:
            string_sound_files_list = json.load(f)
        sound_files_list = [Path(file) for file in string_sound_files_list if Path(file).is_file()]
    else:
        logger.info(f"File {file_list_path} does NOT exist.")
        zip_files = [INPUT_PATH / file for file 
                     in os.listdir(INPUT_PATH) 
                     #if file=='gettysburg.zip'
                     #if REGEX_INPUT_FILES_NAMES in file
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
        logger.info(f'End ingest file location from {INPUT_PATH} with count of files: {len(sound_files_list)}')

    #run workflow on batches
    logger.info("Begin workflow on each batch")
    for idx, batch in enumerate( get_next_batch(sound_files_list, BATCH_COUNT) ):
        pdfs = run_workflow(
            sound_files=batch, 
            intermediate_save_dir=INTERMEDIATE_PATH
            )
        logger.info("End workflow")

        #export
        logger.info("Begin export")
        file_path = OUTPUT_PATH / f'VDI_ApplicationStateData_v0.2.1-{idx+1}.gz'
        check = utils.export_to_vdi_workspace(workspace_schema, pdfs, file_path)
        logger.info(f"Data processed for batch-{idx+1}: {check}")

    logger.info(f"End process, execution took: {round(time.time() - start_time, 3)}sec")



if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("input", help="Required positional argument")
    parser.add_argument("batch_count", help="Required positional argument")

    # Optional argument flag to prepare the models (defaults to False)
    parser.add_argument("-p", "--prepare_models", action="store_true", default=False)

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)