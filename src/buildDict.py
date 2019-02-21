
# -*- coding: utf-8 -*-
import re
import sys,random,time
from wiki import *
from util import getArgMap


class AnchorExtractor:
    anchor_titles = dict()
    visited_titles = set()
    anchors = set()
    wikis = set()
    wiki2cats = dict()
    catcnt = dict()

    def __init__(self, init_titles=[], max_d=1, cache_wiki=0):
        self.init_titles = init_titles
        self.max_d = max_d
        self.cache_wiki = cache_wiki

    def dfs(self, titles, depth):
        print '{0} pages visited'.format(len(self.visited_titles))
        print 'anchor_titles: {0}'.format(len(self.anchor_titles))
        if len(titles) == 0 or depth == self.max_d:
            return
        for t in titles:
            if t in self.visited_titles:
                continue
            print '======' + t
            self.visited_titles.add(t)
            # if cache
            # wikitext = get_wikipage_content(t)
            # else
            a=random.randint(1, 10)
            if a<=3:
                print 'sleep'
                time.sleep(random.randint(1, 10))
            ret = get_page_html(t, prop='wikitext')
            if not 'parse' in ret:
            	continue
            wikitext = ret['parse']['wikitext']['*']
            new_titles = []
            matches = re.findall('\[\[(.+?)\]\]', wikitext)
            self.wikis.add(t)
            for match in matches:
                s = match.split("|")
                if len(s) > 2:  # File:...
                    continue
                wiki_title = s[0].encode('utf-8')
                if wiki_title.find(':') != -1:
                    continue
                new_titles.append(wiki_title)
                anchor = ''
                if len(s) == 2:
                    anchor = s[1].lstrip().encode('utf-8')
                anchor = s[0].encode('utf-8') if len(anchor) == 0 else anchor
                at_pair = (anchor, wiki_title)
                self.anchor_titles[
                    at_pair] = self.anchor_titles.get(at_pair, 0) + 1
                self.anchors.add(anchor)
                self.wikis.add(wiki_title)
                if len(self.wikis)>500:
                    return
                
            self.dfs(new_titles, depth + 1)

    def save(self, book_title):
        print 'saving anchor-title pairs'
        with open('../test/{0}.anchor_title'.format(book_title), 'w') as out:
            for at in self.anchor_titles:
                out.write(
                    '{0}\t{1}\t{2}\n'.format(
                        at[0], at[1], self.anchor_titles[at]))

        print 'saving anchors'
        with open('../test/{0}.anchors'.format(book_title), 'w') as out:
            for wd in self.anchors:
                out.write(wd + '\n')

        print 'saving wiki2cats'
        with open('../test/{0}.wiki2cats'.format(book_title), 'w') as out:
            for wiki in self.wiki2cats:
                out.write('{0}\t{1}\n'.format(wiki, str(self.wiki2cats[wiki])))

        print 'saving catcnt'
        with open('../test/{0}.catcnt'.format(book_title), 'w') as out:
            sorted_cnt = sorted(self.catcnt.items(), key=lambda x: x[1],
                                reverse=True)
            for (cat, cnt) in sorted_cnt:
                out.write('{0}\t{1}\n'.format(cat.encode('utf-8'), cnt))

        print 'saving wiki titles'
        with open('../test/{0}.wikis'.format(book_title), 'w') as out:
            for k, wd in enumerate(self.wikis):
                print '{0}/{1}'.format(k, len(self.wikis))
                print wd
                
               
                #print len(redir_titles)
                #line = '{0}\t{1}\n'.format(wd, '|'.join(redir_titles))
                line='{0}\n'.format(wd)
                out.write(line)

    def count_categories(self):
        print 'count_categories...'
        for k, wiki in enumerate(self.wikis):
            if k % 10 == 0:
                print '{0}/{1}'.format(k, len(self.wikis))
            a=random.randint(1, 10)
            print a
            if a<=4:
                print 'sleep'
                time.sleep(random.randint(1, 5))
            ret = get_categories(titles=wiki)
            if not 'query' in ret:
            	continue
            pid = ret['query']['pages'].keys()[0]
            categories = []
            if 'categories' in ret['query']['pages'][pid]:
                cats = ret['query']['pages'][pid]['categories']
                categories = [cat['title'] for cat in cats]
            # print categories
            self.wiki2cats[wiki] = categories
            for cat in categories:
                self.catcnt[cat] = self.catcnt.get(cat, 0) + 1
            # break


argMap = getArgMap(sys.argv[1:])
max_d = int(argMap.get('-d', 2))
s = int(argMap.get('-s', 1))
cache = int(argMap.get('-c', 0))
#init_titles=argMap.get('-t', 1)
#book_title = argMap.get('-b', 1)
#= ['History of the United States']
init_titles=['Deep learning']
book_title='Deep_learning'
if __name__ == "__main__":
    
    ae = AnchorExtractor(init_titles=init_titles, max_d=max_d)
    ae.dfs(ae.init_titles, 0)
    ae.count_categories()
    if s:
        ae.save(book_title)
