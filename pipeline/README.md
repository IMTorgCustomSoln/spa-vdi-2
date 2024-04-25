


## Usage

Prepare `.env` file with `HF_TOKEN`, `HF_HOME`.

```
pipenv install
pipenv install Jinja2
pipenv install --upgrade Jinja2     #fixes breaking error




```



## Note

* use `whisper-large`, [ref](https://huggingface.co/openai/whisper-large-v2#long-form-transcription)
* `taunt-FAILS.wav` fails without error
* chunk_length_s [explanation](https://huggingface.co/blog/asr-chunking)



## TODO

* migrate to spa_v2
* output to Workspace file
  - doc to DocumentRecord
  - document, index and topics, notes
  - reuse existing code by running node script to process?
  - compress to zip
  - test it can be uploaded
* How to add classifier metadata so that it highlights hits in selected search?