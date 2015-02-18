#
#
#

import re

DOF_TYPES = [
    'IIR',
    'CMAT',
    ]

SNIFFS = {
        "IIR": [
            r'^SUBJ(ECT)? *: *IIR',
            r'^ *SERIAL: *IIR',
            ],
        "CMAT": [
            r'^ *CMAT NUMBER',
            r'^ *SERIAL: *DSA',
            ],
        }

def sniff_doctype(text):
    """Use the document text to determine the type of the document.
    """
    matched_types = []
    for dtyp, tests in SNIFFS.items():
        tmprexp = '|'.join(tests)
        match = re.search(tmprexp, text) ### not at all clever...
        if match:
            matched_types.append(dtyp)
    print("[+] matched on:", matched_types)
    return matched_types

def process_IIR(text):
    """extract the known fields from an IIR
    """
    # find and process headers
    # split paragraphs
    # 
    pass
