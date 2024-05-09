


## Usage

Expects a directory of either: i) compressed audio files or ii) single audio files.

Prepare `.env` file with:

* `HF_TOKEN` - account
* `HF_HOME` - model files directory
* `CURL_CA_BUNDLE` - public key (.pem) cert

Ensure dependencies are correct.  You may have to upgrade with the following: `pip install --upgrade s3fs fsspec`

Change `src/asr.py` at `asr_pipeline = pipeline(...` to `whisper-large`.

Install [styled_text](https://github.com/IMTorgOpenDataTools/styled-text) the usual way.

```
$ pipenv install
```


Ensure you are in directory `pipelines/pipeline-asr/`, then to use the provided audio `samples/`:

```
$ pipenv run python main.py --version
$ pipenv run python main.py samples/ 4 --prepare_models
```

Review `logs/process.log` and obtain `samples/OUTPUT/VDI_ApplicationStateData_v0.2.1-XXX.gz` where `XXX` refers to the batch number.

You may also want to run in the background with `nohup`.  To do this:

```bash
$ nohup python main.py infer samples/ 4 --infer_from_remaining_list; echo 'Job finished at:' $(date); &
```

Then, review running jobs with: `$ jobs`


## Performance

Using a g5.4xlarge: RHEL8, 16vCPU, 64GB RAM, with A100 gpu (24GB video memory), we can get throughput of ~35 audio files / minute.

```python
from datetime import datetime

tm1 = '240503 19:13:12'
tm2 = '240506 12:48:13'
rt1 = datetime.strptime(tm1, '%y%m%d %H:%M:%S')
rt2 = datetime.strptime(tm2, '%y%m%d %H:%M:%S')
37045 / (rt2 - rt1).seconds * 60
#35.1131
```


## Dev & Test

If using vscode, open in dev container and 'Add folder to workspace' > `pipelines/pipline-asr/`

```
pipenv run pytest --collect-only
/home/node/.local/share/virtualenvs/pipeline-asr-WU7QSYkE/bin/pytest --collect-only
```

A single test can be run with (-s displays stdout):

```
py.test tests/test_utils.py  -k 'test_export_to_output_excel_single_file' -s
```


## Note

* `pipenv install --upgrade Jinja2` may be needed to fixing breaking error
* use `whisper-large` if compute resources are available, [ref](https://huggingface.co/openai/whisper-large-v2#long-form-transcription)
* unknown `taunt-FAILS.wav` fails without error
* chunk_length_s [explanation](https://huggingface.co/blog/asr-chunking)



## TODO:list

* ~~migrate to spa_v2~~
* ~~output to Workspace file~~
  - ~~doc to DocumentRecord~~
  - ~~document, index and topics, notes~~
  - ~~reuse existing code by running node script to process?~~
  - ~~compress to zip~~
  - ~~test it can be uploaded~~
* ~~add classifier metadata so that it highlights hits in selected search?~~
* logging
  - ~~all files ingested~~
  - ~~processing time~~
  - ~~audio file errors => TODO:ISSUE - not possible~~
  - ~~accounting to validate all files processed~~
  - ~~all files included in a batch => each file is a batch and saved to intermediate json~~
* run
  - ~~via commandline from within workspace~~
  - ~~dirs: logs, output (dated)~~
  - ~~separate preparation (finetune) from workflow~~
  - ~~load from intermediate files (.json)~~
  - ~~create Workspace from current output~~
  - ~~multiple audio files per zip~~
  - convenience functions:
    + 
    + ~~compare file_list.json???~~
* process batch
  - ~~intermediate .json files are correct~~
  - ~~prepare example files~~
  - ~~setup remainder_list.json~~
  - run on batches
    + ~~get all .json files (root and subdirs)~~
    + ~~sort on: acct_date_index~~
    + ~~group by: acct~~
    + ~~mod batch to group by acct~~ 
    + NO ~~combine audio files into one document, separate pages <--- AUDIO FILE ${file_name} --->~~ should they be combined??? => NO b/c harder to determine audio file => KEEP IN SAME BATCH
* output: excel
  - fix styling
  - fix error `usupported operand type(s) for +:  'float' and 'NoneType' 
  - ~~round timestamps~~
  - ~~fix duplicates~~ => empty sound
  - ~~fix empties~~
* output: workspace
  - incorrect image (follow from client)
* design
  - oop design
  - ~~add batching to pipeline~~
  - integrate EnteroDoc
  - ...
  - ~~add total audio length - where?~~ => use lines for Sentences
* Performance testing
    + audio per second processed, by machine
    + workspace size (mb) per audio size (mb)
    + vdi import limitations
    + => determine zip file batching, 100 .json files
* reporting: accounting by acct
  - number of accounts
    + audio files per acct
* product
  - ~~deploy client, awaiting~~
  - ~~table: acct, score sort~~