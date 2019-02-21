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
from reading_order import *
argMap = getArgMap(sys.argv[1:])
bookname = argMap.get('-b','')
'''
0 label network: 
1 titleExactMatch 1:match 0: not match network bianry: 0.836 macro_binary:0.78 
2 contentMatch numerci value 0-1 network binary: 0.571  macro_binary:0.6
3 jaccard with title network binary: 0.63  macro_binary:0.52
4 avg similarity with candidates within one subsection network binary:0.47 macro_binary
5 avg simialrity with candidates within one chapter network binary:0.37 macro_binary:0.34
6 1-avg similarity with candidates from different chapters  network binary: 0.31 macro_binary: 0.32
 
7 avg sim title jacard
8
9
10 avg sim category
11
12
dependency feature
13 r - pre appears after it/pre appears in the whole book
14 r - post appears before it/ post appears in the whole book
7 sum(ti,tj)/subsection number
'''
path = '../test/'+bookname+'/'
fn = path+bookname
reader = open(path+'label/'+bookname+'_vote_final.csv','r')
candidates = defaultdict(lambda:defaultdict(list))
chapter_titles = defaultdict(str)

features = defaultdict(list)
section_number = defaultdict()
# 1.2 : 1 2 
#chapters = defaultdict(list)

id_list=defaultdict(int)

rank_content,sec_content=loadRankScore(fn+'_rank_contentMatch') 
rank_title,sec_title=loadRankScore(fn+'_rank_titleMatch')
rank_all,sec_all = loadRankScore(fn+'_rank')
vocabulary, wiki_titles, redirs ,title2title = loadWikiDic(path,bookname)
concepts = set() #all concepts appears as candidates
dic=loadWikiDic2(fn+'.wikis_clean')
pair_sim = loadSim(fn+'_wiki_sim')
jt_sim = loadSim(fn+'_wiki_sim_titleJaccard')
#cat_sim = loadSim(fn+'.sr')
dep = loadSim(fn+'.dependency_defOnly')
res_set,sec_res=loadLabel('../test/'+bookname+'/label/'+bookname+'_vote_final.csv')
titleDepth,delimiter=delimiterSettings(bookname)


def init():
    i=0
    ch=0
    sec=0
    subsec=0
    global delimiter
    for line in reader:
        line=line.decode('utf-8')
        ls = line.split(';')
        if len(ls)< 4 or (ls[0]=='' and ls[1]=='') or line.startswith('#'):
            continue
        if ls[3].strip()=='':
            ls[3]='0'
        
        if '-' in ls[0]:
            delimiter = '-'
        if len(ls[0].split(delimiter))>2:
            titleDepth=3
        #candidates : k1:sec number;k2: label(0,1,2); value: wiki title
        
        if ls[3].strip()=='2':
            ts='1'
        else:
            ts=ls[3].strip()
        candidates[ls[0].strip()][ts].append(ls[2].strip())
        chapter_titles[ls[0].strip()] = ls[1].strip()
        concepts.add(ls[2].strip())
        id_list[ls[0]+'\t'+ls[2]] = i
        i=i+1
    #print candidates


def f0(features):
    #print candidates
    for c in candidates.keys():
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
    		features[c+'\t'+t].append(l)
    return features
#titleMatch
def f1(features):
    for c in candidates.keys():
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
    		#1
    		if t in rank_title[c]:
    		    features[c+'\t'+t].append(1)
    		else:
    		    features[c+'\t'+t].append(0)
    return features
#content sim
def f2(features):
    for c in candidates.keys():
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
    		#2
                features[c+'\t'+t].append(rank_content[c][t])
    return features
#jaccard similarity title
def f3(features):
    for c in candidates.keys():
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
                max_titleSim = -1
                jt=-1
                for r in dic[t]:
                    jt = jaccard(r,chapter_titles[c])
                    if jt > max_titleSim:
                        max_titleSim = jt
                features[c+'\t'+t].append(max_titleSim)

    
'''
def f7(features,jt_sim):
    sameSection(features,jt_sim)
def f8(features,jt_sim):
    sameChapter(features,jt_sim)
def f9(features,jt_sim):
    diffChapter(features,jt_sim)
def f10(features,cat_sim):
    sameSection(features,cat_sim)
def f11(features,cat_sim):
    sameChapter(features,cat_sim)
def f12(features,cat_sim):
    diffChapter(features,cat_sim)
'''
#sim is defaultdict(lambda:defaultdict)
#maxNum: 
#consistency using 
def sameSection(features,sim,maxNum=50):
    for c in candidates.keys():
        if not c in sec_res:
            continue
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
                #4
                s=0; n=0
                for ll in candidates[c].keys():
                    for i,tt in enumerate(candidates[c][ll]):
                        if tt == t:
                            continue
                        if i>maxNum:
                            break
                        i=i+1
                        s=s+max(float(sim[tt][t]),float(sim[t][tt]))
                        n=n+1
                if n ==0:
                    features[c+'\t'+t].append(0)
                else:
                    features[c+'\t'+t].append(s/n)

