#
#
#

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
    pass

def process_IIR(text):
    """extract the known fields from an IIR
    """
    # find and process headers
    # split paragraphs
    # 
    pass
