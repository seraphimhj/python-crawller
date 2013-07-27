import sys
import re
import urllib2
from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re
import mechanize
import json
import string

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
header = {"User-Agent": user_agent}
shop_list = {}

import socket
socket.setdefaulttimeout(10) 

def load_shop(fname):
    f = open(fname, "r")
    for line in f.readlines():
        segs = line.split("\t")
        print segs[0]
        shop_list[segs[0]] = 1
    f.close()
     
def crawl_page(cate_url, f):
    request = urllib2.Request(cate_url, "", header)
    cate_page = urllib2.urlopen(request)
    pagelist_ss = SoupStrainer('a', attrs={"class": "PageLink"})
    pagelist = BeautifulSoup(cate_page, parseOnlyThese=pagelist_ss)
    total_page = int(pagelist.findAll('a', {"class": "PageLink"})[-1].string)
    for i in range(1, total_page+1):
        print "page:%d" % i
        page_url = cate_url + "p%d" % i
        crawl_cate(page_url, f)
    
def crawl_cate(cate_url, f):
    request = urllib2.Request(cate_url, "", header)
    cate_page = urllib2.urlopen(request)
    shoplist_ss = SoupStrainer('a', attrs={"class": "BL", "href": re.compile('shop')})
    shoplist = BeautifulSoup(cate_page, parseOnlyThese=shoplist_ss)
    i = 0
    for a in shoplist:
        i = i + 1
        print "shop:%d" % i
        shop_url = "http://www.dianping.com/%s" % a.get('href')
        if shop_url in shop_list:
            continue
        else:
            shop_list[a.string] = 1
        f.write("%s\t%s\t" % (a.string.encode('utf-8'), shop_url.encode('utf-8')))
        crawl_shop(shop_url, f)
    shoplist.decompose()
    
def crawl_shop(shop_url, f):
    try:
        request = urllib2.Request(shop_url, "", header)
        shop_page = urllib2.urlopen(request)
        shop_ss = SoupStrainer('div', attrs={"class": "section"})
        shop = BeautifulSoup(shop_page, parseOnlyThese=shop_ss)
        abstract = shop.find('div', attrs={"class":"comment-rst"})
        f.write("%s\tprice:%s\t" % (abstract.span.contents[-1].rstrip().encode('utf-8'), abstract.dl.dd.contents[1].encode('utf-8')))
        detail = shop.find('div', attrs={"class":"desc-list"}).findAll('dl')
        f.write("%s%s\t" % (detail[0].dt.string.encode('utf-8'), detail[0].em.string.encode('utf-8')))
        f.write("%s%s\t" % (detail[1].dt.string.encode('utf-8'), detail[1].em.string.encode('utf-8')))
        f.write("%s%s\t" % (detail[2].dt.string.encode('utf-8'), detail[2].em.string.encode('utf-8')))
        address = detail[3].dt.string + detail[3].span.string + detail[3].findAll('span')[1].string or ""
        string.replace(address, "\n", "")
        f.write("%s\t" % address.encode('utf-8'))
        tele = detail[4].dt.string + detail[4].strong.string or ""
        f.write("%s\t" % tele.encode('utf-8'))
        f.write("%s" % detail[5].dt.string.encode('utf-8'))
        for tag in detail[5].findAll('span'):
            tag_str = tag.a.string or ""
            string.replace(tag_str, "\n", "")
            f.write("%s," % tag_str.encode('utf-8'))
        f.write("\t")
        tmp = shop.find('div', attrs={"class":"rec-menu"})
        if tmp != None:
            menu = tmp.findAll('a') 
            if menu != None:
                f.write("menu:")
                for food in menu:
                    food_str = food.string or ""
                    f.write("%s," % food_str.encode('utf-8'))
                f.write("\t")
        tmp = shop.find('div', attrs={"class":"chara-con J_new-chara-con"})
        if tmp != None:
            features = tmp.findAll('a')
            if features != None:
                for fea in features:
                    f.write("%s," % fea.string.encode('utf-8'))
                f.write("\t")
        tmp = shop.find('div', attrs={"class":"block-inner desc-list"})
        if tmp != None:
            more_info = tmp.findAll('dl')
            if more_info != None:
                for info in more_info:
                    f.write(info.dt.string.encode('utf-8'))
                    if info.dd.find('span'):
                        if info.dd.span.find('a'):
                            for tag in info.dd.findAll('a', {"rel":"tag"}):
                                f.write("%s," % tag.string.encode('utf-8'))
                            f.write("\t")
                        else:
                            f.write("%s\t" % info.dd.span.string.rstrip().encode('utf-8'))
                    else:
                        f.write("%s\t" % info.dd.string.rstrip().encode('utf-8'))
                   
        f.write("\n")
        shop.decompose()
    except Exception, e:
        f.write("\n")
        print "No Information:", e
        pass  

def get_latlng(address):
    query = "http://maps.googleapis.com/maps/api/geocode/json?address=" + address
    query = "http://maps.google.com/maps/geo?q=" + address
    page = urllib2.urlopen(query)
    #print page
    map_data = json.load(page)
    #print type(map_data)
    if map_data["Status"]["code"] == 200:
        #print map_data["Placemark"][0]["Point"]["coordinates"]
        print address, map_data["Placemark"][0]["Point"]["coordinates"]
    else:
        print address, "Not Found"
    
if __name__ == "__main__":
    #if len(sys.argv) < 2:
    #    print "Error argc!"
    #    pass
    #get_latlng(sys.argv[1])
    f = open("shoplist", "a+")
    load_shop("shoplist")
    for i in range(2104, 2281):
        cate_url = "http://www.dianping.com/search/category/2/10/r%d" % i
        print "cate:%d" % i
        crawl_page(cate_url, f)
        f.flush()
    f.close()
    #crawl_shop("http://www.dianping.com//shop/4174680", f)
    #crawl_shop("http://www.dianping.com//shop/3215488", f)
