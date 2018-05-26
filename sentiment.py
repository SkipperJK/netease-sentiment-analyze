#coding=utf-8
import os
import sys
import myclassifier as mclf
import train_doc_vector as dv
from snownlp import SnowNLP


if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')

file_path = '/home/skipper/study/python/project_v2/cmt_stit.txt'

def get_stit_label(sentences, file_path, sw_path, name = 'svm' ,language = 'CN'):
	labels = []
	try:
		model = dv.doc2vec_model(file_path, sw_path = sw_path, language = language)
		vec_list = dv.get_new_vec(model, sentences, sw_path, language)
		clf_res = mclf.get_classifier(file_path, name = name)
		labels = clf_res.predict(vec_list)
		# print labels
		return labels
	except Exception as e:
		print "From get_stit_label:\n\tUnexpect Error:{}".format(e)


def get_snow_label(sentences):
	labels = []
	try:
		for s in sentences:
			s = s.decode('utf-8')
			score = SnowNLP(s).sentiments
			if score > 0.5:
				labels.append('pos')
			else:
				labels.append('neg')
		return labels
	except Exception as e:
		print "From get_snow_label:\n\tUnexpect Error: {}".format(e)


def get_stit_prop(labels):
	pos = 0
	neg = 0
	cnt = 0
	try:
		cnt = len(labels)
		for ele in labels:
			if ele == 'pos':
				pos += 1
			elif ele == 'neg':
				neg += 1
			else:
				print "Sentiment type in not support!"
		# return 1.0*pos/cnt, 1.0*neg/cnt
		return 1.0*pos/cnt
	except Exception as e:
		print "From get_stit_prop:\n\tUnexpect Error: {}".format(e)


if __name__ == '__main__':
	st_list = []
	sentences = '''
		你这话我不爱听，废铁怎么了？垃圾怎么了？这破烂经费换茅台
		不会太快,说实话目前歼八还是主力
		军建务实，媒体爱吹
		sB文章，炸农田和炸麦田有区别吗？
		日本二战时就做到了
		今天天气不错啊
		因为他遇到了QQ，可是他其实并不开心'''

	# st_list.append(sentence)
	st_list = sentences.split('\n')

	file_path = '/home/skipper/study/python/project_v2/cmt_stit.txt'
	stopwords_path = "/home/skipper/nltk_data/Other_data/stopwords/stopsign.txt"
	svm_label = get_stit_label(st_list, file_path = file_path, \
											 sw_path = stopwords_path, name = "svm", language = "CN")
	print svm_label
	print svm_label[0]