# index.py
# build an index of documents to be downloaded from the Gulflink site
from lxml import etree
from urllib.parse import urljoin
import pickle
import sys

import scrapelib

import util

def index_all():
    pass

def _find_decalss_sources(root):
    dept_page_link_xpath = "/html/body/table/tr/td/blockquote/ul[2]/li/a"
    pages = root.xpath(dept_page_link_xpath)
    return pages

def _get_agency_paths(scraper):
    top_browse_url = "http://www.gulflink.osd.mil/search/browse.html"
    tmpfile, resp = scraper.urlretrieve(top_browse_url)
    #print(resp.headers)
    #print(len(resp.content))
    root = util.parse_etree(tmpfile)
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
    root = util.parse_etree(tmpfile)
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
    rel_docs = _inventory_release_documents(rel_url, scraper, 
            "dummydate", "dia")
    return rel_docs

def _mine_doc_url(durl):
    bits = durl.split('/')
    agency = bits[2]
    reldate = bits[3]
    return agency, reldate

def _clean_title(old_title):
    title = old_title.strip()
    title = "".join(title.split('\n'))
    title = "".join(title.split('\t'))
    title = " ".join([bit.strip() for bit in title.split()])
    return title

def _inventory_release_documents(rurl, scraper):
    ## returns a list of {title:t, link:l} tuples
    tmpfile, resp = scraper.urlretrieve(rurl)
    #print(resp.code)
    if resp.code < 200 or resp.code >= 300:
        print('[-] release url failed:', rurl)
        return []
    root = util.parse_etree(tmpfile)
    doc_xpath = '//tr/td/p'
    doc_paras = root.xpath(doc_xpath)
    #print(doc_paras)
    ret_val = []
    for doc in doc_paras:
        links = doc.xpath('./a')
        ### need to search through found links for the link with "ascii text"
        if len(links) == 1:
            title = _clean_title(doc.text)
            href = links[0].attrib['href']
            link = urljoin("http://www.gulflink.osd.mil/", href)
            agency, rel_date = _mine_doc_url(link)
            ret_val.append({"title": title, "link": link,
                "date":rel_date, "agency":agency})
    return ret_val

def _inventory_agency(agency_data, scraper):
    long_name, path = agency_data
    print("[+] tackling:", long_name)
    ag_url = urljoin("http://www.gulflink.osd.mil/", path)
    #short_ag = path.split('/')[-2]
    # print(long_name, ag_url, short_ag)
    inv = []
    releases = _get_releases(ag_url, scraper)
    if len(releases) ==0:
        print('[-] failed to find a release')
        return inv
    for date_str, date_int, rel_url in releases:
        print("[+]   beginning release:", date_str)
        rel_docs = _inventory_release_documents(rel_url, scraper)
        print("[+]   found ", len(rel_docs), " released docs")
        inv.extend(rel_docs)
    return inv

def inventory_declass(scraper=None):
    if scraper is None:
        scraper = scrapelib.Scraper()
    inventory = []
    agency_data = _get_agency_paths(scraper)
    for agency in agency_data:
        inventory.extend(_inventory_agency(agency, scraper))
    return inventory


def main():
    #config based on example at:github/olberger/scrapelib/docs/example/
    #        follow_robots=True, cache_obj=filecache, cache_write_only=False, 
    #        config={'verbose':sys.stderr}, raise_errors=False,
    scraper = scrapelib.Scraper(requests_per_minute=60, raise_errors=False)
    ofil = open("inventory.pickle", r'wb')
    inv = inventory_declass(scraper)
    print("[+] found ", len(inv), " total docs")
    pickle.dump(inv, ofil)

if __name__ == '__main__':
    main()
