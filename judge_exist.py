import os
import time
import netease_4_10 as crawl
from datetime import datetime

cwd = os.getcwd()

def is_exist(date_start = None, date_end = None, n_clusters = 0, days = 5):

	if date_start and date_end:
		s_eles = date_start.split('/')
		s_eles = [int(i) for i in s_eles]
		s_eles = [str(i) for i in s_eles]
		e_eles = date_end.split('/')
		e_eles = [int(i) for i in e_eles]
		e_eles = [str(i) for i in e_eles]
		# base_path = '_'.join(s_eles)+'-'+'_'.join(e_eles)
		if n_clusters == 0:
			base_path = '_'.join(s_eles)+'-'+'_'.join(e_eles)+'-orign'
		else:
			base_path = '_'.join(s_eles)+'-'+'_'.join(e_eles)+'-Clusters_%s'%str(n_clusters)
		print "The store path: %s"%base_path
	else:
		c_t = time.localtime(time.time())
		# print c_t[0], c_t[1], c_t[2]
		tag_time = crawl.get_point_time(days)		#  0 present today 0:0   -1 present tommorow
		b = str(tag_time).split()[0].split('-')
		b = [int(i) for i in b]
		b = [str(i) for i in b]
		# base_path = '_'.join(b)+'-'+'_'.join([str(c_t[0]), str(c_t[1]), str(c_t[2])])
		if n_clusters == 0:
			base_path = '_'.join(b)+'-'+'_'.join([str(c_t[0]), str(c_t[1]), str(c_t[2])])+'-orign'
		else:
			base_path = '_'.join(b)+'-'+'_'.join([str(c_t[0]), str(c_t[1]), str(c_t[2])])+'-Clusters_%s'%str(n_clusters)
		print "The store path: %s"%base_path

	path = os.path.join(cwd, 'app/static/img/')+base_path
	
	if os.path.exists(path):
		return "The analyse result have exists, you can directly load from the disk!"
	else:
		return "Have not analyse, if you want to analyse, it may be take some time"


if __name__ == '__main__':
	print is_exist('2018/4/25', '2018/4/30')
	print is_exist()