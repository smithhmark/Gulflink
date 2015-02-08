# index.py
# build an index of documents to be downloaded from the Gulflink site
import scrapelib
from lxml import etree
from urllib.parse import urljoin

def index_all():
    pass

def _find_decalss_sources(root):
    dept_page_link_xpath = "/html/body/table/tr/td/blockquote/ul[2]/li/a"
    pages = root.xpath(dept_page_link_xpath)
    return pages

def _parse_etree(file_obj, html_parser=None):
    if html_parser is None:
        html_parser = etree.HTMLParser()
    root = etree.parse(file_obj, html_parser)
    return root

def _get_agency_paths(scraper):
    top_browse_url = "http://www.gulflink.osd.mil/search/browse.html"
    tmpfile, resp = scraper.urlretrieve(top_browse_url)
    #print(resp.headers)
    #print(len(resp.content))
    root = _parse_etree(tmpfile)
    #print(root)
    pages = _find_decalss_sources(root)
    agency_data = []
    for page in pages:
        agency_long = page.text
        agency_path = page.attrib['href']
        agency_data.append((agency_long, agency_path))
    return agency_data

def _get_releases(ag_url, scraper):
    tmpfile, resp = scraper.urlretrieve(ag_url)
    root = _parse_etree(tmpfile)
    rel_xpath = "/html/body/table/tr/td[2]/ul/li/a"
    rel_links = root.xpath(rel_xpath)
    ret_val = []
    for release in rel_links:
        href = release.attrib['href']
        bits = href.split('/')
        date_num = int(bits[-2])
        link = urljoin(ag_url, href)
        text = release.text
        date_text = text.split(':')[1].strip()
        ret_val.append((date_text, date_num, link))
    return ret_val

def test_get_releases():
    scraper = scrapelib.Scraper()
    test_url = "http://www.gulflink.osd.mil/declassdocs/dia/"
    return  _get_releases(test_url, scraper)

def _process_release(rurl, scraper):
    tmpfile, resp = scraper.urlretrieve(rurl)
    root = _parse_etree(tmpfile)
    doc_xpath = '//p[class="main"]'
    doc_paras = root.xpath(doc_xpath)
    ret_val = []
    for doc in doc_paras:
        title = doc.text.strip()
        href = doc[1].attrib['href']
        bits = href.split('/')
        link = urljoin("http://www.gulflink.osd.mil/", href)
        ret_val.append((title, link))
    return ret_val

def _inventory_agency(agency_data, scraper):
    long_name, path = agency_data
    ag_url = urljoin("http://www.gulflink.osd.mil/", path)
    #print(long_name, ag_url)
    inv = []

    ag_rels = _get_releases(ag_url, scraper)
    docs = []
    for date_str, date_int, rel_url in ag_rels:
        rel_docs = _process_release(rel_url, scraper)
        docs.extend(rel_docs)
    return inv

def index_declass(scraper=None):
    if scraper is None:
        scraper = scrapelib.Scraper()

    agency_data = _get_agency_paths(scraper)

    inventory = []
    for agency in agency_data:
        inventory.extend(_inventory_agency(agency, scraper))
