#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from nltk.stem.porter import PorterStemmer
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from nltk import pos_tag
from util import getArgMap
import sys,re,copy,os
import collections
from collections import *
import nltk
from nltk.util import ngrams
from book import Book

ps = PorterStemmer()
argMap = getArgMap(sys.argv[1:])
bookname = argMap.get('-b','')
tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
'''
load file with format
======= title
keywords \t keywords \t tf
as a dic(dic(int))
usage:
for
'''
ps = PorterStemmer()
def stemming(w):
	w=w.strip()
	if w.endswith('aes') or w.endswith('ues') or w.endswith('oes'):
	    	return w[:-1]
	elif  w.endswith('s') and not w.endswith('ss') and not w.endswith('sses') and not w.endswith('is'):
	    	return w[:-1]
	elif (w.endswith('ed')  and not w.endswith('ied')) or w.endswith('sses'):
		# or (w.endswith('es') and not w.endswith('ies')):
	    	return w[:-2]
	elif w.endswith('ing'):
	    	return w[:-3]
	elif w.endswith('ies') or w.endswith('ied'):
	    	return w[:-3]+'y'
	return w
def loadContent(bn,i):
    return '../../test/'+bn+'/'+bn+'_content/'+str(i)

#freq: 0 no frequency for term specified
# t1: title t2:anchor
def loadTerms(bn,t1='subtitle',t2='index',freq=0):
    if freq == 0:
    	fn='../../test/'+bn+'/'+bn+'.terms'
    else:
    	fn='../../test/'+bn+'/'+bn+'.cls'
    print 'load file '+fn
    if not os.path.isfile(fn):
		return d
    reader = open(fn,'r')
    if freq == 0:
    	terms=defaultdict(lambda:defaultdict(set))
    else:
    	terms_title=defaultdict(lambda:defaultdict(int))
    	terms_anchor=defaultdict(lambda:defaultdict(int))
    	cls_title=defaultdict(int) #freq of a category in the dictionary file
    	cls_anchor=defaultdict(int) #freq of a category in the dictionary file
    counter = -1
    key=''
    for line in reader:
       	if line.startswith('====='):
            counter=counter+1
            tidx=line.rfind('===')
            title=line[tidx+3:].strip()
        elif line.startswith('#')  :
            if line.split()[1]==t1:
                key=t1
            else:
            	key=t2
        else:
            if freq == 0:
            	terms[counter][key].add(line.strip())
            else:

            	if len(line.strip().split('\t')) == 1:
            	    terms_title[title][line.strip()] = terms_title[title][line.strip()] + 1
            	    cls_title[line.strip()] = cls_title[line.strip()] + 1
            	else:
            	    terms_anchor[title][line.strip().split('\t')[0]] = terms_anchor[title][line.strip().split('\t')[0]] + int(line.strip().split('\t')[1])
            	    cls_anchor[line.strip().split('\t')[0]] = cls_anchor[line.strip().split('\t')[0]] + int(line.strip().split('\t')[1])

    if freq == 0:
    	return terms
    else:
    	return terms_title,cls_title,terms_anchor,cls_anchor


def loadWiki_One(filePath):
	#d=defaultdict(lambda:defaultdict(float))
        d=defaultdict(str)
	print 'load file '+filePath
        if not os.path.isfile(filePath):
                return d
	reader = open(filePath,'r')
	title=''
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('~~~~~~~~~~~~'):

			tidx=line.rfind('~~~')
			title=line[tidx+4:].strip()
		else:

                        d[title]=d[title]+line.strip()+'\n'
	return d

def loadWiki_Two(filePath):
        d=dict()
	print 'load file '+filePath
	if not os.path.isfile(filePath):
                return d
	reader = open(filePath,'r')
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('~~~~~~~~~~~~~~'):

			tidx=line.rfind('~~~')
			title=line[tidx+4:].strip()
			d[title]=d.get(title,dict())

		else:
			ls=line.strip().split('\t')
			if len(ls) < 2:

				continue
                        d[title]=d.get(title,dict())
                        d[title][ls[0]]=d[title].get(ls[0],0)
                        d[title][ls[0]]=float(ls[1])
	return d
