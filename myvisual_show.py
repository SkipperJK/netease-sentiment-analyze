import math
import random
import pyLDAvis
import pyLDAvis.gensim
import numpy as np
import pandas as pd
import matplotlib as mpl
# mpl.use('Agg')					# plt.show() so can not add this line code
import matplotlib.pyplot as plt
from math import sqrt
from matplotlib import colors
from matplotlib import markers
from sklearn.cluster import KMeans
from sklearn.manifold import MDS
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity


def cluster_barh_new(n_clusters, index_list, clusters_topic_dict, clusters_art_number,\
					 clusters_cmt_number, path, saving):
	topic_list = []
	art_number_list = []
	cmt_number_list = []
	for idx in index_list:
		topic_list.append(clusters_topic_dict[idx].decode('utf-8'))
		art_number_list.append(clusters_art_number[idx])
		cmt_number_list.append(clusters_cmt_number[idx])

	colors_list = get_colors_list(n_clusters)

	fig, ax = plt.subplots(nrows=1, ncols=2, figsize = (18, int(n_clusters*1)))
	y_pos = np.arange(len(topic_list))+1
	x = np.array(art_number_list)
# article number bar
	ax[0].barh(y_pos, x, align='center', color='green')
	ax[0].set_yticks(y_pos)
	ax[0].set_yticklabels(topic_list)
	ax[0].invert_yaxis()  # labels read top-to-bottom
	ax[0].set_xlabel('Article Number')
	ax[0].set_title('Hot Sort')
	ax[0].set_xlim(0, max(art_number_list)*1.2)
	ax[0].grid(axis = 'x')
	for i in range(len(x)):
		ax[0].text(x[i], y_pos[i], x[i])	# Tag art number for every bar
# comment number bar
	x = np.array(cmt_number_list)
	ax[1].barh(y_pos, x, align='center', color='green')
	ax[1].invert_yaxis()  # labels read top-to-bottom
	ax[1].set_xlabel('Comments Number')
	ax[1].set_title('Corresponding Commnets')
	ax[1].set_xlim(0, max(cmt_number_list)*1.2)
	ax[1].grid(axis = 'x')
	for i in range(len(x)):
		ax[1].text(x[i], y_pos[i], x[i])	# Tag art number for every bar

	plt.tight_layout()
	
	print path+'/bar.jpg'
	if saving == 1:
		plt.savefig(path+'/bar.jpg')
	if saving == 0:
		plt.show()
	plt.close()


def cluster_stit_pie(n_clusters, index_list, d_stit_prop_dict, clusters_topic_dict,\
						path, saving):
	d_stit_prop = []
	topic_list = []
	for idx in index_list:
		d_stit_prop.append(d_stit_prop_dict[idx])
		topic_list.append(clusters_topic_dict[idx].decode('utf-8'))

	colors_list = get_colors_list(n_clusters)

	labels = ['Pos', 'Neg']
	explode = [0.1, 0]
	# nrows = int(n_clusters/4)+1			# ERROR 8 3-lines but should be 2-lines
	nrows = int(math.ceil(1.0*n_clusters/4))
	# print "nrows: %d, ncols: 4"%nrows
	fig, ax = plt.subplots(nrows=nrows, ncols=4, figsize = (15,6))
	# print ax.shape

	if nrows < 2:
		for i in range(ax.size):
			if i < n_clusters:
				ax[i].pie([100*d_stit_prop[i], 100-100*d_stit_prop[i]], labels = labels,\
							explode = explode, colors = ['g', 'r'], autopct='%3.1f %%',\
	        				shadow=True, labeldistance=1.1, startangle = 90,pctdistance = 0.6)
				ax[i].set_aspect('equal')
				ax[i].set_xlabel(topic_list[i])
			else:
				ax[i].pie([50, 50])
				ax[i].cla()
				ax[i].axis('off')
	else:
		sub_num = 0
		for i in range(nrows):
			for j in range(4):
				if sub_num < n_clusters:
					ax[i][j].pie([100*d_stit_prop[sub_num], 100-100*d_stit_prop[sub_num]], labels = labels,\
									explode = explode, colors = ['g', 'r'], autopct='%3.2f %%', shadow=True,\
									 labeldistance=1.1, startangle = 90,pctdistance = 0.6)
					ax[i][j].set_aspect('equal')
					ax[i][j].set_xlabel(topic_list[sub_num])
					sub_num += 1
				else:
					sub_num += 1
					ax[i][j].pie([50, 50])
					ax[i][j].cla()
					ax[i][j].axis('off')

	plt.tight_layout()
	
	print path+'/pie.jpg'
	if saving == 1:
		plt.savefig(path+'/pie.jpg')
	if saving == 0:
		plt.show()
	plt.close()


def pca_show_scatter(tfidf_matrix, clusters_topic_dict, n_clusters, data):
	pca = PCA(n_components = 2)
	pos = pca.fit_transform(tfidf_matrix)
	groups = data.groupby('cluster')
	cluster_colors = get_colors_list(n_clusters)
	cluster_markers = get_marker_list(n_clusters)

	pos_list = []
	for cluster_label, group in groups:
		position_dict = {}
		x_list = []
		y_list = []
		index_list = list(group.index)
		# print index_list
		for ele in index_list:
			x_list.append(pos[ele][0])
			y_list.append(pos[ele][1])
		position_dict['x'] = x_list
		position_dict['y'] = y_list
		pos_list.append(position_dict)

	for i, ele in enumerate(pos_list):
		color = cluster_colors[i]
		marker = cluster_markers[i]
		plt.scatter(ele['x'], ele['y'], c = color, marker = marker)
	plt.show()


