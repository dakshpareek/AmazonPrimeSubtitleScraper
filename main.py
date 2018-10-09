import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import json,time
from selenium import webdriver
from pathlib import Path

def login():
	link="https://www.amazon.com/ap/signin?accountStatusPolicy=P1&clientContext=262-8850897-1873444&language=en_US&openid.assoc_handle=amzn_prime_video_desktop_us&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.primevideo.com%2Fauth%2Freturn%2Fref%3Dav_auth_ap%3F_encoding%3DUTF8%26location%3D%252Fref%253Ddv_auth_ret"
	amazonDriver.get(link)
	time.sleep(2)
	amazonDriver.find_element_by_name('email').send_keys("+917597186191")
	amazonDriver.find_element_by_name('password').send_keys("cockroach")
	time.sleep(1)
	amazonDriver.find_element_by_xpath('//*[@id="signInSubmit"]').click()
	time.sleep(1)

def getsub(link,idd):
	subRequestObject = requests.get(link)
	subsFileHandler = open(str(idd) + ".ttml2","w",encoding='utf-8')
	subsFileHandler.write(subRequestObject.text)
	subsFileHandler.close()
	fin='py ttml2srt.py '+str(idd)+'.ttml2 > '+str(idd)+'.srt'
	os.system(fin)
	os.remove(str(idd) + ".ttml2")
	os.rename(str(idd) + ".srt","prime-data/"+str(idd) + ".srt")
	print("Subtitle Downloaded")

def getjson(link,idd):
	amazonDriver.get(link)
	soup = BeautifulSoup(amazonDriver.page_source,"lxml")
	dict_from_json = json.loads(soup.find("body").text)
	for k in dict_from_json['subtitleUrls']:
		if k['languageCode']=="en-gb":
			sublink=k['url']
			break
	try:
		getsub(sublink,idd)
		title=dict_from_json['catalogMetadata']['catalog']['title']
		runtime=dict_from_json['catalogMetadata']['catalog']['runtimeSeconds']
		image=dict_from_json['catalogMetadata']['images']['imageUrls']['title']
		return title,runtime,image
	except:
		print("Exception While Getting SRT JSON")
		return None,None,None

def save(title,runtime,image,release,genres,idd):
	j={'data':[]}
	j['data'].append({'vid':idd})
	j['data'].append({'title':title})
	j['data'].append({'duration':runtime/60})
	j['data'].append({'release':release})
	j['data'].append({'genres':genres})
	with open(str(idd)+'.json', 'w') as outfile:
		json.dump(j, outfile)
	urllib.request.urlretrieve(image,str(idd)+".jpg")
	os.rename(str(idd)+'.json', "prime-data/"+str(idd)+'.json')
	os.rename(str(idd)+'.jpg', "prime-data/"+str(idd)+'.jpg')
	print("Done")

def scrape1(link):
	dt=link.split('/')
	idd=dt
	if Path("prime-data/"+str(idd[4]) + ".srt").is_file() or Path("prime-data/"+str(idd[4]) + ".nosub").is_file() :
		print("Skipping --")
	else:
		amazonDriver.get(link)
		page_src=amazonDriver.page_source
		time.sleep(5)
		resourceList = []
		sub_url=""
		resourceList = amazonDriver.execute_script("return window.performance.getEntries();")
		for i in resourceList:
			if 'name' in i.keys():
				if "GetPlaybackResources?" in i['name']:
					sub_url=i['name']
					break
		#print(sub_url)
		try:
			title,runtime,image=getjson(sub_url,dt[4])
			if title!=None:
				soup = BeautifulSoup(page_src,"lxml")
				try:
					release=soup.find('span',{'data-automation-id':'release-year-badge'}).text
				except:
					release=None
				try:
					gen=soup.find('div',{'data-automation-id':'meta-info'})
					dl=gen.findAll('dl')
					gens=dl[2].findAll('a')
					genres=[i.text for i in gens]
				except:
					genres=[]
				#extracting more data
				save(title,runtime,image,release,genres,dt[4])
			else:
				print("No Subtitle Found")
				fh = open(str(dt[4])+".nosub","w")
				fh.close()
				os.rename(str(dt[4]) + ".nosub", "prime-data/"+str(dt[4]) + ".nosub")
		except:
			print("Exception While Getting JSON API")

path="c:\chromedriver.exe"
amazonDriver = webdriver.Chrome(path)
#amazonDriver.set_page_load_timeout(30)
login()
if not os.path.exists("prime-data"):
	os.makedirs("prime-data")
time.sleep(4)
link="https://www.primevideo.com/detail/0PHXMBR0NM48WQBNOQPF9T500H/ref=atv_hm_hom_c_Lel2oV_brws_3_2"
scrape1(link)