#load concepts in each book chapter
def loadConcepts(bookname,path,suffix):
    	print 'load file '+path+bookname+suffix
	tf=defaultdict(lambda:defaultdict(int))
	df=defaultdict(int)
	titles=defaultdict(str)
	if not os.path.isfile(path+bookname+suffix):
		return titles,tf,df
	reader = open(path+bookname+suffix,'r')
	if not os.path.isfile(path+bookname+suffix):
		return titles,tf,df
	counter = -1
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('========='):
		   		counter=counter+1
				tidx=line.rfind('===')
				titles[counter]=line[tidx+4:].strip()


		else:
			ls=line.strip().split('\t')
			if len(ls) != 3:
				if ls[0]!='':
					df[ls[0]]=df.get(ls[0],0)
					tf[counter]=tf.get(counter,dict())
					tf[counter][ls[0]]=tf[counter].get(ls[0],0)
				continue
			df[ls[0]]=float(ls[2])
			tf[counter][ls[0]]=float(ls[1])

	return titles,tf,df


def loadWikiNorm_bySec(fn):
    	print 'load file '+fn
	wiki_sec_norm=defaultdict(lambda:defaultdict(float))
	if not os.path.isfile(fn):
		return wiki_sec_norm
	reader = open(fn,'r')
	wiki_title=''
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('~~~~~~~~~~~~~~~~~~'):
				tidx=line.rfind('~~~')
				wiki_title=line[tidx+4:].strip()
		else:
			wiki_sec_norm[wiki_title][line.strip().split('\t')[0]]=float(line.strip().split('\t')[1])
	return wiki_sec_norm
def loadWikiSections(fn,titles=[]):
	print 'load file'+fn
	reader = open(fn,'r')
	wiki_sec = defaultdict(lambda:defaultdict(str))
	if not os.path.isfile(fn):
		return wiki_sec
	wiki_title = ''
	wiki_content=''
	wiki_whole=''
	for line in reader:
		line  = line.decode('utf-8')
		if line.startswith('~~~~~~~~~~'):
			if  not wiki_content == '' and (wiki_title in titles or titles == []):
				sec_titles,sec=parseWikiSec(wiki_content)
				for i in xrange(len(sec_titles)):
					wiki_sec[wiki_title][sec_titles[i]]=sec[i]
					#wiki_sec[wiki_title]["WHOLEPAGE"]=wiki_sec[wiki_title]["WHOLEPAGE"]+sec[i]
				wiki_content = ''

			tidx = line.rfind('~~~')
			wiki_title = line[tidx+4:].strip()

		else:

			wiki_content=wiki_content+line

	return wiki_sec

#file format: wiki_title wiki_sec_title words tf df
def loadWikiConcepts_Sec(fn,i):
    	print 'load file '+fn
	tf=defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:defaultdict(int))))
	df=defaultdict(lambda:defaultdict(int))
	titles=defaultdict(str)
	if not os.path.isfile(fn):
		return tf,df
	reader = open(fn,'r')
	if not os.path.isfile(fn):
		return tf,df
	counter = -1
	wtitle=''
	flag = 0
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('========='):
				if flag==1:
					break
		   		counter=counter+1
				if counter != i:
					continue
				flag=1
				tidx=line.rfind('===')
				titles[counter]=line[tidx+4:].strip()
		elif line.startswith('~~~~~~')	:
				if counter != i:
					continue
				tidx=line.rfind('~~~')

				wtitle=line[tidx+4:].strip()
		else:
			if counter != i:
				continue
			#tf[counter][wtitle]=tf[counter].get(wtitle,dict())
			ls=line.strip().split('\t')
			if len(ls) != 5:
				continue
			df[counter][ls[2]]=int(ls[4])
			tf[counter][ls[0]][ls[1]][ls[2]]=int(ls[3])

	return tf,df


def loadBook_One(fn):
    	print 'load file '+fn
	reader = open(fn,'r')
	titles=defaultdict(str)
	d=defaultdict(float)
	counter = -1
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('========='):
		   		counter=counter+1
				tidx=line.rfind('===')
				titles[counter]=line[tidx+4:].strip()
		else:
			d[counter]=float(line.strip())
	return titles,d
