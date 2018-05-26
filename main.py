import os
import sys
import time
import topic
import sentiment
import mycluster
import pandas as pd
import preprocess as prep
import mongodb_io as mgio
import netease_4_10 as crawl
from math import sqrt
from pymongo import MongoClient
from datetime import datetime

if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')


def main(date_start = None, date_end = None, n_clusters = 0, days = 5, saving = 0, show = 0):
	if saving == 1:
		import myvisual as visual
	else:
		import myvisual_show as visual
	sw_path = "/home/skipper/study/python/project/text/news_stopwords.txt"
	sw_list = prep.get_stopwords(sw_path)

	# new_insert = crawl.crawl_new(5)
	# state = mgio.sync()
	# print state
	# if new_insert > 0 or state == 0: 
	# 	mgio.art_tokenize()
	# 	mgio.rm_sp_tokens(sw_list)
	# 	mgio.pos_clean_tokens()

	# date_start = datetime(2018, 5, 3)
	# date_end = datetime(2018, 5, 6)
	# date_start = '2018/5/1'
	# date_end = '2018/5/6'

	if date_start and date_end:
		s_eles = date_start.split('/')
		s_eles = [int(i) for i in s_eles]
		s_eles = [str(i) for i in s_eles]
		d_st = datetime(int(s_eles[0]), int(s_eles[1]), int(s_eles[2]))
		e_eles = date_end.split('/')
		e_eles = [int(i) for i in e_eles]
		e_eles = [str(i) for i in e_eles]
		d_end = datetime(int(e_eles[0]), int(e_eles[1]), int(e_eles[2]), 23, 59, 59)
		if n_clusters == 0:
			base_path = '_'.join(s_eles)+'-'+'_'.join(e_eles)+'-orign'
		else:
			base_path = '_'.join(s_eles)+'-'+'_'.join(e_eles)+'-Clusters_%s'%str(n_clusters)
		print "The store paht: %s"%base_path
	else:
		c_t = time.localtime(time.time())
		tag_time = crawl.get_point_time(days)		#  0 present today 0:0   -1 present tommorow
		b = str(tag_time).split()[0].split('-')
		# print b
		b = [int(i) for i in b]
		b = [str(i) for i in b]
		# print b
		if n_clusters == 0:
			base_path = '_'.join(b)+'-'+'_'.join([str(c_t[0]), str(c_t[1]), str(c_t[2])])+'-orign'
		else:
			base_path = '_'.join(b)+'-'+'_'.join([str(c_t[0]), str(c_t[1]), str(c_t[2])])+'-Clusters_%s'%str(n_clusters)
		print "The store path: %s"%base_path
	flask_path = '/static/img/'+base_path
	print flask_path

	if os.path.exists('/home/skipper/study/python/project_v2/app'+flask_path) and show == 0:
		p_list = ['mds.jpg', 'pca.jpg', 'bar.jpg', 'pie.jpg']
		p_list = [flask_path+'/'+i for i in p_list]
		p_list.append(base_path)
		print "The main function return file path list:"
		print p_list
		return p_list
	else:
		path = '/home/skipper/study/python/project_v2/app'+flask_path
		if saving == 1:
			os.mkdir(path)

		print "Loading data from the MongoDB......"
		if date_start and date_end:
			target = mgio.get_target_1(d_st, d_end)
		else:
			target = mgio.get_target(tag_time)

		data = prep.convert_to_dataframe(target)
		cnt = len(data)
		doc_id = list(data.id)
# -------------------------------------------------------------------
		print "The number of article: %d"%cnt
		print "Detail as follows:"
		df = pd.DataFrame(data, columns = ['id','date', 'title', 'url'])
		print df
# -------------------------------------------------------------------

	# Whether using title or content, it is diffcult to find a optimal cluster k value.

	# One Method-----:
	# Using the title clustering		
	# The words is few, and the result of clustering is not optimal 
		# tokens_string = []
		# for i in range(cnt):
		# 	title_keywords = []
		# 	if len(data.keywords[i]) > 1:	# article have keywords
		# 		title_keywords = data.title[i] + '\t\t'+' '.join(data.keywords[i])
		# 	else:
		# 		title_keywords = data.title[i]
		# 	tokens_string.append(' '.join(prep.tokenize(title_keywords, sw_list = sw_list, language = 'CN')))
		# for ele in tokens_string:
		# 	print ele
	# Another Method----:
	# Using the article content clustering  # A lot of words
		tokens_string = list(data.im_tokens)
		# for ele in tokens_string:
		# 	print ele

# -------------------------------------------------------------------
		d = {'id': data['id'], 'date':data['date'], 'keywords': tokens_string}
		df = pd.DataFrame(d)
		print df
