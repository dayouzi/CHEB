#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from util import getArgMap
import sys,re
import collections
from collections import *
from nltk.util import ngrams



argMap = getArgMap(sys.argv[1:])
thres = int(argMap.get('-thres',0))
domain = argMap.get('-d','')
bookname = argMap.get('-b','')
wiki=int(argMap.get('-w','-1'))
path = '../test/'+bookname+'/'
#thres_set={'data_mining':15,'computer network':15,'economics':10,'precalculus':5,'physics':20,'general':5,'data_structure':15}
def clsFilter(thres,domain):
    r=open(path+bookname+'.wikis','r')
    redir=defaultdict(str)
    for line in r:
    	redir[line.split('\t')[0].strip()]=line
    cls_stopword={'science':['law','programmers','chess','philosophy','journals','researchers','philosophers','mathematicians','billionaires',\
                             'awards','companies','history','market','players','physicists','business terms','turing','amazon','conference',\
                             'international','fellows','inventions','association','publisher','university','surnames','philosophy concepts',\
                             'disambiguition','history','historians','Albert Einstein','physicists','districts','establishments','islands','regions',\
                             'london','streets','areas','faculty','leaders','jews','colonies','anti-communists','knights of the gGarter','democracies',\
                             'inventors','countries','engineers','nations','writers','member states','artists','founder','researchers','scientists','republics',\
                             'alumni','members','history','philosophers','recipients','people','universities','university','fellow','films','sociological terminnology',\
                             'companies','deaths','birth','mathematicians','novelists','chemical elements','organizations','institutes','buildings',\
                             'business term','randomness'],\
                  'economics':['theory','philosophy of science','empiricism','justification','journal','publications','school',\
                               'established','teams','town','neighborhood','geography']}
    r=open(path+bookname+'.catcnt','r')
    cls_clean_w=open(path+bookname+'.catcnt_clean','w')
    wikis2cat_clean_w=open(path+bookname+'.wikis2cat_clean','w')
    wikis_clean_w=open(path+bookname+'.wikis_clean','w')
    wikis_drop_w = open(path+bookname+'.wikis_dropped','w')
    cls_clean=defaultdict(int)
    for c in r:
	flag=0
    	cs=c.split('\t') 
    	for w in cls_stopword[domain]:
	    if w in cs[0].lower():
		flag=1
		break
	if domain in cls_stopword:
	    for w in cls_stopword[domain]:
	    	if w in cs[0].lower():
		    flag =1
		    break
	if int(cs[1])<=thres:
	    flag = 1
	if flag == 0:
            
    	    cls_clean_w.write(c.strip()+'\n')
    	    cls_clean[cs[0]]=int(cs[1])
    	
    r=open(path+bookname+'.wiki2cats','r')
    for line in r:
    	wt=line.split('\t')[0].strip()
    	cls=eval(line.split('\t')[1])
    	count=0
    	for c in cls:
	   
    	    if cls_clean[c]>0:
    	    	count=count+1
    	    	
    	if len(cls)>0 and count/len(cls) >= 0.5:
            
    	    wikis2cat_clean_w.write(line.strip()+'\n')
            if redir[wt]=='':
                wikis_clean_w.write(wt.strip()+'\n')
                continue
    	    wikis_clean_w.write(redir[wt].strip()+'\n')
        else:
            wikis_drop_w.write(redir[wt].strip()+'\n')



if __name__ == "__main__":
	
	
	'''
	if not bookname in thres_set.keys():
		ts=thres_set['general']
	else:
		ts=thres_set[bookname]
	'''
	ts=thres
	clsFilter(ts,domain)
	#capSmallFilter()

