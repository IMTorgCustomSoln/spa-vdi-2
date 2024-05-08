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
from datetime import datetime

from src.prepare_models import finetune
from src.asr import run_workflow
from src.modules import utils

sys.path.append(Path('config').absolute().as_posix() )
from _constants import (
    logging_dir,
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


def infer(args, CONFIG):
    """Run batches through model pipelines to get intermediate files.
    
    TODO: re-run text classification models on intermediate files
    """
    '''
    batch_list_path = CONFIG['INTERMEDIATE_PATH'] / 'batch_list.json'
    if batch_list_path.is_file():
        with open(batch_list_path, 'r') as f:
            batches = json.load(f)
    else:
        batches = {}
    '''
    sound_files_list = []
    if not args.infer_from_remaining_list:
        #load sound files
        file_list_path = CONFIG['INTERMEDIATE_PATH'] / 'file_list.json'
        with open(file_list_path, 'r') as f:
            string_sound_files_list = json.load(f)
        sound_files_list = [Path(file) for file in string_sound_files_list]
    else:
        remaining_list_path = CONFIG['INTERMEDIATE_PATH'] / 'remaining_list.json'
        with open(remaining_list_path, 'r') as f:
            string_sound_files_dict = json.load(f)
        for k,v in string_sound_files_dict.items():
            string_sound_files_dict[k] = [Path(file) for file in string_sound_files_dict[k]]
            sound_files_list.extend( string_sound_files_dict[k] )
        #sound_files_list = [Path(file) for file in string_sound_files_list]

    #run complete workflow on batches
    if not args.infer_text_classify_only:
        logger.info("Begin workflow on each batch")
        for idx, batch in enumerate( utils.get_next_batch_from_list(sound_files_list, CONFIG['BATCH_COUNT']) ):
            #batch_files = [str(file) for file in batch]
            #batches[idx] = batch_files
            batch_files = run_workflow(
                args=args,
                CONFIG=CONFIG,
                sound_files=batch, 
                intermediate_save_dir=CONFIG['INTERMEDIATE_PATH']
                )
            #keys = len(batches.keys())
            #batches[keys+idx] = batch_files
            logger.info(f"End workflow, index: {idx}")

            '''
            #export
            logger.info("Begin export")
            file_path = CONFIG['OUTPUT_PATH'] / f'VDI_ApplicationStateData_v0.2.1-{idx+1}.gz'
            check = utils.export_to_vdi_workspace(workspace_schema, pdfs, file_path)
            logger.info(f"Data processed for batch-{idx+1}: {check}")
            '''

    #run only text classification piece of workflow
    else:
        for idx, batch in batches.items():
            batch_files = run_workflow(
                args=args,
                CONFIG=CONFIG,
                sound_files=batch, 
                intermediate_save_dir=CONFIG['INTERMEDIATE_PATH']
                )
            batches[keys+idx] = batch_files
            logger.info("End workflow")

    #with open(batch_list_path, 'w') as f:
    #    json.dump(batches, f)
    return True


def report(args, CONFIG):
    """Reports and indexes needed for correct processing

    * check / update `batch_list.json`
    * save list of unprocessed audio files
    * save text classification hits to DataFrame csv."""
    import pandas as pd

    #get all files
    file_list_path = CONFIG['INTERMEDIATE_PATH'] / 'file_list.json'
    if file_list_path.is_file():
        with open(file_list_path, 'r') as f:
            audio_files = json.load(f)
    
    #get currently processed files 
    '''
    batch_list_path = CONFIG['INTERMEDIATE_PATH'] / 'batch_list.json'
    if batch_list_path.is_file():
        with open(batch_list_path, 'r') as f:
            batches_from_batch_list = json.load(f)

    '''
    batches_from_file_dir = {}
    batches_from_file_dir['0'] = [file.resolve() for file in CONFIG['INTERMEDIATE_PATH'].glob('**/*')
                                  if ('_list' not in file.name
                                      and '_schema' not in file.name
                                      and '.json' in file.name
                                      )]
    batches = list(*batches_from_file_dir.values())
    
    #update batch_list.json if corrupt
    '''
    if 'batches_from_batch_list' in locals():
        if list(batches_from_file_dir.values()) != list(batches_from_batch_list.values()):
            batches = batches_from_file_dir
            s_batches = {}
            for idx, file_list in batches_from_file_dir.items():
                s_batches[idx] = [str(file) for file in file_list]
            with open(batch_list_path, 'w') as f:
                json.dump(s_batches, f)
        else:
            batches = batches_from_batch_list
    else:
        batches = batches_from_file_dir
        s_batches = {}
        for idx, file_list in batches_from_file_dir.items():
            s_batches[idx] = [str(file) for file in file_list]
        with open(batch_list_path, 'w') as f:
            json.dump(s_batches, f)
    '''
    
    #get results of previous run
    '''
    if 'batches_from_batch_list' in locals():
        files_processed_current_run = len( batches_from_batch_list )
        CONFIG['LOGGER'].info(f'count of currently run files is: {files_processed_current_run} ')
        with open(Path(logging_dir), 'r') as f:
            log_file = f.readlines()
        log_file.reverse()
        l_comments = list(map(lambda x: x.split(']')[1].strip(), log_file))
        last_indices = [idx for idx, item in enumerate(l_comments) if 'End workflow' in item]
        last_idx = last_indices[0] if len(last_indices)>1 else None
        if last_idx:
            first_idx = [idx for idx, item in enumerate(l_comments[last_idx:]) if 'Begin process' in item][0]
            last_datetime = datetime.strptime(
                log_file[last_idx].split('[I ')[1].split(' main')[0],
                '%y%m%d %H:%M:%S'
                )
            first_datetime = datetime.strptime(
                log_file[last_idx+first_idx].split('[I ')[1].split(' main')[0],
                '%y%m%d %H:%M:%S'
                )
            diff = (last_datetime - first_datetime).seconds
            CONFIG['LOGGER'].info(f'process required: {diff} sec')
    else:
        CONFIG['LOGGER'].info('currently run files are not available')
    '''
    
    #get list of unprocessed files
    if args.report_process_status:
        s_batches = set()
        for file in batches:
            s_batches.add( Path(file).name.replace('.json',''))
        s_audio_files = set()
        [s_audio_files.add( Path(file).name ) for file in audio_files]
        remaining_audio_files = list( s_audio_files.difference(s_batches) )
        remaining_audio_files_dict = {}
        for file in audio_files:
            p_name = Path(file).name
            acct_no = p_name.split('_')[0]
            if p_name in remaining_audio_files:
                if acct_no not in remaining_audio_files_dict.keys():
                    remaining_audio_files_dict[acct_no] = []
                if file not in remaining_audio_files_dict[acct_no]:
                    remaining_audio_files_dict[acct_no].append(file)

        CONFIG['LOGGER'].info(f'there are {len( s_batches )} processed')
        CONFIG['LOGGER'].info(f'there are {len(remaining_audio_files_dict)} remaining')

        remaining_path = CONFIG['INTERMEDIATE_PATH'] / 'remaining_list.json'
        with open(remaining_path, 'w') as f:
            json.dump(remaining_audio_files_dict, f)
        return True
    
    '''
    #export hits to csv for review
    if args.report_text_classify:
        intermediate_files = []
        for idx,lst in batches.items():
            for file in lst:
                p_file = Path(file)
                if p_file.is_file():
                    with open(file, 'r') as f:
                        dialogue = json.load(f)
                        for hit in dialogue['classifier']:
                            if hit != []:
                                hit['file_name'] = file
                                intermediate_files.append(hit)
                else:
                    logger.info(f"File not found: {str(p_file)}")
        raw = pd.DataFrame(intermediate_files)
        df = raw[pd.isna(raw['pred'])==False]
        df_path = CONFIG['INTERMEDIATE_PATH'] / 'hit_list.csv'
        df.to_csv(df_path, index=False)
        return True
    '''
    
    return False


def output(args, CONFIG):
    """Output whatever current intermediate files exist."""
    #json files
    '''
    batch_list_path = CONFIG['INTERMEDIATE_PATH'] / 'batch_list.json'
    if batch_list_path:
        with open(batch_list_path, 'r') as f:
            batches = json.load(f)
    else:
        CONFIG['LOGGER'].info('batch_list.json not available')
    
    remaining_list_path = CONFIG['INTERMEDIATE_PATH'] / 'remaining_list.json'
    with open(remaining_list_path, 'r') as f:
        remaining_list_dict = json.load(f)
    for k,v in remaining_list_dict.items():
        remaining_list_dict[k] = [Path(file) for file in remaining_list_dict[k]]
    '''
    intermediate_files = [file.resolve() for file in CONFIG['INTERMEDIATE_PATH'].glob('**/*')
                                  if ('_list' not in file.name
                                      and '_schema' not in file.name
                                      and '.json' in file.name
                                      )]
    intermediate_files_dict = {}
    for file in intermediate_files:
        key = file.name.split('_')[0]
        if key in intermediate_files_dict.keys():
            intermediate_files_dict[key].append(file)
        else:
            intermediate_files_dict[key] = []
            intermediate_files_dict[key].append(file)

    batch_items = utils.get_next_batch_from_dict(
        dictn=intermediate_files_dict, 
        batch_count=CONFIG['BATCH_COUNT']
        )

    #workspace
    schema = CONFIG['INTERMEDIATE_PATH'] / 'workspace_schema_v0.2.1.json'
    if schema:
        with open(schema, 'r') as f:
            workspace_schema = json.load(f)
    else:
        CONFIG['LOGGER'].info('workspace_schema_v0.2.1.json not available')

    #run workflow on batches
    logger.info("Begin workflow on each batch")
    for idx, batch_dict in enumerate(batch_items):
        batch_dialogues = []
        for acct, files in batch_dict.items():
            acct_dialogues = []
            for file in files:
                file_path = Path(file)
                if file_path.is_file():
                    with open(file_path, 'r') as f:
                        dialogue = json.load(f)
                        acct_dialogues.append(dialogue)
            acct_file = utils.combine_account_files(acct_dialogues)             
            batch_dialogues.extend(acct_file)

        #export
        logger.info("Begin export")
        if args.output_type_excel:
            output_path = CONFIG['OUTPUT_PATH'] / f'batch-{int(idx)+1}.xlsx'
            check = utils.export_to_output(workspace_schema, batch_dialogues, output_path, 'excel')
        else:
            output_path = CONFIG['OUTPUT_PATH'] / f'VDI_ApplicationStateData_v0.2.1-{int(idx)+1}.gz'
            check = utils.export_to_output(workspace_schema, batch_dialogues, output_path, 'vdi_workspace')
        logger.info(f"Data processed for batch-{int(idx)+1}: {check}")



def main(args):
    """ Main entry point of the app. """
    logger.info("Begin process")
    start_time = time.time()

    CONFIG = {}
    try:
        CONFIG['LOGGER'] = logger
        CONFIG['INPUT_PATH'] = Path(args.input)
        #TODO:add UNZIPPED
        #TODO:add loaded models
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
        infer(args, CONFIG)
    elif args.task == 'report':
        report(args, CONFIG)
    elif args.task == 'output':
        output(args, CONFIG)
    elif args.task == 'all':
        prepare(args, CONFIG)
        infer(args, CONFIG)
        report(args, CONFIG)
        output(args, CONFIG)
    else:
        pass

    logger.info(f"End process, execution took: {round(time.time() - start_time, 3)}sec")
    return True






if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required (or with default) positional argument
    parser.add_argument("task", 
                        choices=['prepare', 'infer', 'report', 'output', 'all'],
                        help="Required positional argument")
    
    #if parser.parse_args().task in ['infer', 'output']:
    parser.add_argument("input", 
                        help="Required positional argument")
    parser.add_argument("batch_count", 
                        help="Required positional argument")

    #prepare
    #if parser.parse_args().task=='prepare':
    parser.add_argument("-m", "--prepare_models", action="store_true", default=False)
    parser.add_argument("-s", "--prepare_schema", action="store_true", default=False)
    parser.add_argument("-f", "--prepare_file_list", action="store_true", default=False)

    #infer options
    parser.add_argument("-c", "--infer_text_classify_only", action="store_true", default=False)
    parser.add_argument("-r", "--infer_from_remaining_list", action="store_true", default=False)

    #report options
    parser.add_argument("-p", "--report_process_status", action="store_true", default=False)
    parser.add_argument("-t", "--report_text_classify", action="store_true", default=False)

    #output options
    parser.add_argument("-e", "--output_type_excel", action="store_true", default=False)


    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)