


## Usage

Expects a directory of either: i) compressed audio files or ii) single audio files.

Prepare `.env` file with `HF_TOKEN` (account), `HF_HOME` (model files directory).

Ensure you are in directory `pipelines/pipeline-asr/`, then to use the provided audio `samples/`:

```
pipenv run python main.py --version
pipenv run python main.py samples/
```

Review `logs/process.log` and obtain `result_output/VDI_ApplicationStateData_v0.2.1-XXX.gz` where `XXX` refers to the batch number.


## Dev & Test

If using vscode, open in dev container and 'Add folder to workspace' > `pipelines/pipline-asr/`

```
pipenv run pytest --collect-only
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
  - audio file errors => TODO:ISSUE - not possible
  - accounting to validate all files processed
  - ~~all files included in a batch => each file is a batch and saved to intermediate json~~
* run
  - ~~via commandline from within workspace~~
  - ~~dirs: logs, output (dated)~~
  - load from intermediate files
* models
  - ~~add batching to pipeline~~
  - integrate EnteroDoc
  - add total audio length - where?
  - performance testing
    + audio per second processed, by machine
    + workspace size (mb) per audio size (mb)
    + vdi import limitations
    + => determine zip file batching