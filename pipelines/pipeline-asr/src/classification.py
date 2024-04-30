#!/usr/bin/env python3
"""
Module Docstring

"""

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
    KEYWORDS = kw_lines     #['ill', 'sick', 'unemployed', 'child']

    result = {
        'search': 'KW',
        'target': None,
        'timestamp': None,
        'pred': None
        }
    for word in KEYWORDS:
        if word in chunk['text']:
            result['target'] = word
            result['timestamp'] = chunk['timestamp']
            result['pred'] = 1.0
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
    probs = model.predict_proba(chunk['text'])
    if probs[1] > .5:
        result['target'] = chunk['text']
        result['timestamp'] = chunk['timestamp']
        result['pred'] = 1.0
        return result
    
    return None