#chapter 1 and chapter 1 when titleDepth =2
#chapter 1.2 and 1.3 when titleDepth = 3 
def sameChapter(features,sim,maxNum=50):
    global delimiter
    global titleDepth
    for c in candidates.keys():
        if not c in sec_res:
            continue
        cs=c.split(delimiter)
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
                #5
                s=0; n=0
                for cc in candidates.keys():
                    ccs=cc.split(delimiter)
                    if  cs[0] == ccs[0] and not c == cc:
                             if titleDepth == 3 and  cs[1] != ccs[1]:
                                 continue
                             else:
                                 for ll in candidates[cc].keys():
                                     for i,tt in enumerate(candidates[cc][ll]):
                                         if i>maxNum:
                                             break
                                         i=i+1
                                         s=s+max(float(sim[tt][t]),float(sim[t][tt]))
                                         n=n+1
                if n ==0:
                    features[c+'\t'+t].append(0)
                else:
                    features[c+'\t'+t].append(s/n)
def diffChapter(features,sim,maxNum=50):
    global titleDepth
    global delimiter 
    for c in candidates.keys():
        if not c in sec_res:
            continue
        cs=c.split(delimiter)
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
                #6
                s=0; n=0
                for cc in candidates.keys():
                    ccs=cc.split(delimiter)
                    if len(ccs)<1 or len(cs)<1:
                        continue
                    
                    if ccs[0] != cs[0] or (titleDepth == 3 and len(ccs)>1 and len(cs)>1 and ccs[1] != cs[1] ):
                        for ll in candidates[cc].keys():
                            for i,tt in enumerate(candidates[cc][ll]):
                                if i>maxNum:
                                    break
                                i=i+1
                                s=s+max(float(sim[tt][t]),float(sim[t][tt]))
                                n=n+1
                if n ==0:
                    features[c+'\t'+t].append(1)
                else:
                    features[c+'\t'+t].append(1-s/n)


    
#order = 1 : pre exits in after
#order = -1: post exist in previous
def preDep(order=1,maxNum=50):
    for c in candidates.keys():
        if not c in sec_res:
            continue
    	for l in candidates[c].keys():
    	    for t in candidates[c][l]:
                n,penalty=0,0
                for cc in candidates.keys():
                    if cc == c:
                        continue
                    #pre: 1 * chapter 1 look at the chapters after it
                    #post: -1 * chapter -1
                    if order*chapterCmp(c,cc) == 1:
                         #print c+' '+cc+' '+str(chapterCmp(c,cc))+' '+str(order)
                         for ll in candidates[cc].keys():
                             for i,tt in enumerate(candidates[cc][ll]):
                                 if i> maxNum:
                                     break
                                 i=i+1
                                 #order 1: if pre(dep[t][tt]=-1 or dep[tt][t]=1) exists
                                 #tt is t's prerequisite while chapter for t is before tt; PENALIZE
                                 if dep[t][tt]*order == -1 or dep[tt][t]*order == 1:
                                     #print c+' '+t.encode('utf-8')+' '+cc+' '+tt.encode('utf-8')
                                     penalty = penalty+1
                                 n = n+1
                   
                if n == 0:
                    features[c+'\t'+t].append(1)
                else:
                    features[c+'\t'+t].append(1-penalty/n)
def feature():
    #features=defaultdict(list)
    f0(features)#label
    f1(features) #exact match
    f2(features)#content sim
    f3(features) #title jaccard
    #sameSection(features,pair_sim)
    #sameChapter(features,pair_sim)
    #diffChapter(features,pair_sim)
    sameSection(features,pair_sim,5) #consistency wiki sim 
    #sameChapter(features,pair_sim,10) #in v1 not in v2
    diffChapter(features,pair_sim,5)#redundancy wiki sim
    
    sameSection(features,jt_sim,5)#consistency jaccard sim
    #sameChapter(features,jt_sim,10) # in v1 not in v2
    diffChapter(features,jt_sim,5)#redundancy jaccard sim

    #sameSection(features,cat_sim,1)
    #sameChapter(features,cat_sim,10) # in v1 not in v2
    #diffChapter(features,cat_sim,5)

    preDep(1,5) # in v1 not in v2
    preDep(-1,5)

    

'''
save four files
.qid_sec   sec number; sec id(query id)
.features feature file
.features_org feature file with wiki concept title
.features_binary_id     binary label; sec id; features
'''
def savebinarySecFile():
    w = open(fn+'.features_org','w')
    wf = open(fn+'.features','w')
    wbi = open(fn+'.features_binary_id','w')
    wqid=open(fn+'.qid_secTitle','w')
    ltemp=list(chapter_titles.keys())
    qid=defaultdict(int)
    for i,c in enumerate(candidates.keys()):
        for l in candidates[c].keys():
            for t in candidates[c][l]:
                fl = '\t'.join(str(k) for k in features[c+'\t'+t])
                wf.write(fl+'\n')
                w.write(c.encode('utf-8')+'\t'+t.encode('utf-8')+'\t'+str(ltemp.index(c))+'\t'+fl+'\n')
                fl_temp= '\t'.join(str(k) for i,k in enumerate(features[c+'\t'+t]) if i!=0)
                wbi.write(str(features[c+'\t'+t][0])+'\t'+str(ltemp.index(c)+1)+'\t'+fl_temp+'\n')
        qid[c]=i+1
    for c in qid:
        wqid.write(c+'\t'+str(qid[c])+'\n')

#generate binary features
if __name__ == "__main__":
    init()
    feature()
    savebinarySecFile()
