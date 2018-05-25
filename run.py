import sys,time
from bs4 import BeautifulSoup
import requests
from json import *

cookie = 'your_cookie'

#使用PythonProxy获取代理，并使用
#本程序未使用
def get_proxy():
	url = 'http://127.0.0.1:5050/get_one/'
	resp = requests.get(url, timeout=5).content.decode('utf-8')
	item = resp.split(' ')
	return item

def tryOnce(actid, cur_page): 
	global total_num
	url	 = 'http://try.jd.com/migrate/apply?activityId='+actid+'&source=0'
	header = {
		'cookie'     : cookie,
		'referer'    : 'http://try.jd.com/migrate/apply?activityId='+actid+'&source=0',
		'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko)'
	}
	#response = requests.get(url, headers=header, proxies=proxies)
	response = requests.get(url, headers=header)
	g = response.content.decode('utf-8')
	print('{}/{} : {}'.format(cur_page, total_num, g))
	return 0

def getNotTried(actList): 
	url	 = 'http://try.jd.com/user/getApplyStateByActivityIds?activityIds=' + ','.join(actList)
	header = {
		'cookie'  : cookie,
		'referer' : 'http://try.jd.com/activity/getActivityList?page=1&activityState=0'
	}
	response = requests.get(url, headers=header)
	g = response.content.decode('utf-8')
	d=JSONDecoder().decode(g)
	actlist2 = []
	for i in d:
		actlist2.append(str(i['activityId']))
	return set(actList) - set(actlist2)
	
def getAllGoodsFromOnePage(page): 
	url	 = 'http://try.jd.com/activity/getActivityList?page='+str(page)+'&activityState=0'
	response = requests.get(url)
	d = response.content.decode('utf-8')
	soup = BeautifulSoup(d, 'lxml')

	actList = []
	for lind in soup.find_all('li'):
		actid = lind.get('activity_id')
		if actid:
			actList.append(str(actid))

	return actList
	
def getPageNum(): 
	url	 = 'http://try.jd.com/activity/getActivityList?activityState=0'
	response = requests.get(url)
	d = response.content.decode('utf-8')
	soup = BeautifulSoup(d, 'lxml')

	count = 0
	start =  str(soup.head.script).find('{')
	end = str(soup.head.script).rfind('}') + 1
	jsonStr = str(soup.head.script)[start:end]
	jsonStr = jsonStr.replace('\'', "\"")

	d=JSONDecoder().decode(jsonStr)
	return d["pagination"]["pages"]

if __name__ == '__main__':
	global total_num
	print('[+]start!')
	total = getPageNum()
	total_num = total*20
	
	for i in range(1, total+1):
		num = 0
		print('Page:'+str(i))
		actList = getAllGoodsFromOnePage(i)
		actList = getNotTried(actList)
		for actid in actList:
			tryOnce(actid, i*20+num)
			num += 1
			time.sleep(5)
	print('[+]end!')
	
	exit()