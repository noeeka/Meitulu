# -*- coding: utf-8 -*-
import gzip
import httplib
import os
import requests
import sys
import threading
import time
import urllib2
import uuid
import zlib
from StringIO import StringIO
from bs4 import BeautifulSoup
from functools import wraps
from httplib import HTTPConnection, HTTPS_PORT
import httplib,ssl,socket
import urllib3


def sslwrap(func):
	@wraps(func)
	def bar(*args, **kw):
		kw['ssl_version'] = ssl.PROTOCOL_TLSv1
		return func(*args, **kw)
	
	return bar


reload(sys)
sys.setdefaultencoding('utf-8')


def deflate(data):  # zlib only provides the zlib compress format, not the deflate format;
	try:  # so on top of all there's this workaround:
		return zlib.decompress(data, -zlib.MAX_WBITS)
	except zlib.error:
		return zlib.decompress(data)


hdr = {
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Referer': 'https://www.meitulu.com',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	'Accept-Encoding': 'none',
	'Accept-Language': 'en-US,en;q=0.8',
	'Connection': 'keep-alive',
	'cookie': 'UM_distinctid=1609d58bf868-08db4c409f5a5f-3c60460e-130980-1609d58bf8734b; CNZZDATA1255487232=1295110815-1514464165-%7C1514464165; Hm_lvt_e1c5237d553df792018cceb5834a3bdf=1514937759,1515134859,1515245964,1515390323; CNZZDATA1255357127=1984249438-1514466194-https%253A%252F%252Fwww.baidu.com%252F%7C1515389408; Hm_lvt_1e2b00875d672f10b4eee3965366013f=1514937747,1515126142,1515245964,1515390323; Hm_lpvt_e1c5237d553df792018cceb5834a3bdf=1515390518; Hm_lpvt_1e2b00875d672f10b4eee3965366013f=1515390518'
}

http = urllib3.PoolManager()

url = 'https://www.meitulu.com/t/taboo-love/'
class MyThread(threading.Thread):
	def __init__(self, func, args):
		threading.Thread.__init__(self)
		self.args = args
		self.func = func
	
	def run(self):
		apply(self.func, self.args)


# 通用抓站方法
def getWebContents(url, hdr):
	r=http.request('GET', url, headers=hdr)
	return r.data


# 下载图片服务
def downloadImg(refer, url, cate):
	ssl.wrap_socket = sslwrap(ssl.wrap_socket)
	getHeaders = {
		'Host': 'mtl.ttsqgs.com',
		'Connection': 'Keep-Alive',
		'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
		'Upgrade-Insecure-Requests': '1',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
		'Referer': refer,
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'lt,en-us;q=0.8,en;q=0.6,ru;q=0.4,pl;q=0.2'
	}
	response = requests.get(url, headers=getHeaders)
	mkdir(cate)
	
	with open(cate + "/" + os.path.basename(url), 'wb') as f:
		f.write(response.content)


# 生成文件目录
def mkdir(path):
	path = path.strip()
	path = path.rstrip("\\")
	isExists = os.path.exists(path)
	if not isExists:
		os.makedirs(path)
		return True
	else:
		return False


def ceawlWeb(page_url, cate, hdr):
	soup_pages = BeautifulSoup(getWebContents(page_url, hdr), "lxml")
	images_pages = soup_pages.find_all('img', class_="content_img")
	images_pages = list(images_pages)
	for src in images_pages:
		print src.attrs['src']
		downloadImg(page_url, src.attrs['src'], cate)


# 具体的处理函数，负责处理单个任务
dictionary = {}
raw = getWebContents("https://www.meitulu.com/t/taboo-love/", hdr)
soup = BeautifulSoup(raw, "lxml")
for slice in list(soup.find('ul', {'class': "img"}).children):
	if (type(slice.find("a")) != type(1)):
		res = []
		url = str(slice.find("a").attrs['href'])
		res.append(url)
		data = getWebContents(url, hdr)
		soup = BeautifulSoup(data, "lxml")
		pages_temp = list(soup.find('div', {'id': "pages"}).children)
		cate = (soup.title.string).split("_")[0]
		for page in range(2, int(pages_temp[-3].get_text().encode("utf-8")) + 1):
			page_url = url[:-5] + "_" + str(page) + ".html"
			res.append(page_url)
		dictionary[cate] = res

for key, item in dictionary.items():
	threadList = [MyThread(ceawlWeb, (url, key, hdr)) for url in item]
	for t in threadList:
		t.setDaemon(True)
		t.start()
	for i in threadList:
		i.join()
del data
del threadList