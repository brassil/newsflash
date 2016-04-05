from datetime import datetime
import time


months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}


def seconds(d):
	'''
	e.g. input d = Wed Apr 22 13:54:11 +0000 2015
	return Unix time seconds
	'''
	d = d.split()
	t = (int(x) for x in d[3].split(':'))

	# datetime obj: year, month num, day; asterisk unpacks tuple
	dt = datetime(int(d[5]), months[d[1]], int(d[2]), *t)

	return time.mktime(dt.timetuple())