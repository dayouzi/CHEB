import requests
#WIKI DOC: http://en.wikipedia.org/w/api.php?action=help&recursivesubmodules=1
base_url = 'http://en.wikipedia.org/w/api.php'

def total_hits(text):
	url = base_url + '?action=query&format=json&srlimit=0&list=search&srsearch='+text
	#&srwhat=text
	#&srinfo=totalhits
	return requests.get(url).json()
def search(text, srlimit=50):
    params = {'action':'query', 'format':'json', 'list':'search',
'srlimit':srlimit, 'srsearch':text}
    r = requests.get(base_url, params=params)
    return r.json()

def get_categories(titles='', pageids=''):
    url = base_url + '?action=query&format=json&prop=categories&clshow=!hidden&cllimit=50'
    if titles != '':
        url += '&titles={0}'.format(titles)
    elif pageids != '':
        url += '&pageids={0}'.format(pageids)
    return requests.get(url).json()

def get_wiki_pages(titles=''):
    url = base_url + '?action=query&format=json&redirects=true'
    if titles != '':
        url += '&titles={0}'.format(titles)
    return requests.get(url).json()

def get_page_html(page, prop='text|categories'):
    params = {'action':'parse', 'format':'json', 'prop':prop, 'page': page,'redirects':'true'}
    return requests.get(base_url, params=params).json()

def get_wikipage_content(wiki_title):
    #fname = data_folder + wiki_title.replace('/', ' ')
    #content = ''
    #if os.path.isfile(fname) and update_cache == 0:
     #   content = open(fname).read().decode('utf-8')
    #else:
    # the input titile is of format : Aaaa Bbbb
    # if not found, try aaaa bbbb
    ret = get_page_html(wiki_title, prop='wikitext')
    if 'parse' not in ret.keys():
	ret = get_page_html(wiki_title.lower(),prop='wikitext')
    if 'parse' not in ret.keys():
	return  ''
    if 'wikitext' not in ret['parse'].keys():
	return ''
    if '*' not in ret['parse']['wikitext'].keys():
	return ''
    content = ret['parse']['wikitext']['*']
   
    return content

def get_page_plainText(title,prop='extracts',value='explaintext'):
    url= base_url + '?action=query&format=json&titles='+title+'+&prop='+prop+'&'+value+'&redirects=true'
    search_query =  requests.get(url).json()
    return search_query
    
def get_redirects(titles, rdlimit=50):
    params = {'action': 'query', 'format': 'json', 'prop': 'redirects',
              'rdnamespace': 0, 'rdlimit': rdlimit, 'titles': titles}
    return requests.get(base_url, params=params).json()
    
def get_back_links(title, blfilterredir='all', bllimit=10):
    params = {'action':'query', 'format':'json', 'list':'backlinks', 'bltitle':title, 'blfilterredir':blfilterredir, 'bllimit':bllimit}
    r = requests.get(base_url , params=params)
    return r.json()
def list_category_members(cat, cmcontinue=''):
    params = {'action': 'query', 'format': 'json', 'list': 'categorymembers',
              'cmtitle': cat, 'cmnamespace': '0|14', 'cmlimit': 500,
              'cmcontinue': cmcontinue}
    return requests.get(base_url, params=params).json()


def get_all_category_members(cat):
    res = []
    cmcontinue = ''
    while 1:
        ret = list_category_members(cat, cmcontinue=cmcontinue)
        res.extend(ret['query']['categorymembers'])
        if 'query-continue' not in ret:
            break
        cmcontinue = ret['query-continue']['categorymembers']['cmcontinue']
    return res
if __name__ == '__main__':
    #print get_back_links('Kernel density')
	print search('search engine')
    
