import os
import csv  
# import pickle 
from sklearn.externals import joblib
import numpy as np
import train_doc_vector as dv
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib      
from sklearn.preprocessing import StandardScaler
from sklearn import svm 						# SVM classifier
from sklearn.naive_bayes import MultinomialNB 	# NB classifier
from sklearn.linear_model import SGDClassifier  # SGD classifier

cwd = os.getcwd()


def get_classifier(file_path, name = 'svm'):
	try:
		directory = os.path.join(os.path.split(file_path)[0], 'classifier')
		classifier_path = os.path.join(directory, name+'.pkl')
		clf_res = joblib.load(classifier_path)
		print "Loading the %s Classifier from: %s"%(name.upper(), classifier_path)
	except:
		print "The %s Classifier is not Persistence, Creating the classifier..."%name.upper()
		# get the doc2vec vector and label using to train svm model
		vector, label = get_vec_label(file_path)
		# print len(vector), len(label)
		if name == 'svm':
			# Train the svm classifier
			clf_res = svm_classifier_persistence(vector, label, file_path)
		elif name == 'sgd':
			clf_res = sgd_classifier(vector, label, file_path)
	return clf_res


# def get_vec_label(file_path, vec_path, label_path):
def get_vec_label(file_path):
	try:
		directory = os.path.join(os.path.split(file_path)[0], 'doc2vec')
		file_name = os.path.splitext(os.path.split(file_path)[1])[0]
		vec_path = os.path.join(directory, 'vector.npy')
		label_path = os.path.join(directory, 'labels')
		# print vec_path, label_path

		# IF the doc2vec not exist, Create it.
		if not os.path.exists(vec_path) and not os.path.exists(label_path):
			print "The doc2vec not exist, so must create the doc2vec model first!\tCreating......"
			dv.doc2vec_model(file_path)

		with open(label_path) as fp:
			label_list = fp.read().split()
		# print len(label_list)

		doc_vec_matrix = []
		doc_vec = np.load(vec_path)
		doc_vec = doc_vec.tolist()
		# print len(doc_vec)
		for i, label in enumerate(label_list):
			tag = "%s_%s"%(file_name, str(i))
			doc_vec_matrix.append(doc_vec[tag])
			# print len(doc_vec_matrix)

		return doc_vec_matrix, label_list
	except Exception as e:
		print "From: get_vec_label()\n\tUnexpect Error: {}".format(e)


def svm_classifier_persistence(vector, label, file_path):
	try:
		directory = os.path.join(os.path.split(file_path)[0], 'classifier')
		classifier_path = os.path.join(directory, 'svm.pkl')
		if not os.path.exists(directory):
			os.mkdir(directory)
			
		print "Persistence SVM Classifier....."

		clf = svm.LinearSVC()
		clf_res = clf.fit(vector, label)
		joblib.dump(clf, classifier_path)

		return clf_res
	except Exception as e:
		print "From: svm_classifier_persistence()\n\tUnexpect Error: {}".format(e)


def svm_classifier_accuracy(file_path):
	try:
		presist_path = os.path.join(cwd, 'text/accuracy.txt')
		if os.path.exists(presist_path):
			with open(presist_path) as fp:
				report = fp.read()
			return report
		else:
			vector, label = get_vec_label(file_path)
			directory = os.path.join(os.path.split(file_path)[0], 'classifier')
			classifier_path = os.path.join(directory, 'svm.pkl')

			print "SVM Classifier:"
			d_train, d_test, l_train, l_test = train_test_split(vector, label, test_size = 0.33, random_state=42)

			sc = StandardScaler()
			sc.fit(d_train)
			d_train = sc.transform(d_train)
			d_test = sc.transform(d_test)

			clf = svm.LinearSVC()
			clf_res = clf.fit(d_train, l_train)
			# joblib.dump(clf, classifier_path)
			string_1 = "Test Accuracy of VSM: %.2f"%clf_res.score(d_test, l_test)
			svm_predicted = clf_res.predict(d_test)
			cm = confusion_matrix(l_test, svm_predicted)
			string_2 = classification_report(l_test, svm_predicted)
			# print svm_predicted
			print cm
			print string_1
			print string_2
			
			report = string_1 + '\n' + string_2
			with open(presist_path, "w") as fp:
				fp.write(report)
			return report
	except Exception as e:
		print "From: svm_classifier()\n\tUnexpect Error: {}".format(e)


if __name__ == '__main__':
	file_path = os.path.join(cwd, 'text/cmt_stit.txt')
	print svm_classifier_accuracy(file_path)