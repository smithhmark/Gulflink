from lxml import etree

def parse_etree(file_obj, html_parser=None):
    if html_parser is None:
        html_parser = etree.HTMLParser()
    root = etree.parse(file_obj, html_parser)
    return root
