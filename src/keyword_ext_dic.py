#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from book import Book
from nltk.stem.porter import PorterStemmer
from nltk import pos_tag
from util import getArgMap
import sys,re,copy
import collections
from collections import *
from nltk.util import ngrams
from keyword_tool import *
import nltk
from loadFile import *
from nltk.tokenize import word_tokenize

ps = PorterStemmer()

argMap = getArgMap(sys.argv[1:])
bookname = argMap.get('-b','')
doc_suffix=argMap.get('-s','')
path = '../test/'+bookname+'/'

#vocabulary is the original vocabulary
#stem2dic is the defaultdict(list) key is the stemming form of the word. values are words
#df defaultdict(int)
# c is content
def exactMatch_byWords(c,vocabulary,df,stem2dic,stopword=()):
	tf_temp=wordFreq(c,stopword)
	new_voc=stem2dic.keys()
	wl=set()
	tf=defaultdict(int)
	for w in tf_temp.keys():
		if w in stopword or len(w) < 3:
			continue
		if w in vocabulary :
		    tf[w]=tf_temp[w]
		    if not w in wl:
			    df[w]=df[w]+1
			    wl.add(w)
		else:
		    sp = stemPhrase(w)
		    if sp in new_voc :
		    	for v in stem2dic[sp]:
		    	    tf[v]=tf[v]+tf_temp[w]
			    if not v in wl:
			    	df[v]=df[v]+1
				wl.add(v)
		    	if len(stem2dic[sp]) == 0:
		    	    print sp
		
	return tf

def GenNgram(words,stopword=(),min=1,max=4):
	grams=[]
	n=min
	while n<=max:
	    g=ngrams(words, n)
	    for gram in g:
	    	temp=' '.join(gg for gg in gram)
	    	
		if not temp in stopword:
			grams.append(temp)
		#if n==2:
		#	print temp.encode('utf-8')
	    n=n+1
	return grams
def stemPhrase(w):
    if len(w.split()) == 1 and len(w) < 4:
    	return w
    return ' '.join(stemming(x) for x in w.split())

#return the frequency of all n-grams in given content c
def wordFreq(c,stopword=(),n=4):
	words_temp=word_tokenize(c)
	words=[]
	sents=['.',',',':',';','!','?','(',')','\'','-',']','[','—']
	for w in words_temp:
	    if w in sents:
		    continue
	    
	    words.append(w.strip())
	grams=[]
	n=1
	while n<=4:
	    g=ngrams(words, n)
	    for gram in g:
	    	temp=' '.join(gg for gg in gram)
		if not temp in stopword:
			grams.append(temp)
		#if n==2:
		#	print temp.encode('utf-8')
	    n=n+1
	tf=defaultdict(int)
	
	for w in grams:
		tf[w]=tf[w]+1
	
	return tf

def wiki_exactMath_BySec(wikis,whole,vocabulary,stem2dic,wiki_sec):
	stopword=loadStopWord()
	df=defaultdict(int)
	tf=defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
	for t in wikis:
		for sec in whole[t]:
		    	s=wiki_sec[t][sec].lower()
		    	tf_sec=exactMatch_byWords(s,vocabulary,df,stem2dic,stopword) 
		    	for w in tf_sec.keys():
			    	tf[t][sec][w] = tf_sec[w]
	return tf,df
def wiki_exactMath_BySec_v0(wikis,whole,vocabulary,stem2dic,wiki_sec):
	stopword=loadStopWord()
	df=defaultdict(int)
	tf=defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
	for t in wikis:
	    if whole[t] == 0:
	    	#print 'WHILE IN '+t
	    	s=wiki_sec[t]['WHOLEPAGE'].lower()
	    	tf_sec=exactMatch_byWords(s,vocabulary,df,stem2dic,stopword)
	    	for w in tf_sec.keys(): 
	    	    tf[t]['WHOLEPAGE'][w] = tf_sec[w]
		if len(tf_sec) == 0:
			print 'WIKI MATCH IS 0 '+t.encode('utf-8')
			print len(s)
	    else:
	    	#wiki_sec=getWikiSec(contents[t])
	    	for sec in wiki_sec[t]:
	    	    	#if sec == 'WHOLEPAGE':
	    	    	#    continue
		    	s=wiki_sec[t][sec].lower()
		    	tf_sec=exactMatch_byWords(s,vocabulary,df,stem2dic,stopword)
			#if len(tf_sec) == 0:
				#print 'WIKI MATCH IS 0 '+t.encode('utf-8')+'\t'+sec.encode('utf-8') 
		    	for w in tf_sec.keys():
			    	tf[t][sec][w] = tf_sec[w]
	return tf,df
