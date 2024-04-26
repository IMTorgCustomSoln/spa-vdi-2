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

from src.prepare_models import finetune
from src.asr import run_workflow
from src.modules import utils

sys.path.append(Path('config').absolute().as_posix() )
from _constants import (
    logger
)



def main(args):
    """ Main entry point of the app. """
    logger.info("Begin process")
    start_time = time.time()

    try:
        INPUT_PATH = Path(args.input)
        INTERMEDIATE_PATH = (INPUT_PATH / 'tmp').mkdir(parents=True, exist_ok=True)
    except:
        logger.info(f"End process, execution took: {round(time.time() - start_time, 3)}sec")
        sys.exit()


    #prepare
    if args.prepare_models:
        logger.info("Begin prepare_models")
        check_prepare = finetune()
        if not check_prepare: 
            logger.info(f"models failed to prepare")
            exit()
        logger.info("End prepare_models")

    #ingest
    logger.info("Begin ingest file location")
    zip_files = [INPUT_PATH / file for file 
                 in os.listdir(INPUT_PATH) 
                 #if '_Calls_' in file
                 ]
    sound_files_list = []
    for file in zip_files:
        extracted_sound_files = utils.get_decompressed_filepath(
            filepath=file,
            target_extension=['.wav','.mp3']
            )
        sound_files_list.extend(extracted_sound_files)
    logger.info(f'End ingest file location from {INPUT_PATH} with count of files: {len(sound_files_list)}')

    #run workflow
    logger.info("Begin workflow")
    pdfs = run_workflow(
        sound_files=sound_files_list, 
        intermediate_save_dir=INTERMEDIATE_PATH
        )
    logger.info("End workflow")

    #export
    logger.info("Begin export")
    check = utils.export_to_vdi_workspace(pdfs)

    logger.info(f"data processed: {check}")
    logger.info(f"End process, execution took: {round(time.time() - start_time, 3)}sec")



if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("input", help="Required positional argument")

    # Optional argument flag to prepare the models (defaults to False)
    parser.add_argument("-p", "--prepare_models", action="store_true", default=False)

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)