def updateStem(wd,wd2stem):
    if wd not in wd2stem:
        wd2stem[wd] = ' '.join(map(lambda x:ps.stem(x), wd.split()))



def loadWikiDic(path,bookname):
        vocabulary = set()
	wikis =  set()
	wd2stem = dict()
	redirs = dict()

	title2title=defaultdict(set)

        print 'loading wiki titles'
        with open(path+bookname+'.wikis_clean') as f:
                for line in f:
                    s = line.replace('–','-').strip().split('\t')
                    wiki = s[0].decode('utf-8').strip()
		    if '#' in wiki:
			continue
                    wikis.add(wiki)

                    if wiki.lower() in title2title.keys():
                        continue
		    if '(' in wiki and ')' in wiki:
			new_wiki=wiki[:wiki.find('(')].strip()
		    else:
                        new_wiki = wiki
                    title2title[new_wiki.lower()].add(wiki)
                    title2title[wiki.lower()].add(wiki)
		    new_wiki=new_wiki.lower()
                    #updateStem(new_wiki,wd2stem)
                    vocabulary.add(new_wiki)
                    if len(s) > 1:

                        rds = map(lambda x: x.decode('utf-8'), s[1].split('|'))
                        for rd in rds:

                            rd=rd.strip()
                            wikis.add(rd)

                            if '(' in rd and ')' in rd:
				new_rd=rd[:rd.find('(')].strip()
                            else:
                                new_rd=rd
                            title2title[rd.lower()].add(rd)
                            title2title[new_rd.lower()].add(rd)
                            new_rd=new_rd.lower()
                            redirs[rd]=redirs.get(rd,set())
                            redirs[rd].add(wiki)
                            #updateStem(rd,wd2stem)
                            vocabulary.add(new_rd)



	print 'voc size'+str(len(vocabulary))
	print 'wiki sze '+str(len(wikis))
        return vocabulary, wikis, redirs ,title2title
#wiki includes both original titles and redirects
#voc includes the stemming style of orginal titles and redicts
#title2title is a link from voc to wiki
#redirs use the unstemming style, to get the orginial title of a stemming word, use redir[title2title[w]]
def loadWikiDicStem(path,bookname):
        vocabulary = set()
	wikis =  set()
	wd2stem = dict()
	redirs = dict()

	title2title=defaultdict(set)

        print 'loading wiki titles'+path+bookname+'.wikis_clean'
        with open(path+bookname+'.wikis_clean') as f:
                for line in f:
                    s = line.replace('–','-').strip().split('\t')
                    wiki = s[0].decode('utf-8').strip()
		    if '#' in wiki:
			continue
                    wikis.add(wiki)

                    if wiki.lower() in title2title.keys():
                        continue
		    if '(' in wiki and ')' in wiki:
			new_wiki=wiki[:wiki.find('(')].strip() if stemming(wiki[:wiki.find('(')].strip()) <4 else stemming(wiki[:wiki.find('(')].strip())
		    else:
                        new_wiki = wiki if stemming(wiki) <4 else stemming(wiki)
                    title2title[new_wiki.lower()].add(wiki)
                    title2title[wiki.lower()].add(wiki)
		    new_wiki=new_wiki.lower()
                    #updateStem(new_wiki,wd2stem)
                    vocabulary.add(new_wiki)

                    if len(s) > 1:
                        rds = map(lambda x: x.decode('utf-8'), s[1].split('|'))
                        for rd in rds:

                            rd=rd.strip()
                            wikis.add(rd)

                            if '(' in rd and ')' in rd:
				new_rd=rd[:rd.find('(')].strip() if stemming(rd[:rd.find('(')].strip()) <4 else stemming(rd[:rd.find('(')].strip())
                            else:
                                new_rd=rd if stemming(rd) <4 else stemming(rd)
                            title2title[rd.lower()].add(rd)
                            title2title[new_rd.lower()].add(rd)
                            new_rd=new_rd.lower()
                            redirs[rd]=redirs.get(rd,set())
                            redirs[rd].add(wiki)
                            #updateStem(rd,wd2stem)
                            vocabulary.add(new_rd)



	print 'voc size'+str(len(vocabulary))
	print 'wiki sze '+str(len(wikis))
        return vocabulary, wikis, redirs ,title2title


