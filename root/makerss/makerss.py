#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys, os, time
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib, re, yaml
import json
import base64
import traceback
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait

def GetList(driver, site, cate):
	# 리스트 생성
	indexList = []
	for page in range(1, site['MAX_PAGE']+1):
		print('PAGE : %s' % page)
		u = '%s/bbs/board.php?bo_table=%s&page=%s' % (site['TORRENT_SITE_URL'], cate, page)
		print('URL : %s' % u)
		driver.get(u)

		list_tag = site['XPATH_LIST_TAG'][:site['XPATH_LIST_TAG'].find('[%s]')]
		list = WebDriverWait(driver, 3).until(lambda driver: driver.find_elements_by_xpath(list_tag))
		step = 1 if 'STEP' not in site else site['STEP']
		for i in range(1, len(list)+1, step):
		#for i in range(1, 6):
			try:
				a = WebDriverWait(driver, 3).until(lambda driver: driver.find_element_by_xpath(site['XPATH_LIST_TAG'] % i))
				if a.get_attribute('href').find(cate) == -1: continue
				#a = WebDriverWait(driver, 3).until(lambda driver: driver.find_element_by_xpath(''))

				item = {}
				item['title'] = a.text
				item['detail_url'] = a.get_attribute('href')
				indexList.append(item)
			except:
				print('NOT BBS : %s' % i)
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)


	# 세부 페이지에서 링크 추출
	list = []
	for item in indexList:
		print ('URL : %s' % item['detail_url'])
		driver.get(item['detail_url'])

		if 'HOW' not in site:
			try:
				link_element = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath("//a[starts-with(@href,'magnet')]"))

				for magnet in link_element:
					print('HREF : %s' % magnet.get_attribute('href'))
					idx2 = 0
					# torrentao 에서 magnet이 붙어있다
					while True:
						idx1 = magnet.get_attribute('href').find('magnet:?xt=urn', idx2)
						idx2 = magnet.get_attribute('href').find('magnet:?xt=urn', idx1+1)
						if idx2 == -1: idx2 = len(magnet.get_attribute('href'))
						# 중복검사
						entity = {}
						entity['title'] = item['title']
						entity['link'] = magnet.get_attribute('href')[idx1:idx2]
						flag = False
						for tmp in list:
							if tmp['link'] == entity['link']:
								flag = True
								break
						if flag == False:
							list.append(entity)
							print('TITLE : %s\nLINK : %s' % (entity['title'], entity['link']))
						if idx2 == len(magnet.get_attribute('href')): break
			except:
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)

		elif site['HOW'] == 'USING_MAGNET_REGAX':
			try:
				regax = re.compile(site['MAGNET_REGAX'], re.IGNORECASE)
				#match = regax.search(driver.page_source)
				match = regax.findall(driver.page_source)
				for m in match:
					entity = {}
					entity['title'] = item['title']
					entity['link'] = site['MAGNET_MAKE_URL'] % m
					list.append(entity)
					print('TITLE : %s\nLINK : %s' % (entity['title'], entity['link']))
			except:
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)

		# 첨부파일 다운로드
		if 'DOWNLOAD_FILE' in site and site['DOWNLOAD_FILE'] == 'ON':
			try:
				tmp = '%s/bbs/download.php' % site['TORRENT_SITE_URL']
				link_element = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements_by_xpath("//a[starts-with(@href,'%s')]" % tmp))
				for a_tag in link_element:
					tmp = a_tag.text.replace('\n', ' ').replace('\r', '')
					flag = False
					filename = ''
					for ext in ['.torrent', '.smi', '.srt', '.ass']:
						idx = tmp.find(ext)
						if idx != -1:
							flag = True
							if ext != '.torrent':
								filename = tmp[:idx + len(ext)]
							break
					if flag and filename is not '':
						print('DOWNLOAD : %s' % filename)
						download(driver, a_tag.get_attribute('href'), filename)
			except:
				exc_info = sys.exc_info()
				traceback.print_exception(*exc_info)
				print("")
				pass
	return list

def MakeRssFeed(where, cate, list):
	str =  '<rss xmlns:showrss=\"http://showrss.info/\" version=\"2.0\">\n'
	str += '\t<channel>\n'
	str += '\t\t<title>' + '%s - %s</title>\n' % (where, cate)
	str += '\t\t<link></link>\n'
	str += '\t\t<description></description>\n'
	for item in list:
		str += '\t\t<item>\n'
		str += '\t\t\t<title>%s</title>\n' % item['title']
		str += '\t\t\t<link>%s</link>\n' % item['link']
		#str += '\t\t\t<description>%s</description>\n' % item['title']
		str += '\t\t\t<showrss:showid></showrss:showid>\n'
		str += '\t\t\t<showrss:showname>%s</showrss:showname>\n' % item['title']
		str += '\t\t</item>\n'
	str += '\t</channel>\n'
	str += '</rss>'
	return str.replace('&', '&amp;')

def WriteFile(filename, data ):
	try:
		#with open(filename, "w", encoding='utf8') as f:
		with open(filename, "w") as f:
			f.write( unicode(data) )
		f.close()
		return
	except Exception as e:
		print('W11:%s' % e)
		pass
	try:
		with open(filename, "w", encoding='utf8') as f:
		#with open(filename, "w") as f:
			f.write( data )
		f.close()
		return
	except Exception as e:
		print('W22:%s' % e)
		pass

def download(driver, download_url, filename):
	print('Injecting retrieval code into web page')
	driver.execute_script("""
	    window.file_contents = null;
	    var xhr = new XMLHttpRequest();
	    xhr.responseType = 'blob';
	    xhr.onload = function() {
	        var reader  = new FileReader();
	        reader.onloadend = function() {
	            window.file_contents = reader.result;
	        };
	        reader.readAsDataURL(xhr.response);
	    };
	    xhr.open('GET', %(download_url)s);
	    xhr.send();
	""".replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ') % {
	    'download_url': json.dumps(download_url),
	})

	print('Looping until file is retrieved')
	downloaded_file = None
	while downloaded_file is None:
	    # Returns the file retrieved base64 encoded (perfect for downloading binary)
	    downloaded_file = driver.execute_script('return (window.file_contents !== null ? window.file_contents.split(\',\')[1] : null);')
	    #print(downloaded_file)
	    if not downloaded_file:
	        print('\tNot downloaded, waiting...')
	        time.sleep(0.5)
	print('\tDone')

	print('Writing file to disk')
	fp = open('/rssxml/' + filename, 'wb')
	fp.write(base64.b64decode(downloaded_file))
	fp.close()
	print('\tDone')


def GetDriver():
	driver = webdriver.Remote(command_executor='http://127.0.0.1:8910', desired_capabilities=DesiredCapabilities.PHANTOMJS)
	driver.implicitly_wait(10)
	return driver

def Start(title, site):
	print('MAKERSS START : %s' % title)
	for cate in site['BO_TABLE_LIST']:
		print('CATE : %s' % cate)
		list = GetList(driver, site, cate)
		if len(list) == 0: return -1
		str = MakeRssFeed(title, cate, list)
		#print('RSS : %s' % str)
		WriteFile('/rssxml/%s_%s.xml' % (title, cate), str)
		time.sleep(10)


if __name__ == "__main__":
	with open('/config/config.yml', 'r') as stream:
		config = yaml.load(stream)

	global driver
	driver = GetDriver()
	for site in config['SITE_LIST']:
		Start(site, config['templates'][site])
	driver.quit()
