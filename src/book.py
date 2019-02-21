import os
class Section():
    def __init__(self, title="", sid="", page=0):
        self.title = title
        self.sid = sid
        self.page = int(page)
        self.parent = None
        self.children = None
        self.chapterLen=0
        self.content=''
	self.context=''
	self.contextLen=0
    def __repr__(self):
        return self.title
    
class Book():
    def __init__(self, name , tocfile):
        self.name = name
        self.tocfile = tocfile
        self.toc = []
        self.toc_root = Section()  # tree structure
        self.length=0
        self.init_toc()
	
        
    def init_toc(self):
    	counter=0
        with open(self.tocfile) as f:
            for line in f:
            	if line == '':
            		continue
            	#print line
            	self.length=self.length+1
                line = line.strip()
                i = line.find(' ')
                sid = line[:i]
                title = line[i + 1:line.rfind(' ')]
                j = line.find('. . . .')
		k = line.find('...')
                if j >= 0:
                    title = line[i + 1:j]
		else:
			if k >= 0:
				title = line[i + 1:k]
                page = line[line.rfind(' ') :]
                sec = Section(title , sid , page)
                sec.content=open('../test/'+self.name+'/'+self.name+'_content/'+str(counter),'r').read().replace('\n',' ')
		if os.path.isfile('../test/'+self.name+'/'+self.name+'_context/'):
                	sec.context=open('../test/'+self.name+'/'+self.name+'_context/'+str(counter),'r').read().replace('\n',' ')
		else:
			sec.context=''
		sec.chapterLen=len(sec.content.split(' '))
		sec.contextLen=len(sec.context.split(' '))
		self.toc.append(sec)
                levels = sid.split('.')
                p = self.toc_root
                for i in xrange(len(levels) - 1):
                    p = p.children[int(levels[i]) - 1]
                if p.children == None:
                    p.children = []
		    
                p.children.append(sec)
                sec.parent = p
                counter=counter+1
    def load_pages(self):  # load page content into memory
        self.pages = []
        totpages = len(listdir('../test/{0}/{0}_pages'.format(self.name)))
        for i in xrange(totpages):
            sents = []
            with open('../test/{}_pages/{}'.format(self.name, i + 1)) as f:
                for line in f:
                    if len(line.strip()) > 0:
                        sents.append(line.strip().decode('utf-8'))
            self.pages.append(sents)
        # convert page 2 chapters
        self.p2c = [[] for i in xrange(len(self.pages))]
        for i, sec in enumerate(self.toc):
            st = sec.page - 1
            if i < len(self.toc) - 1:
                ed = self.toc[i + 1].page
            else:
                ed = len(self.pages)
            for j in xrange(st, ed):
                self.p2c[j].append(i)

    def depth_first_traverse(self, sec):
        if sec.children == None:
            #print sec
            return
        for c in sec.children:
            self.depth_first_traverse(c)
    def load_chapters(self):
        self.chapters = []
        for i in xrange(len(self.toc)):
            sents = []
            with open('../test/{0}/{0}_content/{1}'.format(self.name, i)) as f:
                for line in f:
                    if len(line.strip()) > 0:
                        sents.append(line.strip().decode('utf-8'))
            self.chapters.append(sents)
	
