#!/usr/bin/env python3
"""
Module Docstring

"""

#TODO:from nltk.tokenize import word_tokenize 

from pathlib import Path


def classifier(chunk):
    """Importable function to run assigned models."""
    result = []
    models = [
        kw_classifier,
        phrase_classifier,
        fs_classifier
    ]
    for model in models:
        result.append( model(chunk) )

    return result


def kw_classifier(chunk):
    """..."""

    data_path = Path('./src/data')
    with open(data_path / 'pos_kw.txt', 'r') as file:
        kw_lines = file.readlines()
    KEYWORDS = [word.replace('\n','') for word in kw_lines]

    result = {
        'search': 'KW',
        'target': None,
        'timestamp': None,
        'pred': None
        }
    hits = []
    for word in KEYWORDS:
        if word in chunk['text']:
            hits.append(word)
    #words = word_tokenize(chunk['text'])
    if len(hits)>0:
            result['target'] = ' '.join(hits)
            result['timestamp'] = chunk['timestamp']
            result['pred'] = len(hits) / len(chunk['text'])
            return result
    else:
        return None
    

def phrase_classifier(chunk):
    """..."""
    return None


def fs_classifier(chunk):
    """..."""

    #from transformers import AutoModel
    from setfit import SetFitModel

    from pathlib import Path

    result = {
        'search': 'FS',
        'target': None,
        'timestamp': None,
        'pred': None
        }
    model_path = Path("pretrained_models/finetuned--BAAI")
    model = SetFitModel.from_pretrained(model_path)
    if len(chunk['text']) > 40:
        probs = model.predict_proba(chunk['text'])
        pos_idx = model.labels.index('positive')
        prob_positive = probs.tolist()[pos_idx]
        if prob_positive > .5:
            result['target'] = chunk['text']
            result['timestamp'] = chunk['timestamp']
            result['pred'] = prob_positive
            return result
    return None