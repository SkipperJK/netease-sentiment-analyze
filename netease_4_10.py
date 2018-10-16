import re
import sys
import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')

headers = {
	"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36" 
}


class News_basic():
	def __init__(self, title, docurl, commenturl, n_id, n_time):
		self.title = title
		self.docurl = docurl
		self.commenturl = commenturl
		self.n_id = n_id
		self.n_time = n_time


def crawl_page_url(url):
	try:
		page_urls = []
		for i in range(0, 10):
			if i == 0:
				page_urls.append(url+"cm_war.js")
			elif i > 1 and i < 4:
				page_urls.append(url+"cm_war_"+str("%02d"%i)+".js")
		return page_urls
	except Exception as e:
		print "From:crawl_page_url\n\tUnexpect Error: {}".format(e)
	

def crawl_news_class(page_urls):
	try:
		news_class_list = []

		for url in page_urls:
			r = requests.get(url, headers = headers)
			if r.status_code == 200:
				t1 = r.text 
				raw_json = t1.strip("data_callback(").rstrip(')')
				j = json.loads(raw_json)

				for sub_url in j:
					time_state = 1
					n_id = sub_url['commenturl'].split('/')[-1].split('.')[0]
					# "time":"03/31/2018 15:14:01"
					# convert it to datatime format
					if sub_url['time'] != "":
						raw_time = sub_url['time'].split()
						raw_time1 = raw_time[0].split('/')
						raw_time2 = raw_time[1].split(':')
						n_time = datetime(int(raw_time1[2]), int(raw_time1[0]), int(raw_time1[1]), \
											int(raw_time2[0]), int(raw_time2[1]), int(raw_time2[2]))
					else:
						time_state = 0
						print sub_url['docurl']
						print "Note --- No time value!--- Drop this news!"
						continue
					news = News_basic(sub_url['title'], sub_url['docurl'],\
										 sub_url['commenturl'], n_id, n_time)    
					pp = datetime(2018,1,1) 
					if n_time < pp:
						continue
					if sub_url['docurl'].split('/')[2] == "war.163.com" or \
							sub_url['docurl'].split('/')[2] == "dy.163.com":
						if news not in news_class_list and time_state == 1:    
							news_class_list.append(news)
			else:
				raise Exception("The return code is %d"%r.status_code)
		return news_class_list
	except Exception as e:
		print "From:crawl_news_class:\n\tUnexpect Error: {}".format(e)


def get_point_time(days):
	try:
		c_t = time.localtime(time.time())
		#process the date, only crawl the five days ago news
		c_y = c_t[0]
		c_m = c_t[1]
		c_d = c_t[2]

		ms = days/30
		ys = ms/12
		days = days-ms*30
		ms = ms-ys*12

		if c_d - days > 0:
			c_d -= days
		else:
			ms += 1
			c_d = 30-days+c_d

		if c_m - ms > 0:
			c_m -= ms
		else:
			ys += 1
			c_m = 12-ms+c_m
		c_y -= ys
		return datetime(c_y, c_m, c_d)
# Version2: get current time
	# datetime.utcnow()
	except Exception as e:
		print "From:get_point_time\n\tUnexpect Error: {}".format(e)


def crawl_news_content(docurl, n_id):
	
	keywords =''
	content = ''
	try:
		r = requests.get(docurl, headers = headers)
		t = r.text
		if r.status_code == 200:
			soup = BeautifulSoup(t, 'html.parser')
			
			for i in soup.find_all('meta'):
				if i.get('name') == 'keywords':
					keywords = [word for word in i['content'].split(',')]

			#There have three types file, 
			#1, war.163   2. photoview  3. article
			try:
				if docurl.split('/')[3] == 'photoview':
					text = json.loads(soup.textarea.get_text())
					content = text['info']['prevue']
					for t in text['list']:
						content = content + t['note']
				elif docurl.split('/')[4] == 'article':
					content = soup.find('div', class_ = 'content').get_text()
				else:
					content = soup.find('div', class_ = 'post_text').get_text()
				content = content.strip()				# clean the date
				content = content.replace('\n', '')
				content = content.replace('<br>', '')

				# return 1, content, keywords
				return content, keywords
			except Exception as e:
				print "Unexpect Error: {}".format(e)
				content = -1
				keywords = -1
				return content, keywords
				# return -1, content, keywords  # draw the content failed!
		else:
			raise Exception("The return code is %d---crawl_news_content"%r.status_code)

	except Exception as e: 
		print "The %s article:"%n_id
		print "From:crawl_news_content:\n\tUnexpect Error: {}".format(e)
		return -2, content, keywords # request failed!


def crawl_news_cmtcount(commenturl, n_id):
 	cmt_url = commenturl
	base_url = "http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/"
	count_url = base_url + n_id
	try:
		r = requests.get(count_url, headers = headers)
		if r.status_code == 200:
			j = json.loads(r.text)
			tie_count = j['tcount']
			join_count = j['cmtVote'] + j['cmtAgainst'] + j['rcount']
			return tie_count
		else:
			raise Exception("The return code is %d---crawl_news_cmtcount"%r.status_code)
	except Exception as e:
		print "The %s article:"%n_id
		print "From:crawl_news_cmtcount:\n\tUnexpect Error: {}".format(e)
		return -1


