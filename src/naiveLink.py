from book import Book
from wiki import *
import collections
from collections import defaultdict
import csv,re
#getAnchor: get the anchor texts
def getAnchor(wikitext):
        #anchors=set() 
        anchor_freq=defaultdict(int)
        matches = re.findall('\[\[(.+?)\]\]', wikitext)
        for match in matches:
            s = match.split("|")
            if len(s) > 2:  # File:...
                continue
            wiki_title = s[0]
            if wiki_title.find(":") != -1:
                continue
            anchor = ''
            if len(s) == 2:
                anchor = s[1].lstrip()
            anchor = s[0] if len(anchor) == 0 else anchor 
            anchor_freq[anchor]=anchor_freq[anchor]+1
	return anchor_freq
#get the wikipedia title in the anchor
#return a list; since difference anchor text may directs to same wikipedia: geometry and Geometry
def getReferences(wikitext):
	anchor_freq=[]
        matches = re.findall('\[\[(.+?)\]\]', wikitext)
        for match in matches:
            s = match.split("|")
            if len(s) > 2:  # File:...
                continue
            wiki_title = s[0]
            if wiki_title.find(":") != -1:
                continue
            anchor_freq.append(wiki_title.strip())
	return anchor_freq
	
def toContentExt(qstring,content=0,srlimit=10):
    contents=[]
    wiki_titles = []
   
    search_query = search(qstring,srlimit)
    if 'query' not in search_query.keys():
   	return wiki_titles,contents
    if 'search' not in search_query['query'].keys():
	return wiki_titles,contents
    search_res=search_query['query']['search']
    qrange=min(srlimit,len(search_res))
    
    for i in xrange(qrange):
	wiki_titles.append(search_res[i]['title'])
    if content:
	for wt in wiki_titles:
    		contents.append(content_ext(wt))
   
    return wiki_titles,contents
     	  
def content_ext(wiki_title):
    wiki_content = ''
    search_query = get_page_plainText(wiki_title)
    if 'query' not in search_query.keys() or 'pages' not in search_query['query'] or '-1' in search_query['query']['pages']: 
	search_query = get_page_plainText(wiki_title.lower())
    if 'query' not in search_query.keys():
   	return wiki_content
    if 'pages' not in search_query['query'].keys():
	return wiki_content
    content_res=search_query['query']['pages'] 
    for pid in content_res:
    	wiki = content_res[pid]
	if 'extract' not in wiki.keys():
		return wiki_content
	wiki_content=wiki['extract']
    return  wiki_content 
#return total hits of a word in wiki
def wordDF(text):
	df=-1
	jc  = search(text, srlimit=0)
	if 'query' in jc.keys():
		if 'searchinfo' in jc['query'].keys():
			if 'totalhits' in jc['query']['searchinfo']:
				df=jc['query']['searchinfo']['totalhits']
	return df

