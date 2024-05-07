#!/usr/bin/env python3
"""
Module Docstring

ref: https://github.com/huggingface/transformers/issues/23231
"""

from src.modules import utils



dialogue = {
        "text": " Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. Nor is Mr. Quilter's manner less interesting than his matter. Nor is Mr. Quilter's",
        "chunks": [
            {
                "timestamp": (0.0, 6.0),
                "text": " Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel.",
            },
            {
                "timestamp": (6.0, 11.0000000999999),
                "text": " Nor is Mr. Quilter's manner less interesting than his matter.",
            },
            {"timestamp": (11.0000000999999, None), "text": " Nor is Mr. Quilter's"},
        ],
    }




def test_format_dialogue():
    mod_dialogue = utils.format_dialogue_timestamps(dialogue)
    assert mod_dialogue == [
        '(0.0, 6.0)  -   Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. \n', 
        "(6.0, 11.0)  -   Nor is Mr. Quilter's manner less interesting than his matter. \n", 
        "(11.0, None)  -   Nor is Mr. Quilter's \n"
        ]
    
def test_output_to_pdf():
    mod_dialogue = [
        '(0.0, 6.0)  -   Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. \n', 
        "(6.0, 11.0)  -   Nor is Mr. Quilter's manner less interesting than his matter. \n", 
        "(11.0, None)  -   Nor is Mr. Quilter's \n"
        ]
    mod_dialogue = [
        '(0.0, None)  -   Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel. \n', 
        ]
    pdf = utils.output_to_pdf(dialogue, mod_dialogue, output_type='str')
    assert True == True