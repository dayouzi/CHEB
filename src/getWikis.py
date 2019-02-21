#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from book import Book
from nltk.stem.porter import PorterStemmer
from nltk import pos_tag
from util import getArgMap
import sys,re,copy
from copy import deepcopy
import collections
from collections import *
from nltk.util import ngrams
import loadFile
from loadFile import *
import keyword_ext_dic
from keyword_ext_dic import *
from naiveLink import *
from keyword_tool import *
from nltk.util import ngrams
ps = PorterStemmer()
#convert wiki text to plain text
    
def getWikiText(wiki_content):
    content=''
    for line in wiki_content.replace('\r\n','\n').split('\n'):
            if line.startswith('==') and not line.startswith('==='):
                continue
            content=content+line
    return content
    
#get wiki sections for one wiki page
def parseWikiSec(wiki_content):
	sec_title = 'sec0'
	sec_content =''
	sec=[]
	sec_titles=[]
	for line in wiki_content.replace('\r\n','\n').split('\n'):
		if line.startswith('==') and not line.startswith('==='):
			if not sec_content == '':
				if 'references' in sec_title.lower() or 'see also' in sec_title.lower() or 'external link' in sec_title.lower():
					continue
				sec_titles.append(sec_title)
				sec.append(sec_title+'\n'+sec_content)
				sec_content=''
				tidx = line.find('==')#cannot use rfind because line ends with ==
				sec_title = line[tidx+2:-2].strip()
		else:
		    sec_content = sec_content+line+'\n'
		    
	sec_titles.append(sec_title)
	sec.append(sec_title+'\n'+sec_content)
	sec_titles.append('WHOLEPAGE')
	sec.append(wiki_content)
	return sec_titles,sec
	
def getBookKeywords(anchor_freq,tf_book_dict,doc_wiki):
	v_all_book=dict()
	for sec in tf_book_dict.keys():
		v_all_book[sec]=v_all_book.get(sec,set())
		for w in tf_book_dict[sec]:
			if tf_book_dict[sec][w] != 0:
				v_all_book[sec].add(w)
		for d in doc_wiki[sec]:
			if not d in anchor_freq.keys():
				continue
			for a in anchor_freq[d]:
				if anchor_freq[d][a] !=0:
					v_all_book[sec].add(a)
	return v_all_book
'''
fn: ../test/bookname
wordset: page titles appear in the text
'''
def getWikis(fn,wordset,redirs=dict(), title2title=dict()):
    	wiki2ext=set()
	keyword_wiki_redir=defaultdict(set)
	wikis=set()
	v_all=set()#all the keywords appear in the chapter
	wiki_contents_sec,anchor_freq,wiki_norm_sec =loadWiki(fn)
	#print anchor_freq.keys()
	wk_writer=open(fn+'_keyword_title','w')#keyword - wikipedia title; for debug; not necessary
	w_v_all=open(fn+'_allkeywords','w')
	wc_writer=open(fn+'_wiki_plain','a')
	wiki_writer=open(fn+'_wiki_text','a')
	anchor_writer=open(fn+'_wiki_anchor','a')
	
	for w in wordset:
		if '#' in w:
		    continue
		if w=='(' or w ==')' or w == '' or len(w)<2:
		    continue
		if '(disambiguation)'  in w:
                    continue
                
		for tt in title2title[w]:
		    	if tt=='(' or tt==')' or tt=='' or len(tt)<2:
		    	    continue
			
			if tt in redirs:
			    for ww in redirs[tt]:
				wikis.add(ww)
				keyword_wiki_redir[w].add(ww)
				v_all.add(ww)
			else:
                            wikis.add(tt)
                            keyword_wiki_redir[w].add(tt)
                            v_all.add(tt)
                        
		wk_writer.write('============= '+w.encode('utf-8')+'\n')
		for wr in keyword_wiki_redir[w]:
			wk_writer.write(wr.encode('utf-8')+'\n')
			
        #wiki pages to extract
	for t in wikis:
	    if not t in wiki_contents_sec.keys():
                wiki2ext.add(t)
	
	#print len(wikis)
	#print len(v_all)
	print 'number of title to extract '+str(len(wiki2ext))
	for num,wt in enumerate(wiki2ext):
		wikitext=get_wikipage_content(wt)#get wiki text
		wiki_writer.write( '~~~~~~~~~~~~~~~~~~~~~~~~~~ '+wt.encode('utf-8')+'\n')
		wiki_writer.write(wikitext.encode('utf-8')+'\n')
		#get and update anchord
		anchors = getAnchor(wikitext)
		anchor_freq[wt]=anchor_freq.get(wt,dict())
		for a in anchors.keys():
			anchor_freq[wt][a.lower()] = anchor_freq[wt].get(a.lower(),0)
			anchor_freq[wt][a.lower()] = anchors[a]
			#v_all.add(a.lower())
		anchor_writer.write( '~~~~~~~~~~~~~~~~~~ '+wt.encode('utf-8')+'\n')
		sorted_anchor=sorted(anchor_freq[wt].items(), key=lambda x: x[1], reverse=True)
		for s in sorted_anchor:
			anchor_writer.write(s[0].encode('utf-8')+'\t'+str(s[1])+'\n')
		
		plaintext=content_ext(wt) #get plain text
		wc_writer.write( '~~~~~~~~~~~~~~~~~~~~~ '+wt.encode('utf-8')+'\n')#update wiki plaintext
		wc_writer.write(plaintext.encode('utf-8')+'\n')
		
		
		sec_titles,sec=parseWikiSec(plaintext)
		#update norm length of each section; In current method, only 'WHOLEPAGE'
		for i in xrange(len(sec_titles)):
			wiki_contents_sec[wt][sec_titles[i]]=sec[i]
			
	
	
	for v in v_all:
		w_v_all.write(v.encode('utf-8')+'\n')
        print '~~~~~~~~~~~~LEN OF VALL'+str(len(v_all))
    
	return anchor_freq,wiki_contents_sec, wikis

def loadWiki(fn,suffix=''):
	
	#load each section seperately
	wiki_contents_sec=defaultdict(lambda:defaultdict(str))
	wiki_contents = loadWiki_One(fn+'_wiki_plain'+suffix)
	
	for wt in wiki_contents:
		sec_titles,sec=parseWikiSec(wiki_contents[wt])
		for i in xrange(len(sec_titles)):
			wiki_contents_sec[wt][sec_titles[i]]=sec[i]
		wiki_contents_sec[wt]['WHOLEPAGE']=wiki_contents[wt]
	anchor_freq = loadWiki_Two(fn+'_wiki_anchor'+suffix)
	wiki_2norm_sec = loadWikiNorm_bySec(fn+'_wiki_sec_norm'+suffix)
   	
   	
   	'''
   	if  os.path.isfile(fn+'_allkeywords'+suffix):
   		reader = open(fn+'_allkeywords'+suffix,'r')
   		for line in reader:
   			v_all.add(line.strip())
   	'''
	return wiki_contents_sec,anchor_freq,wiki_2norm_sec