#title2title each key corresponds one value
def loadWikiDicStem_single(path,bookname):
        vocabulary = set()
	wikis =  set()
	wd2stem = dict()
	redirs = dict()

	title2title=defaultdict(str)

        print 'loading wiki titles'+path+bookname+'.wikis_clean'
        with open(path+bookname+'.wikis_clean') as f:
                for line in f:
                    s = line.replace('–','-').strip().split('\t')
                    wiki = s[0].decode('utf-8').strip()
		    if '#' in wiki:
			continue
                    wikis.add(wiki)

                    if wiki.lower() in title2title.keys():
                        continue
		    if '(' in wiki and ')' in wiki:
			new_wiki=wiki[:wiki.find('(')].strip() if stemming(wiki[:wiki.find('(')].strip()) <4 else stemming(wiki[:wiki.find('(')].strip())
		    else:
                        new_wiki = wiki if stemming(wiki) <4 else stemming(wiki)
                    if title2title[new_wiki.lower()]!='' or len(new_wiki)>len(title2title[new_wiki.lower()]):
			    title2title[new_wiki.lower()] = wiki
		    if title2title[wiki.lower()]!='' or len(wiki)>len(title2title[wiki.lower()]):
			    title2title[wiki.lower()] = wiki
		    new_wiki=new_wiki.lower()
                    vocabulary.add(new_wiki)
	return vocabulary, wikis, redirs ,title2title

def stemDic(vocabulary,stopword=set(),sents=[]):
    stem2dic = defaultdict(set)
    dic2stem = defaultdict(set)
    new_voc=set()
    for v in vocabulary:
    	if len(v)<3:
    		continue

    	if len(v.split()) == 1 and len(stemming(v)) < 4:
    	    stem2dic[v].add(v)
    	    dic2stem[v].add(v)
    	    new_voc.add(v)
    	else:
    	    v_new = ' '.join(vv if len(stemming(vv))<4 else stemming(vv) for vv in v.split())
    	    stem2dic[v].add(v_new)
    	    dic2stem[v_new].add(v)
    	    new_voc.add(v_new)
    #print new_voc
    return stem2dic,new_voc,dic2stem




def loadRank(fn,top=5000):

        print 'load file '+fn
	reader = open(fn,'r')
	t=defaultdict(list)
	sec_set=[]
	#counter = -1
        rank=0
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('====='):
                        rank=0
                        #counter=counter+1
			sec=line.split('\t')[1].strip()
			sec_set.append(sec)
		else:

                        if rank < top:
                            rank=rank+1
                            t[sec].append(line.split('\t')[0].strip())
	return t,sec_set

def loadRank2(fn,top=5000):
    	print 'load file '+fn
	reader = open(fn,'r')
	t=defaultdict(list)
	sec_set=[]
	counter = -1
        rank=0
	sec=''

	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('====='):
                        rank=0
                        counter=counter+1
			sec=line.split('\t')[1].strip()
			sec_set.append(sec)
		else:
			if len(line.split('\t'))<2: continue
                        if rank > top:
                            continue
                        rank=rank+1

			t[sec].append(float(line.split('\t')[1].strip()))
	return t,sec_set

def loadRankScore(fn,top=100):
    	print 'load file '+fn

	reader = open(fn,'r')
	t=defaultdict(lambda:defaultdict(float))
	sec_set=[]
	counter = -1
        sec=''
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('========='):
                        rank=0
                        counter=counter+1
			sec=line.split('\t')[1].strip()
			sec_set.append(sec)
		else:
			#print sec
			#print line
                        if rank >= top:
                            continue
                        if '(disambiguation)' in line:
                            continue
 			t[sec][line.split('\t')[0].strip()]=float(line.split('\t')[1])
			rank=rank+1
	return t,sec_set
def loadSim(fn,delimiter = '===='):
	reader=open(fn,'r')
	sim=defaultdict(lambda:defaultdict(float))
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith(delimiter):
			tidx=line.rfind(delimiter[0:3])
			title=line[tidx+4:].strip()
		else:
			sim[title][line.split('\t')[0].strip()] = float(line.split('\t')[1])
	return sim


