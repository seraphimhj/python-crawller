from weibo import APIClient
import sys
import urllib2
from BeautifulSoup import BeautifulSoup, SoupStrainer
import re
import mechanize
import json

def get_crawl_list():
    """
    file = open()
    """
    pass

def get_fiction_index_update():
    url = "http://www.qidian.com/BookReader/1639199.aspx"
    page = urllib2.urlopen("http://www.qidian.com/BookReader/1639199.aspx")
    charpter = SoupStrainer('li', style="width:33%;")
    soup = BeautifulSoup(page, parseOnlyThese=charpter)
    size = len(soup) - 1
    print soup.contents[size].contents[0]
    #print soup.contents[size].a.get('title')
    #for li in soup:
    #    print li.contents[0].contents[0] 
    #    print li.a.get('title')

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
    


def login_weibo():
    # OAUTH_consumer_key
    APP_KEY = '4286165328'
    # OAUTH_consumer_secret
    APP_SECRET = 'aefb6cf7e9f3b22e6a07af2d81fa3fdc'
    CALLBACK_URL = 'http://huangjian.info/oauth2/'
    client = APIClient(app_key = APP_KEY, app_secret = APP_SECRET, redirect_uri = CALLBACK_URL)
    url = client.get_authorize_url()
    print url
    #print mechanize.urlopen(url).read()
    #code = '1d0e436da1b12e548a15aff3febe16fc'
    #r = client.request_access_token(code)
    #OAUTH_token
    #access_token = r.access_token
    #expires_in = r.expires_in
    #access_token = "2.00Dg1_yCq5_EgE2725e3e3a2cAH4lC"
    #expires_in = "1336291837"
    #client.set_access_token(access_token, expires_in)
    #print client.get.statuses__user_timeline()
    #print client.post.statuses__update(status=u'test for OAuth2.0')

if __name__ == "__main__":
    #login_weibo()
    if len(sys.argv) < 2:
        print "Error argc!"
        pass
    get_latlng(sys.argv[1])