#match book and wiki dictionary
def book_exactMatch(b,path,bookname,doc_suffix,vocabulary,stem2dic,content_context=0):
    stopword=loadStopWord()
    df_book_dict=defaultdict(int)
    tf_book_dict=defaultdict(lambda:defaultdict(int))
    
    book_writer = open(path+bookname+doc_suffix,'w')
    for i,sec in enumerate(b.toc):
        book_title = sec.title.lower().replace('¡¯', '\'')
	print '=========== {0} {1}'.format(sec.sid, book_title)
	if content_context == 0:
		s=sec.content.lower().replace('\r',' ').replace('\n',' ').replace('\r\n',' ').decode('utf-8')	
	else:
		s=sec.context.lower().replace('\r',' ').replace('\n',' ').replace('\r\n',' ').decode('utf-8')	
	tf_book_sec=exactMatch_byWords(s,vocabulary,df_book_dict,stem2dic,stopword)
	
	for w in tf_book_sec.keys():
	    tf_book_dict[i][w]=tf_book_sec[w]
    for i,sec in enumerate(b.toc):
        book_title = sec.title.lower().replace('¡¯', '\'')
        book_writer.write('=========== {0} {1}'.format(sec.sid,book_title.encode('utf-8'))+'\n')
	for w in tf_book_dict[i].keys():
		book_writer.write(w.encode('utf-8')+'\t'+str(tf_book_dict[i][w])+'\t'+str(df_book_dict[w])+'\n')
    return tf_book_dict,df_book_dict #return new matched dictionary

def loadStopWord():
    stopwordlist= './stopword_patent'
    stopword=set()
    with open(stopwordlist) as s:
    	    for w in s:
    	    	    stopword.add(w.strip())
    return stopword

#match keywords by section; whole book as one word vector: too much calculation;used for match book contents on domain dic+wiki anchors
def book_exactMatch_Sec(path,bookname,doc_suffix,vocabulary,stem2dic):
    stopword=loadStopWord()
    b = Book(bookname, path+bookname+'.toc')
    
    df_book_dict=defaultdict(int) 
    #match book and wiki dictionary
    book_writer = open(path+bookname+doc_suffix,'w')
    tf_book_dict=defaultdict(lambda:defaultdict(int))
    for i,sec in enumerate(b.toc):
    	
        book_title = sec.title.lower().replace('¡¯', '\'')
	print '=========== {0} {1}'.format(sec.sid, book_title)
	if '_context' in doc_suffix:
		print 'MATCHING CONTEXT'
		reader = open(path+bookname+'_context'+'/'+str(i),'r')
	else:
		reader = open(path+bookname+'_content'+'/'+str(i),'r')

	s=reader.read().lower().replace('\r',' ').replace('\n',' ').replace('\r\n',' ').decode('utf-8')	
	tf_sec_dict = exactMatch_byWords(s,vocabulary,df_book_dict,stem2dic,stopword)
	for w in tf_sec_dict.keys():
	    tf_book_dict[i][w]=tf_sec_dict[w]
        
    for i,sec in enumerate(b.toc):
        book_title = sec.title.lower().replace('¡¯', '\'')
        book_writer.write('=========== {0} {1}'.format(sec.sid,book_title.encode('utf-8'))+'\n')
	for w in tf_book_dict[i].keys():
		book_writer.write(w.encode('utf-8')+'\t'+str(tf_book_dict[i][w])+'\t'+str(df_book_dict[w])+'\n')
	
    return tf_book_dict,df_book_dict #return new matched dictionary


def book_norm(path,bookname,doc_suffix):
    book_2norm=defaultdict(float)
    b = Book(bookname, path+bookname+'.toc')
    print 'write to '+path+bookname+doc_suffix+'_norms'
    w=open(path+bookname+'_norms','w')
    for i,sec in enumerate(b.toc):
            book_title = sec.title.lower().replace('¡¯', '\'')
            w.write('=========== {0} {1}'.format(sec.sid, book_title)+'\n')
	    if '_context' in doc_suffix:
            	reader = open(path+bookname+'_context'+'/'+str(i),'r')
            else:	
		reader = open(path+bookname+'_content'+'/'+str(i),'r')
#s=reader.read().lower().replace('\r',' ').replace('\n',' ').replace('\r\n',' ').decode('utf-8')
	    s=reader.read().lower().decode('utf-8')
            book_2norm[i]=normDocVec(s)
            w.write(str(book_2norm[i])+'\n')
    return book_2norm


