#coding=utf-8
import os
import sys
import csv
import numpy as np
from gensim.models import doc2vec
from preprocess import tokenize
from preprocess import get_stopwords

if sys.getdefaultencoding() != 'utf-8':
	reload(sys)
	sys.setdefaultencoding('utf-8')
# default_sw_path = '/home/skipper/nltk_data/Other_data/stopwords/CNENstopwords.txt'
default_sw_path = '/home/skipper/nltk_data/Other_data/stopwords/stopsign.txt'


class Documents(object):
	def __init__(self, file_path, \
					sw_path = default_sw_path, language = 'CN'):
		self.file_path = file_path
		self.file_name = os.path.splitext(os.path.split(file_path)[1])[0]
		self.sw_path = sw_path
		self.label_list = []
		self.lines = 0
		self.t = language

	def __iter__(self):
		sw_list = get_stopwords(self.sw_path)
		f = open(self.file_path)
		csv_reader = csv.reader(f, delimiter = '\t')
		for i, line in enumerate(csv_reader):
			if i+1 > self.lines:
				self.lines = i+1
				self.label_list.append(line[0])		# get the doc label
			tag = "%s_%s"%(self.file_name, str(i))
			# print '---1'
			yield doc2vec.TaggedDocument(tokenize(line[1], sw_list, self.t), tags = [tag])


def store_doc_label(file_path):
	directory = os.path.join(os.path.split(file_path)[0], 'doc2vec')
	if not os.path.exists(directory):
		os.makedirs(directory)
	label_path = directory+'labels'
	label_list = []
	f = open(label_path, "w")
	csv_reader = csv.reader(f, delimiter = '\t')
	for line in csv_reader:
		label_list.append(line[0])
	f.write(' '.join(label_list))
	f.close()


# docs is string list
def get_new_vec(model, docs, sw_path = default_sw_path, language = "CN"):
	sw_list = get_stopwords(sw_path)
	new_doc_vec = []
	try:
		for doc in docs:
			tokens = tokenize(doc, sw_list, language = language)
			doc_vec = model.infer_vector(tokens)
			new_doc_vec.append(doc_vec)
		return new_doc_vec
	except Exception as e:
		print "From get_new_vec:\n\tUnexpect Error:{}".format(e)


def doc2vec_model(file_path, sw_path = default_sw_path, language = 'CN'):
	directory = os.path.join(os.path.split(file_path)[0], 'doc2vec')
	if not os.path.exists(directory):
		os.makedirs(directory)
	model_path = os.path.join(directory, 'model')
	vector_path = os.path.join(directory, 'vector.npy')
	label_path = os.path.join(directory, 'labels')

	try:
		model = doc2vec.Doc2Vec.load(model_path)
		print "Reading the doc2vec model from %s"%model_path
	except:
		print "Building doc2vec model..."

		docs = Documents(file_path, sw_path = sw_path, language = language)

		# print len(docs.label_list)

		
		model = doc2vec.Doc2Vec(vector_size = 100, min_count = 5, alpha=0.025, min_alpha=0.025)
		model.build_vocab(docs)

		print len(docs.label_list)
		
		with open(label_path, "w") as fp:
			fp.write(' '.join(docs.label_list))
		print "Storing the docs label to -->%s"%label_path

		model.train(docs, total_examples=model.corpus_count, epochs=model.epochs)
		for epoch in range(5):
			model.train(docs, total_examples=model.corpus_count, epochs=model.epochs)
			model.alpha -= 0.002 
			model.min_alpha = model.alpha

		model.save(model_path)
		print "Storing the doc2vec model to %s"%model_path

		np.save(vector_path, model.docvecs)
		print "Storing the doc2vec vector to %s"%vector_path
	return model


if __name__ == '__main__':
	# doc_path = "/home/skipper/nltk_data/smsspamcollection/SMSSpamCollection"
	cmt_path = '/home/skipper/study/python/project_v2/cmt_stit.txt'
	
	# model = doc2vec_model(doc_path, language = "EN")
	# sentiment analysis, just need remove some signal
	model = doc2vec_model(cmt_path, sw_path = "/home/skipper/nltk_data/Other_data/stopwords/stopsign.txt")
	