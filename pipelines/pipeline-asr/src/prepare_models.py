#!/usr/bin/env python3
"""
Module Docstring

"""

from pathlib import Path
import sys
import json

from src.modules import config_env

sys.path.append(Path('config').absolute().as_posix() )
from _constants import (
    logger
)
#TODO: logger.info("Begin prepare_models")


def finetune():
    """..."""

    config_env.config()

    #load model
    from setfit import SetFitModel

    model = SetFitModel.from_pretrained("BAAI/bge-small-en-v1.5")


    #get train / test records
    from datasets import load_dataset, Dataset

    data_path = Path('./src/data')
    with open(data_path / 'train.json', 'r') as file:
        train_records = json.load(file)['records']
    #train_dataset = load_dataset(records)         #<<<FAILS HERE, maybe use this: Dataset.from_dict(
    with open(data_path / 'pos_sentence.txt', 'r') as file:
        train_lines = file.readlines()
    recs = [{'text':line.replace('\n',''), 'label':'positive'} for line in train_lines]
    train_records.extend(recs)
    with open(data_path / 'neg_sentence.txt', 'r') as file:
        train_lines = file.readlines()
    recs = [{'text':line.replace('\n',''), 'label':'negative'} for line in train_lines]
    train_records.extend(recs)
    train_dataset = Dataset.from_list(train_records)

    with open(data_path / 'test.json', 'r') as file:
        test_records = json.load(file)['records']
    test_dataset = Dataset.from_list(test_records)

    model.labels = ["negative", "positive"]


    #train model
    from setfit import Trainer, TrainingArguments

    args = TrainingArguments(
        batch_size=25,
        num_epochs=10,
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
    )
    trainer.train()


    #test model
    metrics = trainer.evaluate(test_dataset)
    print(metrics)
    '''
    preds = model.predict([
        "I got the flu and felt very bad.",
        "I got a raise and feel great.",
        "This bank is awful.",
        ])
    print(f'predictions: {preds}')
    '''


    #save model
    model_path = Path("pretrained_models/finetuned--BAAI")
    model.save_pretrained(model_path )
    model2 = SetFitModel.from_pretrained(model_path )
    result = True
    if not model2:
        result = False
    return result