#coding=utf-8
import os
import sys
import json
import jieba
import pandas as pd
import preprocess as prep
import jieba.posseg as pseg
import netease_4_10 as crawl
from datetime import datetime
from pymongo import MongoClient

if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')
cwd = os.getcwd()

def judge_art_cnt(date_start, date_end):
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease

		a = db.war.find({'$and':[{'date':{'$gt':date_start}}, {'date':{'$lt':date_end}}]})
		cnt = a.count()
		conn.close()
		print "%s, %s, %d --from mongodb_io"%(date_start, date_end, cnt)
		return cnt
	except Exception as e:
		print "From:judge_date\n\tUnexpect Error: {}".format(e)

def judge_art_cnt_1(days):
	try:
		tag_time = crawl.get_point_time(days)
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		cnt = db.token_war.find({'date':{'$gt': tag_time}}).count()
		conn.close()
		return cnt
	except Exception as e:
		print "From:judge_art_cnt_1:\n\tUnexpect Error: {}".format(e)



def sync():
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		point = datetime(2018, 1, 1)
		cnt1 = db.war.find({'date':{'$gt':point}}).count()
		cnt2 = db.token_war.find({'date':{'$gt':point}}).count()
		conn.close()
		# print cnt1, cnt2
		if cnt1 == cnt2:
			return 1
		elif cnt1 > cnt2:
			return 0
		else:
			raise Exception("token_war table is bigger than war!")
	except Exception as e:
		print "From:sync:\n\tUnexpect Error: {}".format(e)


def get_target(tag_time):
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		target = db.token_war.find({'date':{'$gt': tag_time}})
		conn.close()
		return target
	except Exception as e:
		print "From:get_target:\n\tUnexpect Error: {}".format(e)

def get_target_1(date_start, date_end):
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		target = db.token_war.find({'$and':[{'date':{'$gt':date_start}}, {'date':{'$lt':date_end}}]})
		conn.close()
		return target
	except Exception as e:
		print "From:get_target_1:\n\tUnexpect Error: {}".format(e)


def id_get_cmts(art_id_list):
	cmt_cnt = 0
	cmt_list = []
	cmt_vote = []
	cmt_against = []
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		for art_id in art_id_list:
			ele = db.war.find_one({'number':art_id})	# Using find_one
			cmt_cnt += len(ele['comments'])
			for cmt in ele['comments']:
				cmt_list.append(cmt['content'])
				cmt_vote.append(cmt['vote'])
				cmt_against.append(cmt['against'])
		cmt_detail = {'vote': cmt_vote, 'against': cmt_against, 'content': cmt_list} 
		return pd.DataFrame(cmt_detail, columns = ['against', 'vote', 'content'])
		conn.close()
	except Exception as e:
		print "From:id_get_cmts:\t\nUnexpect Error: {}".format(e)


def art_tokenize():
	cnt = 0		
	new = []
	point = datetime(2018, 1, 1)
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		target = db.war.find({'date':{'$gt':point}})
		for i in target:
			if db.token_war.find({'number':i['number']}).count() < 1:
				tokens_list = prep.tokenize(i['content'], sw_list = [], language = 'CN')
				del i['content'], i['comments'], i['commenturl'], i['tie_count']
				i['tokens'] = ' '.join(tokens_list)
				new.append(i)
				cnt += 1
		if new:
			# insert bulk
			db.token_war.insert_many(new)						
			print "%d article tokenized completed!"%cnt
			return "%d article tokenized completed!"%cnt
		else:
			print "No new article requires tokenize!"
			return "No new article requires tokenize!"
		conn.close()
	except Exception as e:
		print "From:art_tokenize:\t\nUnexpect Error: {}".format(e)


# add the article tokens that remove stopwords
def rm_sp_tokens(sw_list, update_all = 0):
	cnt = 0
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		target = db.token_war.find()
		if update_all == 1:
			print "Updating rs_tokens of all article again!"
		for i in target:
			# if rs_tokens key is not exist or rs_tokens value is null
			if "rs_tokens" not in i.keys() or not i['rs_tokens'] or update_all == 1:		
				rsTokens = prep.rm_sw(i['tokens'], sw_list)
				db.token_war.update_one({'number': i['number']}, {'$set':{'rs_tokens': rsTokens}})
				cnt += 1
		if cnt == 0:
			print "There are no article that need to be removed stop words!"
			return "There are no article that need to be removed stop words!"
		else:
			if update_all == 0:
				print "%d article have removed stop words!"%cnt
				return "%d article have removed stop words!"%cnt
			else:
				print "%d article have update the rs_tokens!"%cnt
				return "%d article have update the rs_tokens!"%cnt
		conn.close()
	except Exception as e:
		print "From:rm_sp_tokens:\n\tUnexpect Error: {}".format(e)


