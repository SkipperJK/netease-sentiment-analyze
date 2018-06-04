import sys
import json
import jieba
import sklearn
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from gensim import corpora, models


if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')



def union_dict(*dicts):
	ks = set(sum([d.keys() for d in dicts], []))
	total = {}
	for k in ks:
		total[k] = sum([d.get(k, 0) for d in dicts])
	return total


# Term Frequecy matrix
def get_tf_matrix(tdm_words):
	try:
		vectorizer = CountVectorizer()
		tf_matrix = vectorizer.fit_transform(tdm_words)       
		words = vectorizer.get_feature_names()
		return tf_matrix, words
	except Exception as e:
		print "From:get_tf_matrix:\n\tUnexpect Error: {}".format(e)


def get_tfidf_matrix(tf_matrix):
	try:
		transformer = TfidfTransformer()
		tfidf_matrix = transformer.fit_transform(tf_matrix)
		return tfidf_matrix.toarray()
	except Exception as e:
		print "From:get_tfidf_matrix:\n\tUnexpect Error: {}".format(e)


# get first n words of every article according the descend tfidf weight sorting.
def get_first_n_words(tfidf_matrix, n, dictionary):
	try:
		docs_keywords_string = []
		docs_words_weight = []   # the sub element should be a dict
		# np.argsort(-ndarray, axis = 1)  # Descendding Sort, axis = 1 represent the column.
		descend_sort_index = np.argsort(-tfidf_matrix, axis = 1)
		for idx in range(len(tfidf_matrix)):
			words_list = []
			words_weight = {}
			for i in range(n):
				# get the i-th index  				# sort according the tfidf weight
				point = descend_sort_index[idx][i]  
				if tfidf_matrix[idx][point] > 0:                    
					# get the index correspond word and add to words_list
					words_list.append(dictionary[point])	
					# get the first_n_words weight for the idx doc					
					words_weight[dictionary[point]] = tfidf_matrix[idx][point]	

			docs_keywords_string.append(' '.join(words_list))
			docs_words_weight.append(words_weight)
		return docs_keywords_string, docs_words_weight
	except Exception as e:
		print "From:get_first_n_words:\n\tUnexpect Error: {}".format(e)


def get_label_list(n_clusters, weight):
	try:
		kmeans = KMeans(n_clusters = n_clusters, init = "k-means++")
		# kmeans = KMeans(n_clusters = n_clusters, init = "random")
		km_model = kmeans.fit(weight)
		return km_model.labels_
	except Exception as e:
		print "From:get_label_list:\n\tUnexpect Error: {}".format(e)


def get_classes(n_clusters, data,  docs_words_weight, docs_keywords_string):
	try:
		sub_weight = [[] for i in range(n_clusters)]
		sub_cluster = [[] for i in range(n_clusters)]
		for i in range(n_clusters):
			class_weight = []
			number_list = list(pd.DataFrame(data.loc[data['cluster'] == i]).index) # get the art number of every class
			for j in number_list:
				sub_cluster[i].append(docs_keywords_string[j])
				class_weight.append(docs_words_weight[j])
			sub_weight[i] = (union_dict(*class_weight))
		return sub_cluster, sub_weight

	except Exception as e:
		print "From:get_classes:\n\tUnexpect Error: {}".format(e)


def get_class_keywords(n_clusters, count,  sub_cluster, sub_weight):
	try:
		classes_keywords = []
		for i in range(n_clusters):
			class_keywords = []
			tf_m_weight = []
			sub_tf_matrix, sub_words = get_tf_matrix(sub_cluster[i])
			m = sub_tf_matrix.toarray()						# m is two dimension	
			# get the keywords frequency of articles in the same cluster
			tf_sum = np.sum(m, axis = 0)												# get trem frequency
			for wtf in range(len(tf_sum)):
				tf_m_weight.append(tf_sum[wtf] * sub_weight[i][sub_words[wtf]])
			tf_m_weight = np.array(tf_m_weight)										# get tf * weight
			sort_idx = np.argsort(-tf_m_weight, axis = 0)
			# sort according the tf * tfidf weight
			for j in range(count):
				class_keywords.append(sub_words[sort_idx[j]])
			classes_keywords.append(' '.join(class_keywords))
		return classes_keywords
	except Exception as e:
		print "From:get_class_keywords:\n\tUnexpect Error: {}".format(e)


# Throught the col parameter can get the cluster information.
def get_clusters_detail(n_clusters, data, col):
	try:
		clusters_list = []
		hot_sort = data['cluster'].value_counts()
		print list(hot_sort.index)
		
		for i in list(hot_sort.index):
			art_list = list(pd.DataFrame(data.loc[data['cluster'] == i])[col])
			clusters_list.append(art_list)
		# print len(clusters_art_list)
		# for i in clusters_art_list:
		# 	print len(i)
		return clusters_list
	except Exception as e:
		print "From:get_cluster_art:\n\tUnexpect Error: {}".format(e)


def all_output(n_clusters, classes_keywords, clusters_topic_dict, \
						sub_cluster, data, d_stit_prop_dict, s_stit_prop_dict):
	try:
		hot_sort = data['cluster'].value_counts()

		print list(hot_sort.index)
		for i in list(hot_sort.index):
			print "# The count of article: %d"%hot_sort[i]
			print "# %d class --- keywords: %s"%(i, classes_keywords[i])
			print "# %d class --- topic: %s"%(i, clusters_topic_dict[i])
			print "# Sentiment: doc2vec---pos: %f , neg: %f"%(d_stit_prop_dict[i]*100, 100-d_stit_prop_dict[i]*100)
			print "# Sentiment: snownlp---pos: %f , neg: %f"%(s_stit_prop_dict[i]*100, 100-s_stit_prop_dict[i]*100)

			number_list = list(pd.DataFrame(data.loc[data['cluster'] == i]).index)
			id_list = list(pd.DataFrame(data.loc[data['cluster'] == i])['id'])
			url_list = list(pd.DataFrame(data.loc[data['cluster'] == i])['url'])
			for j, number in enumerate(number_list):
				print number, sub_cluster[i][j], id_list[j]

	except Exception as e:
		print "From:all_output:\n\tUnexpect Error: {}".format(e)
