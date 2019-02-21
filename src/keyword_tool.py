#!/usr/bin
# -*- coding: utf-8 -*-
from __future__ import division
import numpy
from numpy import *
import os,sys,collections,re
from collections import *
import math
from loadFile import *
from nltk.stem.porter import PorterStemmer
import nltk
ps = PorterStemmer()
from nltk.tokenize import word_tokenize
#1: c1 is before c2
def chapterCmp(c1,c2,delimiter='.'):
    if c1 == c2:
        return 0
    c1_s = c1.split(delimiter)
    c2_s = c2.split(delimiter)
    
    for i in xrange(min(len(c1_s),len(c2_s))):
        if c1_s[i].endswith('*'): c1_s[i]=int(c1_s[i][:-1])
        else:c1_s[i]=int(c1_s[i])
        if c2_s[i].endswith('*'): c2_s[i]=int(c2_s[i][:-1])
        else:c2_s[i]=int(c2_s[i])
    
        if c1_s[i] < c2_s[i]:
            return 1
        elif c1_s[i] > c2_s[i]:
            return -1
    if len(c1_s) < len(c2_s):
        return 1
    elif len(c1_s) > len(c2_s):
        return -1
#two titles are equal
def equalTitle(w1,w2):
	if w1.lower() == w2.lower(): 
	#and len(w1.split()) > 1:
		return 1
	w1=re.split('\s|-',w1.strip().lower())
	w2=re.split('\s|-',w2.strip().lower())
	#print w1
	if len(w1) != len(w2):
		return 0
	i=0
	while i<len(w1):
		if ps.stem(w1[i])!=ps.stem(w2[i]):
			return 0
		i=i+1
	return 1
#if one title contains or equal to another one
#sameTitle(w1,w2) = sameTitle(w2,w1)
def sameTitle(w1,w2):
    w1=w1.replace('#',' ');w2=w2.replace('#',' ')
    w1_temp=' '.join(ps.stem(i) for i in w1.split())
    w2_temp=' '.join(ps.stem(i) for i in w2.split())
    if (w1_temp.lower() in w2_temp.lower() or w2_temp.lower() in w1_temp.lower()) and len(w2_temp.split())>1 and len(w1_temp.split())>1: 
        return 1
	
    w1=re.split('\s|-',w1.strip().lower())
    w2=re.split('\s|-',w2.strip().lower())
    if len(w1) != len(w2):
        return 0
    i=0
    while i<len(w1):
        if ps.stem(w1[i])!=ps.stem(w2[i]):
            return 0
        i=i+1
    return 1

def calc_ltc_TFIDF(tf,df,num_instances,normD):
	#1 + log_2 term frequency(t, d) x log_2 (N / document frequency(t)) } / { || d || } 
	if tf==0:
	    return 0
	if float(normD) ==0.0:
		return 0
	return (1+(math.log(tf,2))*(math.log(num_instances/df,2)))/float(normD)
	
def normDocVec(sentences):
    	ws=nltk.word_tokenize(sentences)
        c_stem =  ' '.join(ps.stem(x.lower().replace('\r',' ').replace('\n',' ')) for x in ws)
	s=0
	words=dict()
	for w in c_stem.split(' '):
		if w == u'.' or w == u'' or w==u'?' or w==u',' or w==u'-' or w==u'(' or w==u')':
			continue
		words[w]=words.get(w,0)+1
	for w in words.keys():
		s=s+words[w]*words[w]
	
	return math.sqrt(s)
#jaccard: two lists of words/links
def jaccard(l1, l2):
    if len(l1)==0 or len(l2)==0:
    	return 0
    return len(set(l1)&set(l2))/len(set(l1)|set(l2))

#def pmi(l1, l2):
    


def combineDict(u,v):
#return two list,parameter is two dictionaries
	uu=[];vv=[]
	key=list(set(u.keys())|set(v.keys()));key.sort()
        for  k in key:
		if k not in u:
			u[k]=0.0
		if k not in v:
			v[k]=0.0
	for k in u:
		uu.append(u[k])
		vv.append(v[k])
	return uu,vv
	
def cosine_distance(u, v):
    """
    Returns the cosine of the angle between vectors v and u. This is equal to
    u.v / |u||v|.
    """
    if u is None or v is None or len(u)==0 or len(v)==0:
    	    return 0
    s=math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v))
    if s == 0:
    	return 0
    return numpy.dot(u, v) /s

def cosine_distance_dic(dic1, dic2):
    if dic1 is None or dic2 is None or len(dic1)==0 or len(dic2)==0:
    	    return 0
    ks=set(dic1.keys()).union(set(dic2.keys()))
    
    u=[];v=[]
    for k in ks:
        u.append(dic1[k])
        v.append(dic2[k])
    
    s=math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v))
    if s == 0:
    	return 0
    return numpy.dot(u, v) /s 
   


def dicNorm(dic):
    normDic=defaultdict(lambda:defaultdict(float))
    for k in dic:
        s=sum(dic[k].values())
        if s == 0:
            for k1 in dic[k]: normDic[k][k1]=dic[k][k1]
        else:
            for k1 in dic[k]: normDic[k][k1]=dic[k][k1]/s
    return normDic
            
def stemTexts(text,sents):
    s_stem=''
    for x in text.split():
        x=x.strip()
        if len(x)<2:
            continue
        
        if x[-1] in sents:
            x=x[:-1]
            
        if len(stemming(x))>=4:
            x=stemming(x) 
        s_stem=s_stem+' '+x
    return s_stem
#given a list of text and a list of words, get tf and idf
def getTFIDFVec(texts, dic):
    #dic=gensim.corpora.Dictionary([list(words)])
    tfidf=defaultdict(lambda:defaultdict(float))
    grams=[]
    for text in texts:
        gram=[]
        for w in GenNgram(text.split()):
            gram.append(w)
        grams.append(gram)
    corpus=[dic.doc2bow(gram) for gram in grams]
    tfidf_model=gensim.models.tfidfmodel.TdidfModel(corpus)
    for i,model in enumerate(corpus):
        for p in model[corpus[i]]:
            tfidf[i][p[0]]=p[1]
    return tfidf