def pca_show(tfidf_matrix, clusters_topic_dict, n_clusters, data, path, saving):
	pca = PCA(n_components = 2)
	pos = pca.fit_transform(tfidf_matrix)
	xs, ys = pos[:, 0], pos[:, 1]	# get every point value of x and y axis.
	cluster_colors = get_colors_list(n_clusters)
	for k, v in clusters_topic_dict.items():
		clusters_topic_dict[k] = v.decode('utf-8')
	label_list = list(data['cluster'])
	df = pd.DataFrame(dict(x = xs, y = ys, label = label_list))
	groups = df.groupby('label')
	fig, ax = plt.subplots(figsize = (17, 9))
	ax.margins(0.05)
	for cluster_label, group in groups:			# DataFrame data.column / data[column]
		ax.plot(group.x, group.y, marker = 'o', linestyle = '', ms = 12, \
				label = clusters_topic_dict[cluster_label], color = cluster_colors[cluster_label],\
				 mec = 'none')
		ax.set_aspect('auto')
		ax.tick_params(
			axis = 'x',
			which = 'both',
			bottom = False,
			top = False,
			labelbottom = False)
		ax.tick_params(
			axis = 'y',
			which = 'both',
			bottom = False,
			top = False,
			labelbottom = False)
	ax.legend(numpoints = 1)
	
	print path+'/pca.jpg'
	if saving == 1:
		plt.savefig(path+'/pca.jpg')
	if saving == 0:
		plt.show()
	plt.close()


def mds_show(tfidf_matrix, clusters_topic_dict, n_clusters, data, path, saving):
	dist = 1- cosine_similarity(tfidf_matrix)
	mds = MDS(n_components = 2, dissimilarity = 'precomputed', random_state = 1)
	pos = mds.fit_transform(dist)
	xs, ys = pos[:, 0], pos[:, 1]	# get every point value of x and y axis.

	cluster_colors = get_colors_list(n_clusters)
	for k, v in clusters_topic_dict.items():
		clusters_topic_dict[k] = v.decode('utf-8')

	label_list = list(data['cluster'])
	df = pd.DataFrame(dict(x = xs, y = ys, label = label_list))
	groups = df.groupby('label')

	fig, ax = plt.subplots(figsize = (17, 9))
	ax.margins(0.05)

	for cluster_label, group in groups:			# DataFrame data.column / data[column]
		ax.plot(group.x, group.y, marker = 'o', linestyle = '', ms = 12, \
				label = clusters_topic_dict[cluster_label], color = cluster_colors[cluster_label],\
				 mec = 'none')
		ax.set_aspect('auto')
		ax.tick_params(
			axis = 'x',
			which = 'both',
			bottom = False,
			top = False,
			labelbottom = False)
		ax.tick_params(
			axis = 'y',
			which = 'both',
			bottom = False,
			top = False,
			labelbottom = False)
	ax.legend(numpoints = 1)
	
	print path+'/mds.jpg'
	if saving == 1:
		plt.savefig(path+'/mds.jpg')
	if saving == 0:
		plt.show()
	plt.close()


def predict_k(tfidf_matrix, max_value):
	SSE = []
	for k in range(1,max_value):
		estimator = KMeans(n_clusters = k)
		estimator.fit(tfidf_matrix)
		SSE.append(estimator.inertia_)

	print SSE
	X = range(1,max_value)
	plt.xlabel('k')
	plt.ylabel('SSE')
	plt.plot(X, SSE, 'o-')
	plt.show()
	# plt.savefig('/home/skipper/study/python/project/kmeans/tfidf/Max_%d.jpg'%max_value)

	min_dis = -1
	k = -1
	for i in range(1,max_value):
		dis = sqrt(i**2 + SSE[i-1]**2)
		if dis < min_dis or min_dis == -1:
			min_dis = dis
			k = i
	return k


def prediect_k_sc(tfidf_matrix, max_value):
	Scores = []
	for k in range(1, max_value):
		estimator = KMeans(n_clusters = k)
		estimator.fit(tfidf_matrix)
		Scores.append(silhouette_score(tfidf_matrix, estimator.labels_, metric = 'euclidean'))
	X = range(1, max_value)
	print len(X), len(Scores)
	plt.xlabel('k')
	plt.ylabel('Silhouette Score')
	plt.plot(X, Scores, 'o-')
	plt.show()


def get_colors_list(n_clusters):
	colors_list = list(colors._colors_full_map.values())
	use_colors = []
	while len(use_colors) != n_clusters:
		use_colors.append(colors_list[random.randint(0, len(colors_list)-1)])
	# print use_colors
	return use_colors


def get_marker_list(n_clusters):
	m = markers.MarkerStyle()
	markers_list = list(m.filled_markers)
	# print markers_list
	# print len(markers_list)
	use_markers = []
	while len(use_markers) != n_clusters:
		use_markers.append(markers_list[random.randint(0, len(markers_list)-1)])
	print use_markers
	return use_markers


def show_lda(lda, corpus, dictionary, number = 001):
	# corpus, dictionary = get_corpus_dictionary()
 	# lda = LdaModel(corpus=corpus,num_topics=2)
    data = pyLDAvis.gensim.prepare(lda, corpus, dictionary)
    pyLDAvis.show(data,open_browser=True)
    # pyLDAvis.show(data,open_browser=False)
    # pyLDAvis.save_html(data, '/home/skipper/study/python/project/visual/lda_%d.html'%number) 

if __name__ == '__main__':
	# pass
	# label_scatter(4)
	# get_marker_list(4)
	pass
	# cluster_stit_pie(1, 1, 1)