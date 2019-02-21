======= concept extraction label




=== Step 1: Run pdf2Txt2/pdf2Txt.java to convert PDFs to TXTs

Input: PDF version of textbooks, {bookname}.toc
Output: dir {bookname}_content which contains each chapter's content as a seperate file

=== Step 2: Create the domain dictionary & save wiki contents to local files (only need to run this step if you never experiement with this domain before)

python buildDict.py -d 1 -t History_of_the_United_States -b US_History

Parameter:
          max_d: -d depth that the crawler goes to, default 2
          s: -s whether save the results,default 1,save the result
          cache: -c whether to store the meta data of the web page, default 0, not save
          init_titles: -t seed page where the crawler starts 
          book_title: -b book title 

Output:
{bookname}.anchor_title: sometimes anchor texts are different from the wiki title they are directed to, this file saves anchor title pairs
{bookname}.anchors:all the anchor texts in crawled pages 
{bookname}.wiki2cats: categories that each wiki page belongs to
{bookname}.catcnt: number of pages under each wiki category (used in Filter.py which removes words not related to the subject)


=== Step 3: remove entities which are unrelated to the subject; If the category of the entity is in the black list or the number of pages under this category in the dictionary is smaller than parameter {thres}, the category is a weak category; If more than 50% of categories of an entity is a weak entity, remove this entity from the dictionary.

python filter.py –thres 15 –d science

Parameter: domain: -d each domain has a category blacklist, domain includes science and economics
thres: -thres to specifiy the threshold for the weak category

Input:
{bookname}.wikis
{bookname}.wikis2cat
{bookname}.catcnt

Output:
{bookname}.wikis_clean


=== Step 4: generate a rank list of concept candidates for each book chapter

python bookGen.py -b {bookname}
Parameter:  –b specify the bookname
            –s whether save the results to local files

Input:
{bookname}.wikis_clean
{bookname}.toc
{bookname}_content

Output:
{bookname}.rank rank list for the words (Final output for key word extraction phase)
{bookname}_dict_concepts: wiki titles and their tf/idf in each subchapter
{Bookname}_anchors_all: keywords in each wiki page


=== Step 5: feature generation
features:
0 label
1 if in title
2 content sim
3 jaccard title
4 consistency using content sim
5 redundancy using content sim
6 consistency using jaccard title
7 redundancy using jaccard title
8 preOrder
9 subOder

Step 5.1 python Feature.py -b bookname

See papers and comment section in Feature.py for more information about the features

Outputs:
{bookname}.features: features file
{bookname}.features.org: features file with entity name


Step 5.2 generate training data for each textbook
sh featureGen2.sh {bookname}
{bookname}.features_binary_id; this is the training data for each textbook


=== Step 6: predict & eval
Step 6.1 For this step, we need to mix training data from all training textbooks as the final training data
sh fg.sh (Sorry I couldn't find this script, but it should be very simple, just read data from different files and merge into one)
input: {bookname}.features_binary_id


Step 6.2 key concept extraction using rank svm
cd src/svm_rank_linux64/ (you could download the latest version)
sh prediction.sh mix

Step 6.3 python eval.py