# add the article tokens that pos clean
def pos_clean_tokens(update_all = 0):
	cnt = 0
	tag_list = ['t', 's', 'f', 'm', 'q', 'p', 'u', 'w', 'e', 'y', 'o', 'h', 'k', 'a', 'd', 'eng', 'x', 'b', 'i']
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		target = db.token_war.find()
		if update_all == 1:
			print "Updating pos remove of all article again!"
		for i in target:
			if "im_tokens" not in i.keys() or not i['im_tokens'] or update_all == 1:
				t = []
				content = ''.join(i['rs_tokens'].split())
				pos_words = pseg.cut(content)
				pos_words = dict(pos_words)
				for word, pos in pos_words.items():
					if len(word) == 1 and pos[0] == 'j':
						t.append(word)
						# print word,
					elif len(word) > 1 and pos[0] not in tag_list:
						# print word, pos,	
						t.append(word)
				string = ' '.join(t)		
				db.token_war.update_one({'number': i['number']}, {'$set':{'im_tokens': string}})
				cnt += 1
		if cnt == 0:
			print "There are no article that need to pos clean!"
			return "There are no article that need to pos clean!"
		else:
			if(update_all == 0):
				print "%d article have pos clean!"%cnt
				return "%d article have pos clean!"%cnt
			else:
				print "%d article have update pos clean!"%cnt
				return "%d article have update pos clean!"%cnt
		conn.close()
	except Exception as e:
		print "From:pos_clean_tokens:\n\tUnexpect Error: {}".format(e)


def tokens_to_file(key, path):
	conn = MongoClient('127.0.0.1', 27017)
	db = conn.netease
	point = datetime(2018,1,1)
	data = db.token_war.find({'date': {'$gt':point}})
	with open(path, "w") as fpout:
		for i in data:
			fpout.write(i[key]+'\n')


def titile_tokens():
	cnt = 0		
	try:
		sw_path = os.path.join(cwd, "text/news_stopwords.txt")
		sw_list = prep.get_stopwords(sw_path)
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		target = db.token_war.find({})

		for i in target:
			if "title_keywords" not in i.keys() or not i['title_keywords']:
				cnt += 1
				title_keywords = []
				if len(i['keywords']) > 1:	# article have keywords
					title_keywords = i['title'] + '\t\t'+' '.join(i['keywords'])
				else:
					title_keywords = i['title']
				tokens_string = ' '.join(prep.tokenize(title_keywords, sw_list = sw_list, language = 'CN'))
				db.token_war.update_one({'number': i['number']}, {'$set':{'title_keywords': tokens_string}})
		print "%d title tokenize completed!"%cnt
	
		conn.close()
	except Exception as e:
		print "From:art_tokenize:\t\nUnexpect Error: {}".format(e)


def title_clean_tokens():
	cnt = 0
	tag_list = ['t', 's', 'f', 'm', 'q', 'p', 'u', 'w', 'e', 'y', 'o', 'h', 'k', 'a', 'd', 'eng', 'x', 'b', 'i']
	try:
		conn = MongoClient("127.0.0.1", 27017)
		db = conn.netease
		target = db.token_war.find()
		for i in target:
			if "im_title" not in i.keys() or not i['im_title']:
				t = []
				content = ''.join(i['title_keywords'].split())
				pos_words = pseg.cut(content)
				pos_words = dict(pos_words)
				for word, pos in pos_words.items():
					if len(word) == 1 and pos[0] == 'j':
						t.append(word)
						# print word,
					elif len(word) > 1 and pos[0] not in tag_list:
						# print word, pos,	
						t.append(word)
				string = ' '.join(t)		
				db.token_war.update_one({'number': i['number']}, {'$set':{'im_title': string}})
				cnt += 1
		print "%d title tokens clean completed!"%cnt
	
		conn.close()
	except Exception as e:
		print "From:pos_clean_tokens:\n\tUnexpect Error: {}".format(e)


def main():
	crawl_state = crawl.main()
	sp = os.path.join(cwd, "text/news_stopwords.txt")
	sw_list = prep.get_stopwords(sp)
	a = art_tokenize()
	b = rm_sp_tokens(sw_list)
	c = pos_clean_tokens()
	titile_tokens()
	title_clean_tokens()
	crawl_state = crawl_state +'\n'+a+'\n'+b+'\n'+c
	print "From the mongodb_io.py:"
	print crawl_state
	return crawl_state


if __name__ == '__main__':
	# titile_tokens()
	# title_clean_tokens()
	main()
	pass