# -------------------------------------------------------------------

	# 	tokens_string = list(data.rs_tokens)
	# # Using the pyLDAvis showing the result
	# 	# Convert tokens_string to tokens_list(gensim)
	# 	tokens = [ele.split() for ele in tokens_string]
	# 	lda, corpus_BOW, dictionary = topic.get_ldavis_data(tokens, 5)	
	# 	visual.show_lda(lda, corpus_BOW, dictionary)


		if cnt > 0:
			print "Creating TF TDM......"
			tf_matrix, dictionary = mycluster.get_tf_matrix(tokens_string)
			print "The length of dictionary: %d"%len(dictionary)
			print "Creating TF-IDF TDM......"
			tfidf_matrix = mycluster.get_tfidf_matrix(tf_matrix)

			# print len(tfidf_matrix)
			# print len(tfidf_matrix[0])
			# print tfidf_matrix[0]

	# Searching the k vaule, but the two method not effect as follows:
			# for m_value in range(5, 30):
			# 	visual.predict_k(tf_matrix, m_value)
			# k = visual.predict_k(tfidf_matrix, 30)
			# print k
			# visual.prediect_k_sc(tfidf_matrix, 30)


			print "Creating the words and weight of every doc......"
			docs_keywords_string, docs_words_weight = mycluster.get_first_n_words(tfidf_matrix, 10, dictionary)


# -------------------------------------------------------------------
			k_w = {}
			for i,ele in enumerate(docs_words_weight):
			    keys = ele.keys()
			    weight = ele.values()
			    k_w['%d_word'%i] = pd.Series(keys)
			    k_w['%d_weight'%i] = pd.Series(weight)

			df = pd.DataFrame(k_w)
			print df
# -------------------------------------------------------------------

	# Setting the k value
			# n_clusters = 10	
			if n_clusters == 0:
				n_clusters = int(sqrt(cnt/2))
			# n_clusters = 2
			print "The n_clusters is: %d"%n_clusters
			print "Clustering......"
			labels = mycluster.get_label_list(n_clusters, tfidf_matrix)
			# labels = mycluster.get_label_list(n_clusters, tf_matrix)
			data['cluster'] = labels
			index_list = list(data['cluster'].value_counts().index)
			# print index_list

# -------------------------------------------------------------------
			hot_sort = data['cluster'].value_counts()
			df = pd.DataFrame.from_dict({'Cluster Label': hot_sort.index, 'Article Count': hot_sort.values})
			df = pd.DataFrame(df, columns = ['Cluster Label', 'Article Count'])
			print df

			for i in index_list:
			    print "Cluster Lable: %d"%index_list[i]
			    print "# The count of article: %d"%hot_sort[i]
			    df = pd.DataFrame.from_dict({'id': list(pd.DataFrame(data.loc[data['cluster'] == i])['id']),\
			                                'title':list(pd.DataFrame(data.loc[data['cluster'] == i])['title']),\
			                                'url': list(pd.DataFrame(data.loc[data['cluster'] == i])['url'])})
			    df = pd.DataFrame(df, columns = ['id', 'title', 'url'])
			    print df
# -------------------------------------------------------------------

	# Get cluster topic
			clusters_topic_dict = {}
			clusters_art_number = {}
			
			# clusters_art_content = mycluster.get_clusters_detail(n_clusters, data, 'im_tokens') 
			# clusters_title_keywords = mycluster.get_clusters_detail(n_clusters, data, 'title_keywords')
			clusters_title_keywords = mycluster.get_clusters_detail(n_clusters, data, 'im_title') 
			# for i, art_list in enumerate(clusters_art_content):
			for i, art_list in enumerate(clusters_title_keywords):
				texts = [ele.split() for ele in art_list]
				t = topic.get_topic_string(texts)			# get topic according im_tokens through lda model
				clusters_topic_dict[index_list[i]] = t
				clusters_art_number[index_list[i]] = len(art_list)

			# for k,v in clusters_topic_dict.items():
			# 	print k, v
			# for k,v in clusters_art_number.items():
			# 	print k, v

# -------------------------------------------------------------------
			topic_list = []
			art_number_list = []
			c_classes_keywords_sort = []
			for idx in index_list:
			    topic_list.append(clusters_topic_dict[idx])
			    art_number_list.append(clusters_art_number[idx])
			    
			df = pd.DataFrame.from_dict({'Cluster Label': index_list, 'Article Count': art_number_list,\
			                            'Topic Based on Title': topic_list})
			df = pd.DataFrame(df, columns = ['Cluster Label', 'Article Count', 'Topic Based on Title'])
			print df
