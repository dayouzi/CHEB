#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from book import Book
from nltk.stem.porter import PorterStemmer
from nltk import pos_tag
from util import getArgMap
import sys,re,copy,gc
from copy import deepcopy
import collections
from collections import *
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from loadFile import *
from keyword_ext_dic import *
from keyword_tool import *
from getWikis import *
import gensim
ps = PorterStemmer()
argMap = getArgMap(sys.argv[1:])
bookname = argMap.get('-b','')
doc_suffix=argMap.get('-s','')
save = int(argMap.get('-s',1))
path = '../test/'+bookname+'/'
fn=path+bookname
if __name__ == "__main__":
    gc.enable()
    b = Book(bookname, path+bookname+'.toc')
    print path+bookname+'.toc'
    print b.toc
    stopword=loadStopWord()
    sents=[u'.',u',',u':',u';',u'!',u'?',u'(',u')',u'\'',u'-',u']',u'[',u'-']
    new_voc, wiki_titles, redirs ,title2title = loadWikiDicStem(path,bookname)

    #stem2dic,new_voc,dic2stem = stemDic(vocabulary,stopword,sents) #return the stemming form of the dictionary
    dic_init=gensim.corpora.Dictionary([list(new_voc)])

    id2token_init=defaultdict(str)

    tf_book_dict=defaultdict(lambda:defaultdict(int))
    df_book_dict=defaultdict(int)
    tfidf_book=defaultdict(lambda:defaultdict(float))
    for w in dic_init.token2id.keys():
        id2token_init[dic_init.token2id[w]]=w
    texts=[]

    doc_wiki=defaultdict(set)

    #match key concepts in the text using dictionary
    wordset=set()
    w_bd = open(fn+'_dict_concepts','w')

    for i,sec in enumerate(b.toc):
        book_title = sec.title.lower().replace('?ˉ', '\'')
        print book_title
        if 'summary' in book_title.lower() or 'exercises' in book_title.lower() or 'bibliographic notes' in book_title.lower():
            continue
        s=sec.content.lower().replace('\r',' ').replace('\n',' ').replace('\r\n',' ').decode('utf-8')
        s_stem=stemTexts(s,sents)
        print '============'+sec.sid+' '+book_title
        text=[]
        for w in GenNgram(s_stem.split()):

            text.append(w)
        texts.append(text)
    #print texts
    corpus = [dic_init.doc2bow(text) for text in texts]
    tfidf_book_init=gensim.models.tfidfmodel.TfidfModel(corpus)

    j=0
    for i,sec in enumerate(b.toc):
        book_title = sec.title.lower().replace('?ˉ', '\'')
        if 'summary' in book_title.lower() or 'exercises' in book_title.lower() or 'bibliographic notes' in book_title.lower():
            continue
        for p in corpus[j]:
            df_book_dict[id2token_init[p[0]]]=df_book_dict[id2token_init[p[0]]]+1
            tf_book_dict[i][id2token_init[p[0]]]=p[1]
            wordset.add(id2token_init[p[0]])
        for p in tfidf_book_init[corpus[j]]:
            tfidf_book[i][p[0]]=p[1]
        j=j+1



    print '~~~~~~~~~~~~~~~~BOOK DICT CALCULATION DONE'
    if save==1:
        print 'SAVE TO FILE....'
        for i,sec in enumerate(b.toc):
            book_title = sec.title.lower().replace('?ˉ', '\'')
            print sec.sid
            w_bd.write('=========== {0} {1}'.format(sec.sid,book_title.encode('utf-8'))+'\n')
            if 'summary' in book_title.lower() or 'exercises' in book_title.lower() or 'bibliographic notes' in book_title.lower() or 'conclusion' in book_title.lower():
                continue
            for w in tf_book_dict[i].keys():
                w_bd.write(w.encode('utf-8')+'\t'+str(tf_book_dict[i][w])+'\t'+str(df_book_dict[w])+'\n')

    gc.collect()

    #load/calculate tf and idf of wiki candidates and extend the dictionary
    anchor_freq,wiki_contents_sec,wikis = getWikis(fn,wordset,redirs,title2title)

    for i,sec in enumerate(b.toc):
        book_title = sec.title.lower().replace('¡¯', '\'')
	if 'summary' in book_title.lower() or 'exercises' in book_title.lower() or 'bibliographic notes' in book_title.lower():
	    continue
	for w in tf_book_dict[i].keys():
	    if tf_book_dict[i][w] == 0:
	    	continue
	    for ww in title2title[w]:
                if ww in redirs:
		    for t in redirs[ww]:
			if not t in anchor_freq.keys():
                            continue
                        doc_wiki[i].add(t)
		else:

                    doc_wiki[i].add(ww)



    tf_wiki=defaultdict(lambda:defaultdict(int))
    df_wiki=defaultdict(int)
    wiki_texts=[]
    w_wiki=open(fn+'_wiki_anchors_all','w')
    for wt in list(wikis):
        text=[]
        #s_stem=' '.join(x if len(stemming(x))<4 else stemming(x) for x in wiki_contents_sec[wt]['WHOLEPAGE'].split())
        s_stem=stemTexts(wiki_contents_sec[wt]['WHOLEPAGE'],sents)

        for w in GenNgram(s_stem.split()):
            text.append(w)
        wiki_texts.append(text)
    corpus_wiki = [dic_init.doc2bow(text) for text in wiki_texts]
    tfidf_wiki_init=gensim.models.tfidfmodel.TfidfModel(corpus_wiki)
    tfidf_wiki=defaultdict(lambda:defaultdict(float))
    for i,wt in enumerate(list(wikis)):
        for p in corpus_wiki[i]:
            df_wiki[id2token_init[p[0]]]=df_wiki[id2token_init[p[0]]]+1
            tf_wiki[wt][id2token_init[p[0]]]=p[1]

        for p in tfidf_wiki_init[corpus_wiki[i]]:
            tfidf_wiki[wt][p[0]]=p[1]

    print '~~~~~~~~~~~~~~~~WIKI MATCH CALCULATION DONE'
    if save==1:
        print 'SAVE TO FILE....'
        for i,wt in enumerate(wikis):
            w_wiki.write('==================== '+wt.encode('utf-8')+'\n')
            for p in tf_wiki[wt]:
                w_wiki.write(p.encode('utf-8')+'\t'+str(tf_wiki[wt][p])+'\t'+str(df_wiki[p])+'\n')



    #calculate sim between text and wiki
    cs=defaultdict(lambda:defaultdict(float))
    rw=open(path+bookname+doc_suffix+'_rank','w')
    rw_title=open(path+bookname+doc_suffix+'_rank_titleMatch','w')
    rw_content=open(path+bookname+doc_suffix+'_rank_contentMatch','w')
    exact=defaultdict(set)
    #print doc_wiki

    for i,sec in enumerate(b.toc):

        book_title = sec.title.lower().replace('?ˉ', '\'')
        print '============'+sec.sid+' '+book_title
	rw.write('===========\t{0}\t{1}'.format(sec.sid, book_title)+'\n')
	rw_title.write('===========\t{0}\t{1}'.format(sec.sid, book_title)+'\n')
	rw_content.write('===========\t{0}\t{1}'.format(sec.sid, book_title)+'\n')
	if 'summary' in book_title.lower().strip()  or 'exercises' in book_title.lower().strip() or 'bibliographic notes' in book_title.lower().strip() or 'conclusion' in book_title.lower():
	    continue

        for t in doc_wiki[i]:
	    if sameTitle(t,book_title) == 1 and len(t.split())>0:
		exact[i].add(t)

	for t in doc_wiki[i]:
	    cs[i][t] = cosine_distance_dic(tfidf_wiki[t],tfidf_book[i])
	sorted_link = sorted(cs[i].items(), key=lambda x: x[1], reverse=True)
	rank=0;rank_title=0;rank_content=0
	if len(exact[i])!=0:
            for t in exact[i]:
                if str(cs[i][t])=='0':
                    continue
		rw.write(t.encode('utf-8')+'\t'+str(cs[i][t])+'\t'+str(rank)+'\n')
		rw_title.write(t.encode('utf-8')+'\t'+str(cs[i][t])+'\t'+str(rank_title)+'\n')
		rank_title=rank_title+1;rank=rank+1

	for t in sorted_link:
            if str(t[1])=='0':
                continue
	    rw_content.write(t[0].encode('utf-8')+'\t'+str(t[1])+'\t'+str(rank_content)+'\n')
	    rank_content=rank_content+1
	    if t[0] in exact[i]:
		continue
            if rank < 30:
                rw.write(t[0].encode('utf-8')+'\t'+str(t[1])+'\t'+str(rank)+'\n')
                rank=rank+1
    print '================ CALCULATION DONE'
