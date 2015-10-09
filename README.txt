Advanced Database Systems
Project 1 - Query Expansion

a) Team members:
Shubham Bansal(sb3766), Jie Gao(jg3526)

b) File List:
main.py - program entrance, taking care of the overall logic
queryBing.py - module which sends query requests through Bing Search API and get results
preprocess.py - module that preprocesses doc info and produce document-term matrix
expansion.py - module that applies Rocchio's relevance feedback algorithm for query expansion
README.txt - documentation

c) Instructions for running the program:
	1. NLTK configuration on CLIC machines
	Steps below comes from instructions from the course COMS4805 Natural Language Processing in Spring 2015.
		1) Add the following line of code to your ~/.bashrc file.
			export PYTHONPATH=$PYTHONPATH:/home/cs4701/python/lib/python2.7/site-packages
		2) After, don’t forget to run:
			source ~/.bashrc
		3) Login to your CLIC account.
		4) Run the following commands in your home directory.
        		ln –s /home/coms4705/nltk_data/ nltk_data
	2. Run the program
    	(Please insert instructions here)

d) e) Internal Design & Query-modification method

	   [main.py]
	1. Read user query and precision@10 (also accountKey) from command line.
	2. Iteratively do following things until precision@10 is reached.

		[queryBing.py]
		1) Submit query requests via Bing Search API and get top 50 results.

		[main.py]
		2) If less than 10 results returned, terminate the program.
		3) Show top 10 results (first 10 out of 50) to the user and get their feedback.
		4) If the precision@10 is reached or no result marked as relevant, terminate the program.

		[preprocess.py]
		5) Create inverted index, i. e. term-doc list for each of the term in top 50 results, saving tf(term frequency) at the same time, and the number of document in each list is df (document frequency).
		6) For each term, convert its term-doc list to a vector, which contains its weights correspond to each document.
		Here we us TF*IDF scheme, where TF equals to the tf in the step 3), IDF equals to log[N/(df + 1)], using log with base 2 and df the same as df in the step 3).
		In the denominator within the log term, we add one to df in that there are times the query terms would occur in all top 50 documents so that without adding 1 as adjustment the IDF would became 0 since: N/df=1 => log(N/df)=0, which erases the occurrence of such query terms.
		7) Combine all those vectors together into a term-document matrix.
		8) Transpose it to document-term matrixm normalize for each document vector with cosine normalization.
		9) Treat the query term as a document, create its 'document' vector and do the same normalization as 6).

		[expansion.py]
		10) Apply Rocchio's relevance feedback Algorithm to create a new query vector 'q_m' using only top 10 documents' vectors, and the query vector q_0 from step 7).
		Formulation:
			q_m = alpha * q_0 + beta/|num_r| * sum(d_r) - gamma/|num_nr| * sum(d_nr)
		where alpha = 1, beta = 0.75, gamma = 0.15 as suggested in the textbook.
			|num_r| - number of relevant results out of top 10
			|num_nr| - number of non-relevant results out of top 10
			sum(d_r) - sum of all vectores for relevant result documents out of top 10
			sum(d_nr) - sum of all vectores for non-relevant result documents out of top 10
		11) Pair each weight in the new query vector q_m with the term it represents, and sort the pairs according to the weights.
		12) Extract top k terms from the sorted list to form the new query, where
			k = number of terms in the last query + 2

f) Bing Search Account Key:
v2+SSNBtR6FCjUsVvr1uh0oQr99PA3WU7RxbP3g6fzg

g) References:
Christopher D. Manning, Prabhakar Raghavan and Hinrich Schütze, Introduction to Information Retrieval, Cambridge University Press. 2008. Available electronically at http://nlp.stanford.edu/IR-book/. Chapter 6 ("Scoring, Term Weighting, and the Vector Space Model") and (Chapter 9, "Relevance Feedback & Query Expansion).

(Please add and revise freely)

