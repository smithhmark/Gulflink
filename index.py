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

def test_inventory_release_documents():
    scraper = scrapelib.Scraper()
    rel_url = 'http://www.gulflink.osd.mil/declassdocs/dia/19971030/'
    rel_docs = _inventory_release_documents(rel_url, scraper, "date", "dia")
    return rel_docs

def _inventory_release_documents(rurl, scraper, date, agency):
    ## returns a list of {title:t, link:l} tuples
    tmpfile, resp = scraper.urlretrieve(rurl)
    #print(resp.code)
    root = _parse_etree(tmpfile)
    doc_xpath = '//tr/td/p'
    doc_paras = root.xpath(doc_xpath)
    #print(doc_paras)
    ret_val = []
    for doc in doc_paras:
        title = doc.text.strip()
        title = "".join(title.split('\n'))
        links = doc.xpath('./a')
        if len(links) == 1:
            href = links[0].attrib['href']
            link = urljoin("http://www.gulflink.osd.mil/", href)
            ret_val.append({"title": title, "link": link,
                "date":date, "agency":agency})
    return ret_val

def _inventory_agency(agency_data, scraper):
    long_name, path = agency_data
    ag_url = urljoin("http://www.gulflink.osd.mil/", path)
    short_ag = path.split('/')[-2]
    # print(long_name, ag_url, short_ag)
    inv = []
    ag_rels = _get_releases(ag_url, scraper)
    docs = []
    for date_str, date_int, rel_url in ag_rels:
        rel_docs = _inventory_release_documents(rel_url, 
                scraper, (date_int, date_str), short_ag)
        docs.extend(rel_docs)
    return inv

def index_declass(scraper=None):
    if scraper is None:
        scraper = scrapelib.Scraper()

    agency_data = _get_agency_paths(scraper)

    inventory = []
    for agency in agency_data:
        inventory.extend(_inventory_agency(agency, scraper))