# -------------------------------------------------------------------




			visual.mds_show(tfidf_matrix, clusters_topic_dict, n_clusters, data, path, saving)
			visual.pca_show(tfidf_matrix, clusters_topic_dict, n_clusters, data, path, saving)
			# visual.pca_show_scatter(tfidf_matrix, clusters_topic_dict, n_clusters, data)
			# visual.cluster_barh(n_clusters, index_list, clusters_topic_dict, clusters_art_number)

	# Get cluster comments
			clusters_cmt_number = {}
			clusters_cmt_detail = []
			clusters_id_list = mycluster.get_clusters_detail(n_clusters, data, 'id')
			for i, cluster_id_list in enumerate(clusters_id_list):
				cmt_detail = mgio.id_get_cmts(cluster_id_list)			# return DataFrame format
				clusters_cmt_detail.append(cmt_detail)
				# print len(cmt_detail)
				clusters_cmt_number[index_list[i]] = len(cmt_detail) 

			# for k,v in clusters_cmt_number.items():
			# 	print k, v
			visual.cluster_barh_new(n_clusters, index_list, clusters_topic_dict,\
										 clusters_art_number, clusters_cmt_number, path, saving)

# -------------------------------------------------------------------
			cmt_number_list = []
			for idx in index_list:
			    cmt_number_list.append(clusters_cmt_number[idx])
			hot_sort = data['cluster'].value_counts()
			df = pd.DataFrame.from_dict({'Cluster Label': hot_sort.index, 'Comment Count': cmt_number_list})
			df = pd.DataFrame(df, columns = ['Cluster Label', 'Comment Count'])
			print df
# -------------------------------------------------------------------


	# Get cluster commnet sentiment propation
			file_path = '/home/skipper/study/python/project_v2/cmt_stit.txt'
			stopwords_path = "/home/skipper/nltk_data/Other_data/stopwords/stopsign.txt"

			d_stit_prop_dict = {}
			s_stit_prop_dict = {}
			
			for i, cmt_detail in enumerate(clusters_cmt_detail):
				cmt_list = list(cmt_detail['content'])
				svm_label = sentiment.get_stit_label(cmt_list, file_path = file_path, \
											 sw_path = stopwords_path, name = "svm", language = "CN")
				snow_label = sentiment.get_snow_label(cmt_list)
				# Add to DataFrame
				cmt_detail['d_label'] = svm_label
				cmt_detail['s_label'] = snow_label
				d_stit_prop_dict[index_list[i]] = sentiment.get_stit_prop(svm_label)
				s_stit_prop_dict[index_list[i]] = sentiment.get_stit_prop(snow_label)

			# print pd.DataFrame(cmt_detail, columns = ['d_label', 's_label', 'vote', 'against', 'content'])

			# for k,v in d_stit_prop_dict.items():
			# 	print k, v
			# for k,v in s_stit_prop_dict.items():
			# 	print k, v

# -------------------------------------------------------------------
			for i, cmt_detail in enumerate(clusters_cmt_detail):
			    print "# The Cluster label: %d"%index_list[i]
			    print "# The count of article: %d"%cmt_number_list[i]
			    df = pd.DataFrame(cmt_detail, columns = ['vote', 'against', 'd_label', 'content'])
			    print df
# -------------------------------------------------------------------


			visual.cluster_stit_pie(n_clusters, index_list, d_stit_prop_dict, clusters_topic_dict, path, saving)

			print "Creating the sub class Topic......"
			sub_cluster, sub_weight = mycluster.get_classes(n_clusters, data, docs_words_weight, docs_keywords_string)
			classes_keywords = mycluster.get_class_keywords(n_clusters, 3, sub_cluster, sub_weight)

			print "For K-means clustering "
			mycluster.all_output(n_clusters, classes_keywords, clusters_topic_dict, \
									sub_cluster, data, d_stit_prop_dict, s_stit_prop_dict)
			
		p_list = ['mds.jpg', 'pca.jpg', 'bar.jpg', 'pie.jpg']
		p_list = [flask_path+'/'+i for i in p_list]
		p_list.append(base_path)
		print "The main function return file path list:"
		print p_list
		return p_list

	
if __name__ == '__main__':
	# new_insert = crawl.crawl_new(1)
	# if new_insert > 0:
	# 	mgio.art_tokenize()
	# mgio.art_tokenize()
	date_start = '2018/4/25'
	date_end = '2018/4/26'
	main(date_start = date_start, date_end = date_end, show = 1)
	# main(date_start = date_start, date_end = date_end, n_clusters = 5, show = 1)
	# main(days = 2, show = 1)
	# main(days = 2, n_clusters = 3, show = 1)
	# main(days = 1, show = 1, saving = 1)
	# main(days = 1, n_clusters = 3, show = 1, saving = 1)
	# main(days = 3, show = 1)
	pass