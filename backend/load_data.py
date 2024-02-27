"""
Load test data into the database
"""

import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from api.models import Examiner, DocumentGroup, Document


def run():
    """
    Assumptions:
    * 150 total documents
    * 15 docgrps of 10 documents, each
    * 3 examiners with access to all docgrps
    """
    docgrps = []
    for idx in range(1, 16):
        docgrp = DocumentGroup(name=f'exam-1_grp-{idx}')
        docgrp.save()
        docgrps.append(docgrp)

    for docgrp in docgrps:
        for idx in range(1, 11):
            doc = Document(name=f'doc-{random.randrange(1000,9999)}',
                           docgrp = docgrp,
                           bytes = random.randrange(100, 500),
                           metadata = '{title:"Doc Title"}',
                           uintarray = '[0,1,2,3,4,5]'
                         )
            doc.save()

    for idx in range(1, 4):
        e = Examiner(name=f'user-{idx}')
        e.save()
        for docgrp in docgrps:
            e.docgrp.add(docgrp)


if __name__ == '__main__': 
    run()