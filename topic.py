from gensim import corpora, models


def get_topic_string(texts, num_topics = 1):
	dictionary = corpora.Dictionary(texts) 
	corpus_BOW = [dictionary.doc2bow(text) for text in texts] 
	tfidf = models.TfidfModel(corpus_BOW, dictionary = dictionary, normalize = True)
	corpus_tfidf = tfidf[corpus_BOW]
# LDA model
	# print "LDA..."
	# lda = models.ldamodel.LdaModel(corpus = corpus_tfidf, id2word = dictionary, num_topics = num_topics, alpha = 'auto')
	lda = models.ldamodel.LdaModel(corpus = corpus_BOW, id2word = dictionary, num_topics = num_topics, alpha = 'auto')
	words_list = []
	for i in lda.show_topic(0):
		# print i[0],
		words_list.append(i[0])
	return ' '.join(words_list)

	# print lda.print_topic(0)
	# for pattern in lda.show_topics():
	# 	print pattern[1]
# LSI model
	# print "LSI..."	
	# lsi = models.LsiModel(corpus = corpus_tfidf, id2word = dictionary, num_topics = 1)
	# for i in  lsi.show_topics():
	# 	print i[1]


def get_ldavis_data(texts, num_topics = 1):
	dictionary = corpora.Dictionary(texts) 
	corpus_BOW = [dictionary.doc2bow(text) for text in texts] 
	# tfidf = models.TfidfModel(corpus_BOW, dictionary = dictionary, normalize = True)
	# corpus_tfidf = tfidf[corpus_BOW]

	lda = models.ldamodel.LdaModel(corpus = corpus_BOW, id2word = dictionary, num_topics = num_topics, alpha = 'auto')
	return lda, corpus_BOW, dictionary