# the cmt_list element is dict 
def crawl_news_comment(commenturl, tie_count, n_id):
	cmt_list = []
	cmt_id_list = []
	base_url = "http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/"
	try:
		cmt_url = commenturl
		c_url = base_url + n_id + "/comments/newList"
		payload = {'offset': 0, 'limit': 30}
		# state = 1  # represent the normal return value
		while(payload['offset'] < tie_count):
			r = requests.get(c_url, params = payload)
			if r.status_code == 200:
				j = json.loads(r.text)
				if(len(j['comments']) > 0):
					# if you wanna add more info, you can add info to the cmt_info
					for k,v in j['comments'].items():
						cmt_info = {}
						if j['comments'][k]['commentId'] not in cmt_id_list:
							cmt_id_list.append(j['comments'][k]['commentId'])
							cmt_info['commentId'] = j['comments'][k]['commentId']
							cmt_info['content'] = j['comments'][k]['content']
							cmt_info['vote'] = j['comments'][k]['vote']
							cmt_info['against'] = j['comments'][k]['against']
							c_t = j['comments'][k]['createTime'].split()		
							# time type 2018-04-08 07:28:00
							c_t_0 = c_t[0].split('-')
							c_t_1 = c_t[1].split(':')
							cmt_info['date'] = datetime(int(c_t_0[0]), int(c_t_0[1]), int(c_t_0[2]),\
														 int(c_t_1[0]), int(c_t_1[1]), int(c_t_1[2]))
							cmt_info['content'] = cmt_info['content'].replace('<br>', '')  
							cmt_list.append(cmt_info)    # the cmt_list include cmt_info dictory
				else:
					break  # Quit while
				payload['offset'] = payload['offset'] + 30
			else:
				raise Exception("The return code is %d---crawl_news_comment"%r.status_code)
		return cmt_list
	except Exception as e:
		print "The %s article:"%n_id
		print "From:crawl_news_comment:\n\tUnexpect Error: {}".format(e)
		return -1	#Error Return -1, occur the mongodb the comments value is -1 (Don't why(have continue))


def crawling(news_class_list, tag_time):
	try:
	
		conn = MongoClient('127.0.0.1', 27017)
		db = conn.netease
		war = db.war

		new_insert = 0
		new_update = 0

		if news_class_list and len(news_class_list) > 0:
			for news in news_class_list:
				exist = 0
				s_tie_count = 0
				if news.n_time > tag_time:
					if war.find({"number":news.n_id}).count() > 0 :		# the news have been stored!
						exist = 1
						s_tie_count = war.find_one({'number': news.n_id})['tie_count']
						# print "NNN --- The news have stored in mongodb!"
					else:
						content, keywords = crawl_news_content(news.docurl, news.n_id)
					tie_count = crawl_news_cmtcount(news.commenturl, news.n_id)
					if tie_count == -1:
						continue
					if exist != 1 and s_tie_count != tie_count or tie_count != 0:  # No the latest comments 
						cmt_list = crawl_news_comment(news.commenturl, tie_count, news.n_id)
						if cmt_list == -1:
							cmt_list = []
							continue
					if exist == 0:
						news_item = {}
						news_item['number'] = news.n_id
						news_item['title'] = news.title
						news_item['docurl'] = news.docurl
						news_item['commenturl'] = news.commenturl
						news_item['date'] = news.n_time
						news_item['keywords'] = keywords
						news_item['content'] = content
						news_item['tie_count'] = tie_count
						news_item['comments'] = cmt_list

						war.insert_one(news_item)
						new_insert += 1
						# print "The news insert successed !"
					elif exist == 1 and s_tie_count != tie_count:
						war.update_one({'number': news.n_id}, \
										{'$set':{'tie_count': tie_count, 'comments': cmt_list}})
						new_update += 1
		else:
			print "No the url to be crawl!"
		conn.close()
		return new_insert, new_update
	except Exception as e:
		print "From:crawling:\n\tUnexpect Error: {}".format(e)


def update_cmts(n):
	try:
		# print "Increase updating the comments for stored article......" # Can not recongnize the limit
		print "Updating the comments for stored article......"
		tag_time = get_point_time(n)
		conn = MongoClient('127.0.0.1', 27017)
		db = conn.netease
		war = db.war
		new_update = 0
		for i in war.find():
			if i['date'] > tag_time:
				s_tie_count = i['tie_count']
				tie_count = crawl_news_cmtcount(i['commenturl'], i['number'])
				cmt_list = crawl_news_comment(i['commenturl'], tie_count, i['number'])
				if tie_count != s_tie_count and tie_count != -1 and cmt_list != -1:
					war.update_one({'number': i['number']},\
								   {'$set':{'tie_count': tie_count, 'comments': cmt_list}})
					new_update += 1
		conn.close()
		# return new_update
		print "Update %d article comments."%new_update
	except Exception as e:
		print "From:update_cmts:\n\tUnexpect Error: {}".format(e)


def crawl_new(n):
	url = "http://temp.163.com/special/00804KVA/"
	print "Crawling page url......"
	page_urls = crawl_page_url(url)
	print "Crawling news url......"
	news_class_list = crawl_news_class(page_urls)
	tag_time = get_point_time(n)		# get five days ago time	
	print "Crawling news......"
	new_insert, new_update = crawling(news_class_list, tag_time)
	print "Insert %d article\nUpdate %d article comments"%(new_insert, new_update)
	return new_insert


def main():
	url = "http://temp.163.com/special/00804KVA/"	# dynamic loading josn data of all news web invalid
	print "From netease_4_10.py:"
	print "Crawling page url......"
	page_urls = crawl_page_url(url)
	print "Crawling news url......"
	news_class_list = crawl_news_class(page_urls)
	tag_time = get_point_time(5)		# get five days ago time
	print "Crwaling news......"
	new_insert, new_update = crawling(news_class_list, tag_time)
	print "Insert %d article\nUpdate %d article comments"%(new_insert, new_update)
	return "Insert %d article\nUpdate %d article comments"%(new_insert, new_update)

if __name__ == '__main__':
	main()
	# update_cmts(300)
	# print "Update %d article"%n
	# crawl_page_url('http://temp.163.com/special/00804KVA/')
	pass


	