import nltk
def filterStopWord(fstopword, fin, fkeep,fdrop):
	words=set()
	stopwords=set()
	wdrop=open(fdrop,'w')	
	wkeep=open(fkeep,'w')	
	with open(fstopword, 'r') as reader:
		for line in reader:
			stopwords.add(line.strip())
	with open(fin,'r') as reader:
		reader.next()
		for line in reader:
			ls=line.strip().split()
			if ls[0] in stopwords: wdrop.write(ls[0]+'\n')
			else: wkeep.write(line.strip()+'\n')
	wdrop.close()
	wkeep.close()
def filterPOSTAGGER(fin, fkeep, fdrop):
	wdrop=open(fdrop,'w')	
	wkeep=open(fkeep,'w')	
	with open(fin,'r') as reader:
		reader.next()
		for line in reader:
			ls=line.strip().split()
			pt=nltk.pos_tag([ls[0]])
			
			if pt[0][1].startswith('NN'): wkeep.write(line.strip()+'\n')
			else : wdrop.write(ls[0]+'\n')
	wdrop.close()
	wkeep.close()
if __name__ =='__main__':
	filterStopWord('stopword_patent','topic2.txt','topic2_nostopword.txt','topic2_stopword.txt')
	filterPOSTAGGER('topic2_nostopword.txt','topic2_nn.txt','topic2_nonn.txt')