#load _pre(_all).csv and return the keyword list
def loadPre(fn):
    print 'load file '+fn
    reader = open(fn,'r')
    keywords = set()
    pre = defaultdict(lambda:defaultdict(float))
    sections = defaultdict(str)
    for line in reader:
    	ls = line.decode('utf-8').split(';')
    	if line.startswith('#'):
    	    continue
    	if len(ls) < 5:
    	    continue

    	pre[ls[1]][ls[3]] = ls[4].strip()
        keywords.add(ls[1].lower().strip())
        keywords.add(ls[3].lower().strip())
        sections[ls[1]] = ls[0].strip()
        sections[ls[3]] = ls[2].strip()
    return keywords,sections,pre

def load_book_all_dict():
    titles, tf_book_all, df_book_all = loadConcepts(bookname,path,'_book_all'+doc_suffix)

    sec_ids = []
    dic=[]
    texts=[]
    for k in titles:
    	sec_id=titles[k].split()[0]
    	print sec_id
    	if not sec_id in sec_res:
    	    continue
    	doc=[]
    	for w in tf_book_all[k]:
    	    if w in dic:
    	    	doc.append((dic.index(w),tf_book_all[k][w]))
    	    else:
    	    	doc.append((len(dic),tf_book_all[k][w]))
    	    	dic.append(w)
    	texts.append(doc)
    	sec_ids.append(sec_id)

    return sec_ids,texts,dic

#load _wiki_anchor file; return defaultdict(wikititles: anchors:tf) ' df: defaultdict(int);wordset:set
def loadWikiAnchors(fn,titles = []):
    print 'load file'+fn
    reader = open(fn,'r')
    anchors = defaultdict(lambda:defaultdict(float))
    df = defaultdict(int)
    if not os.path.isfile(fn):
	return anchors
    wiki_title = ''


    wordset = set()
    for line in reader:
        line  = line.decode('utf-8')
        if line.startswith('~~~~~~~~~~'):
	    tidx = line.rfind('~~~')
	    wiki_title = line[tidx+4:].strip()


	else:
            if titles == [] or wiki_title in titles:
                anchors[wiki_title][line.split('\t')[0]] = float(line.split('\t')[1])
                wordset.add(line.split('\t')[0])
                df[line.split('\t')[0]] = df[line.split('\t')[0]] + 1
    return anchors,df, wordset


#=== title
#word1 frequency
def loadCitationNet(fn,titles = []):
    print 'load file'+fn
    reader = open(fn,'r')
    relations = defaultdict(lambda:defaultdict(float))
    if not os.path.isfile(fn):
    	return relations
    wiki_title = ''
    wordset = set()
    for line in reader:
        line  = line.decode('utf-8')
        if line.startswith('======='):
	    tidx = line.rfind('===')
	    wiki_title = line[tidx+4:].strip()


	else:
            if titles == [] or wiki_title in titles:
                relations[wiki_title][line.split('\t')[0]] = float(line.split('\t')[1])


    return relations



#load wikipedia
#load all wiki candidate titles and corresponded anchors which appear in the candidate set
#fn: '../test/bookname/bookname'
def loadAllKeywords(fn):
    titles = set()
    if os.path.isfile(fn+'_allkeywords'):
        with open(fn+'_allkeywords','r') as r:
            for line in r:
            	#line = line.decode('utf-8')
                titles.add(line.decode('utf-8').strip())


    tf, df, wordset = loadWikiAnchors(fn+'_wiki_anchor',titles = titles)

    return tf,df,wordset,titles


