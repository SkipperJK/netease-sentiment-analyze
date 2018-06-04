from gensim import corpora, models


def get_topic_string(texts, num_topics = 1):
	dictionary = corpora.Dictionary(texts) 
	corpus_BOW = [dictionary.doc2bow(text) for text in texts] 
	tfidf = models.TfidfModel(corpus_BOW, dictionary = dictionary, normalize = True)
	corpus_tfidf = tfidf[corpus_BOW]
	lda = models.ldamodel.LdaModel(corpus = corpus_BOW, id2word = dictionary, num_topics = num_topics, alpha = 'auto')
	words_list = []
	for i in lda.show_topic(0):
		words_list.append(i[0])
	return ' '.join(words_list)


def get_ldavis_data(texts, num_topics = 1):
	dictionary = corpora.Dictionary(texts) 
	corpus_BOW = [dictionary.doc2bow(text) for text in texts] 
	lda = models.ldamodel.LdaModel(corpus = corpus_BOW, id2word = dictionary, num_topics = num_topics, alpha = 'auto')
	return lda, corpus_BOW, dictionary

