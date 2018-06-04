import os
import sys
import main as a
from app import app
import myclassifier
import sentiment as stit
import mongodb_io as mgio
import judge_exist as j_e
import preprocess as prep
from datetime import datetime
from flask import render_template, request, jsonify
cwd = os.getcwd()
sys.path.append(cwd)

@app.route('/')		# set the trigger url, call the following function
def f1():
	# return "/ and excute the f1() function"
	return render_template('main.html')

@app.route('/test')
def test():
	return render_template('test.html')
	
@app.route('/crawl')
def crawl():
	crawl_state = mgio.main()
	print "From view.py crawl: %s"%crawl_state
	return jsonify(crawl_state = crawl_state)


@app.route('/query_art_count')
def query():
	date_start = request.args.get('date_st', None, type = str)
	date_end = request.args.get('date_end', None, type = str)
	days = request.args.get('days', 0, type = int)

	print "From view.py query: %s %s %d"%(date_start, date_end, days)
	d_st, d_end = None, None
	if date_start and date_end:
		eles = date_start.split('/')
		d_st = datetime(int(eles[0]), int(eles[1]), int(eles[2]))
		eles = date_end.split('/')
		d_end = datetime(int(eles[0]), int(eles[1]), int(eles[2]), 23, 59, 59)
		# print d_st, d_end
		cnt = mgio.judge_art_cnt(d_st, d_end)
		# print cnt
	else:
		cnt = mgio.judge_art_cnt_1(days)
	return jsonify(count = cnt)


@app.route('/exist')
def judge_exist():
	date_start = request.args.get('date_st', None, type = str)
	date_end = request.args.get('date_end', None, type = str)
	days = request.args.get('days', 0, type = int)
	n_clusters = request.args.get('n_clusters', 0, type = int)

	print "From view.py judge_exist: %s %s %d %d"%(date_start, date_end, n_clusters, days)

	result = j_e.is_exist(date_start, date_end, n_clusters = n_clusters, days = days)
	return jsonify(result = result)


@app.route('/analyse')
def analyse():
	date_start = request.args.get('date_st', None, type = str)
	date_end = request.args.get('date_end', None, type = str)
	days = request.args.get('days', 0, type = int)
	n_clusters = request.args.get('n_clusters', 0, type = int)
	
	print "From view.py analyse: %s %s %d %d"%(date_start, date_end, days, n_clusters)
	filename = a.main(date_start = date_start, date_end = date_end, n_clusters = n_clusters, days = days, saving = 1)
	file_dict = {}
	file_dict['mds'] = filename[0]
	file_dict['pca'] = filename[1]
	file_dict['bar'] = filename[2]
	file_dict['pie'] = filename[3]
	file_dict['date_range'] = filename[4]

	return jsonify(file_dict)


@app.route('/tokenize')
def tokenize():
	content = request.args.get('content', None, type = str)

	print "From view.py tokenize:%s"%content
	sw_list = prep.get_stopwords("/home/skipper/study/python/project/text/news_stopwords.txt")
	tokens = prep.tokenize(content, sw_list, language = "CN")
	for i in tokens:
		print i
	tokens_string = '/'.join(tokens)
	print tokens_string
	pos_tag, pos_string = prep.pos_test(tokens)

	print "From view.py tokenize: %s\n%s\n%s\n"%(tokens_string, pos_tag, pos_string)
	detail = {}
	detail['tokens_string'] = tokens_string
	detail['pos_tag'] = pos_tag
	detail['pos_string'] = pos_string

	return jsonify(detail)


@app.route('/sentiment')
def sentiment():
	# pass
	st_list = []
	comments = request.args.get('comments', None, type = str)
	file_path = request.args.get('file_path', None, type = str)
	# st_list.append(sentence)
	st_list = comments.split('\n')

	print "From view.py comments:%s"%comments
	print "From view.py train corpus:%s"%file_path
	# file_path = '/home/skipper/study/python/project/cmt_stit.txt'
	stopwords_path = "/home/skipper/nltk_data/Other_data/stopwords/stopsign.txt"
	svm_label = stit.get_stit_label(st_list, file_path = file_path, \
											 sw_path = stopwords_path, name = "svm", language = "CN")
	string = ''
	for i in svm_label:
		string = string+'/'+i
	return jsonify(label = string)


@app.route('/accuracy')
def accuracy():
	file_path = request.args.get('file_path', None, type = str)
	print "From view.py accuracy:%s"%file_path
	report  = myclassifier.svm_classifier_accuracy(file_path)
	return jsonify(report = report)
