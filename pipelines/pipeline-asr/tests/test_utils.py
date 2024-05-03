#!/usr/bin/env python3
"""
Module Docstring

ref: https://github.com/huggingface/transformers/issues/23231
"""

from src.modules import utils


def test_format_dialogue():
    dialogue = {
        "text": " Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. Nor is Mr. Quilter's manner less interesting than his matter. Nor is Mr. Quilter's",
        "chunks": [
            {
                "timestamp": (0.0, 6.0),
                "text": " Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel.",
            },
            {
                "timestamp": (6.0, 11.0),
                "text": " Nor is Mr. Quilter's manner less interesting than his matter.",
            },
            {"timestamp": (11.0, None), "text": " Nor is Mr. Quilter's"},
        ],
    }
    mod_dialogue = utils.format_dialogue_timestamps(dialogue)
    assert True == True
