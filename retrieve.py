# retrieve.py
# build an index of documents to be downloaded from the Gulflink site
from urllib.parse import urljoin
import re

import scrapelib
from lxml import etree

import util

def _concat_trees(etrees):
    root = etree.Element("html")
    body = root.SubElement("body")
    pre = body.SubElement("pre")
    contents = []
    for et in etrees:
        contents.append(et.xpath('/html/body/pre')[0].text)
    pre.text = '\n'.join(contents)
    return root

def retrieve_document_etree(url, scraper=None):
    if scraper is None:
        scraper = scrapelib.Scraper()
    tmpfile, resp = scraper.urlretrieve(url)
    match = re.search("Total Pages: *(\d+)", resp.content)
    pg_cnt = int(match.group(1))
    etrees = []
    while pg_cnt > 0:
        etrees.append(util.parse_etree(tmpfile))
        pg_cnt -= 1
        a_s = etrees[-1].xpath('/html/body/p[1]/font/a')
        for aa in a_s:
            if aa.text == "Next":
                url = urljoin("http://www.gulflink.osd.mil/", aa.attrib['href'])
    page = _concat_trees(etrees)
    return page

def default_handler(doc_tree):
    # prints the document to stdout
    print(etree.tostring(doc_tree))

def retrieve(inv, download_handler=default_handler, limit=None, scraper=None):
    if scraper is None:
        scraper = scrapelib.Scraper()
    if limit is None:
        for doc in inv:
            et = retrieve_document_etree(doc['link'], scraper)
            download_handler(et)
    else:
        pass
