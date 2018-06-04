#coding=utf-8
import os
import sys
import json
import jieba
import pandas as pd
import jieba.posseg as pseg
from datetime import datetime

if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')

# Loading the default stopwords
cwd = os.getcwd()
filename = os.path.join(cwd, "text/stopsign.txt")
try:
	with open(filename) as fp:
		stopwords = fp.read().splitlines()
	stopwords = list(set(stopwords))
except Exception as e:
	print "Get default stopwords:\n\tUnexpected Error: {}".format(e)
# sw_path = "/home/skipper/nltk_data/Other_data/stopwords/CNstopwords.txt"


def get_stopwords(filename):
	try:
		with open(filename) as fp:
			stopwords = fp.read().splitlines()
		stopwords = list(set(stopwords))
		return stopwords
	except Exception as e:
		print "From:get_stopwrods:\n\tUnexpected Error: {}".format(e)


def is_alpha(word):
	try:
		return word.encode('ascii').isalnum()
	# except UnicodeEncodeError:
	except:
		return False

		
# Return a list of tokens
def tokenize(st, sw_list = stopwords, language = 'CN'): 
	tokens = []
	if language == 'CN':
		st = st.replace(' ', '')
		st = st.replace('\n', '')
		st = st.replace('\t', '')
		st = st.replace('\r', '')
		st = st.replace('\r\n', '')
		st = st.replace('\xe3\x80\x80', '')
		tokens = jieba.cut(st)
		tokens = [token for token in tokens if token not in sw_list \
					and not token.isdigit() and not is_alpha(token)] # remove digit
		# tokens = [token for token in tokens if token not in sw_list and not token.isalnum()] # remove digit
	elif language == 'EN':
		tokens = [token for token in st.split() if token not in sw_list and not token.isdigit()]
	return tokens


def rm_sw(content, stop_list):
	try:
		tokens = content.split()
		words = [word for word in tokens if word not in stop_list and not word.isdigit()]

		return ' '.join(words)
	except Exception as e:
		print "From:rm_sw:\n\tUnexpect Error: {}".format(e)


# convert data from the mongodb to DataFrame format
def convert_to_dataframe(mg_cursor):
	art_id = []
	art_url = []
	art_date = []
	art_title = []
	art_keywords = []
	art_im_tokens = []
	art_title_keywords = []
	art_im_title = []
	art_rs_tokens = []
	for ele in mg_cursor:
		art_id.append(ele['number'])
		art_url.append(ele['docurl'])
		art_date.append(ele['date'])
		art_title.append(ele['title'])
		art_keywords.append(ele['keywords'])
		art_im_tokens.append(ele['im_tokens'])
		art_title_keywords.append(ele['title_keywords'])
		art_im_title.append(ele['im_title'])
		art_rs_tokens.append(ele['rs_tokens'])
	data = {'id':art_id, 'url':art_url, 'date':art_date, \
			'title':art_title, 'keywords':art_keywords, \
			'im_tokens': art_im_tokens, 'title_keywords': art_title_keywords,\
			'im_title': art_im_title, 'rs_tokens': art_rs_tokens}
	# print pd.DataFrame(data)
	return pd.DataFrame(data)


def pos_test(tokens):
	tag_list = ['t', 's', 'f', 'm', 'q', 'p', 'u', 'w', 'e', 'y', 'o', 'h', 'k', 'a', 'd', 'eng', 'x', 'b', 'i']
	try:
		t = []
		content = ''.join(tokens)
		print content
		pos_words = pseg.cut(content)
		pos_words = dict(pos_words)
		pos_list = []
		for word, pos in pos_words.items():
			pos_list.append(word+'-'+pos)
			if len(word) == 1 and pos[0] == 'j':
				t.append(word)
			elif len(word) > 1 and pos[0] not in tag_list:	
				t.append(word)
		string = ' '.join(t)
		# print '/'.join(pos_list)
		pos_tag = '/'.join(pos_list)
		return pos_tag, string
	except Exception as e:
		print "From:pos_test:\n\tUnexpect Error: {}".format(e)



if __name__ == '__main__':
	sentence = "MDS是一个统计技术集合,用于可视化地描述距离集合中的相似性和差异性.对于经典的MDS的处理过程包括:输入一个包含数据集中任意两个数据点之间距离的距离矩阵"
	sw_list = get_stopwords(os.path.join(cwd, "text/news_stopwords.txt"))
	tokens = tokenize(sentence, sw_list, language = "CN")
	for i in tokens:
		print i
	a, b = pos_test(tokens)
	print a
	print b
	pass

