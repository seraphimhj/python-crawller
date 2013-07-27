import sys
import re
import urllib2
import re
import mechanize
import json
import string
import socket
import time
from threading import Thread, Lock
from Queue import Queue
from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulSoup, SoupStrainer

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
header = {"User-Agent": user_agent}
socket.setdefaulttimeout(100) 
shop_list = {}

class Crawler:
    def __init__(self, nthread, fout):
        proxy_handler = urllib2.ProxyHandler({"http" : "http://172.19.1.2:9217"})
        self.opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
        #self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        self.lock = Lock()
        self.q_req = Queue()
        self.q_ans = Queue()
        self.nthread = nthread
        for i in range(nthread):
            t = Thread(target = self.threadget)
            t.setDaemon(True)
            t.start()
        self.running = 0
        self.fout = fout

    def __del__(self):
        time.sleep(0.5)
        self.q_req.join()
        self.q_ans.join()

    def taskleft(self):
        return self.q_req.qsize() + self.q_ans.qsize() + self.running

    def push(self, req):
        self.q_req.put(req)

    def pop(self):
        ans = self.q_ans.get()
        #parser_shop(ans)
            
    def parser_shop(self, page):
        f = self.fout
        try:
            shop_ss = SoupStrainer('div', attrs={"class": "section"})
            shop = BeautifulSoup(page, parseOnlyThese=shop_ss)
            shopname = shop.find('h1', attrs={"class":"shop_title"}).string
            f.write("%s\t" % shopname)
            abstract = shop.find('div', attrs={"class":"comment-rst"})
            if len(abstract.span.contents) != 0:
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
    
    def threadget(self):
        while True:
            req = self.q_req.get()
            with self.lock:
                self.running += 1
            try:
                ans = self.opener.open(req).read()
                self.parser_shop(ans)
                self.fout.flush()
            except Exception, what:
                ans = ""
                print what
            self.q_ans.put((req, ans))
            with self.lock:
                self.running -= 1
            self.q_req.task_done()
            time.sleep(0.1)

def load_shop(fname):
    f = open(fname, "r")
    for line in f.readlines():
        segs = line.split("\t")
        if segs[0] not in shop_list:
            shop_list[segs[0]] = 1
    f.close()
                        

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
    load_shop("shoplist")
    f = open("shoplist", "a+")
    f_url = open("shop_urls", "w")
    crawler = Crawler(10, f)
    for i in range(2104, 2281):
        cate_url = "http://www.dianping.com/search/category/2/10/r%d" % i
        print "cate:%d, %s" % (i, cate_url)
        request = urllib2.Request(cate_url, "", header)
        cate_page = urllib2.urlopen(request)
        pagelist_ss = SoupStrainer('a', attrs={"class": "PageLink"})
        pagelist = BeautifulSoup(cate_page, parseOnlyThese=pagelist_ss)
        if len(pagelist.findAll('a', "PageLink")) != 0:
            total_page = int(pagelist.findAll('a', {"class": "PageLink"})[-1].string)
        else:
            total_page = 0
        print "total_page:%d" % total_page
        for j in range(1, total_page+1):
            print "page:%d" % j
            shoplist_url = cate_url + "p%d" % j
            request = urllib2.Request(shoplist_url, "", header)
            shoplist_page = urllib2.urlopen(request)
            shoplist_ss = SoupStrainer('a', attrs={"class": "BL", "href": re.compile('shop')})
            shoplist = BeautifulSoup(shoplist_page, parseOnlyThese=shoplist_ss)
            i = 0
            for a in shoplist:
                i = i + 1
                print "shop:%d" % i
                shop_url = "http://www.dianping.com/%s" % a.get('href')
                if shop_url in shop_list:
                    continue
                else:
                    shop_list[a.string] = 1
                f_url.write("%s\t%s\n" % (a.string.encode('utf-8'), shop_url.encode('utf-8')))
                request = urllib2.Request(shop_url, "", header)
                crawler.push(request)
            shoplist.decompose()
        pagelist.decompose()
    while crawler.taskleft():
        crawler.pop()
    f_url.close()
    f.close()
    #crawl_shop("http://www.dianping.com//shop/4174680", f)
    #crawl_shop("http://www.dianping.com//shop/3215488", f)
