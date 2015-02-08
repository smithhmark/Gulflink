# index.py
# build an index of documents to be downloaded from the Gulflink site
import scrapelib
from lxml import etree

def index_all():
    pass

def _find_decalss_sources(root):
    dept_page_link_xpath = "/html/body/table/tr/td/blockquote/ul[2]/li/a"
    pages = root.xpath(dept_page_link_xpath)
    return pages

def _parse_etree(file_obj, html_parser=None):A
    if html_parser is None:
        html_parser = etree.HTMLParser()
    root = etree.parse(file_obj, html_parser)
    return root

def index_declass(scraper=None):
    if scraper is None:
        scraper = scrapelib.Scraper()
    top_browse_url = "http://www.gulflink.osd.mil/search/browse.html"

    tmpfile, resp = scraper.urlretrieve(top_browse_url)
    print(resp.headers)
    print(len(resp.content))

    root = _parse_etree(tmpfile)

    print(root)

    return pages, root