#load anchor file in each wikipedia page,e.g wiki_anchors_all file
def loadAnchors(bookname,path,suffix):
    	print 'load file '+path+bookname+suffix
	tf=defaultdict(lambda:defaultdict(int))
	df=defaultdict(int)
	if not os.path.isfile(path+bookname+suffix):
		return tf,df
	reader = open(path+bookname+suffix,'r')
	if not os.path.isfile(path+bookname+suffix):
		return tf,df
	counter = -1
	for line in reader:
		line=line.decode('utf-8')
		if line.startswith('========='):
		   		counter=counter+1
				tidx=line.rfind('===')
				title=line[tidx+4:].strip()


		else:
			ls=line.strip().split('\t')
			if len(ls) != 3:
				if ls[0]!='':
					df[ls[0]]=df.get(ls[0],0)
					tf[title]=tf.get(counter,dict())
					tf[title][ls[0]]=tf[title].get(ls[0],0)
				continue
			df[ls[0]]=float(ls[2])
			tf[title][ls[0]]=float(ls[1])

	return tf,df

def loadWikiDic2(fp):
    print 'load '+fp
    reader_dic = open(fp,'r')
    dic=defaultdict(list)
    i=0
    for r in reader_dic:
        i=i+1
        r=r.decode('utf-8')
        #print i
        rs=r.split('\t')
        dic[rs[0].strip()].append(rs[0].strip())
        if len(rs)>1:
            rss=rs[1].split('|')
            for rd in rss:
                dic[rs[0].strip()].append(rd.strip())
    return dic

def loadLabel(fn):
	print 'load file '+fn
	reader = open(fn,'r')
	t=defaultdict(lambda:defaultdict(list))
	sec_set=[]
	for line in reader:
		line=line.decode('utf-8')
		ls=line.split(';')
		if ls[0] == '' and ls[1] == '' or line.startswith('#') or len(ls)<4:
			continue
	        label=ls[3].strip()
                if label == '':
                    label='0'
                t[ls[0].strip()][label].append(ls[2].strip())
                if not ls[0] in sec_set:
		    sec_set.append(ls[0].strip())
	return t,sec_set



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



def saveFile(tf,df,w,s1='',s2=''):
    w.write('=========== {0} {1}'.format(s1,s2.encode('utf-8'))+'\n')
    for k1 in tf.keys():
	for k2 in tf[k1].keys():
		for k3 in tf[k1][k2].keys():

		    w.write(k1.encode('utf-8')+'\t'+k2.encode('utf-8')+'\t'+k3.encode('utf-8')+'\t'+str(tf[k1][k2][k3])+'\t'+str(df[k3])+'\n')
#save as '===== title'
#	word1 frequency
#....
#w1 specifies the output dir; dic is defaultdict(lambda:defaultdict(int))
def saveWikiOne(fn,dic):
	w1 = open(fn,'w')
	for t in dic:
		w1.write('=============== '+t.encode('utf-8')+'\n')
		for w in dic[t]:
			w1.write(w.encode('utf-8')+'\t'+str(dic[t][w])+'\n')
	w1.close()


#key as string, value as float
def loadFloat(fn):
	res=defaultdict(float)
	with open(fn,'r') as reader:
		for line in reader:
			ls=line.strip().split('\t')
			if len(ls)<2: continue
			res[ls[0]]=float(ls[1])
	return res

def loadPreLabel(fn):
	label_truth=defaultdict(lambda:defaultdict(int))
	with open(fn,'r') as r1:
            for line in r1:
                ls=line.strip().split('\t')
                if len(ls)<2 or line.startswith('#'):
                    continue

                if ls[-1].strip()!='1' :
                    label_truth[ls[0].lower()][ls[1].lower()]=0
                else:
                    label_truth[ls[0].lower()][ls[1].lower()]=int(ls[-1])
	return label_truth
def writeTop10Candidates(fn):
    rank_all,sec_all = loadRankScore(fn,10)
    w1 = open(fn+'_top10Words','w')
    words=set()
    for s1 in sec_all:
        for r in rank_all[s1]:
            words.add(r)
    for w in words:
        w1.write(w.encode('utf-8')+'\n')
if __name__ == "__main__":
	#writeMalletLdaOutput('../test/'+bookname+'/'+bookname)

        word_list=set()
        suffix = ''
        with open('../test/'+bookname+'/'+bookname+'_allkeywords','r') as r1:
            for line in r1:
                word_list.add(line.decode('utf-8').strip())
        writeWikiConceptDef('../test/'+bookname+'/'+bookname,word_list)

        writeTop10Candidates('../test/'+bookname+'/'+bookname+'_rank')
