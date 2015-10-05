import json
import preprocess

class Expansion:

  def increment(self, docs_list):
    print json.dumps(docs_list, indent=4)
    print preprocess.create_index(docs_list)


# def run(all_docs):
#   # get term-doc index
#   return preprocess.create_index(all_docs)

# if __name__ == '__main__':
#   # with open('relev_doc.pickle', 'rb') as handle:
#   #    docs = pickle.load(handle)

#   with open('result.pickle', 'rb') as handle:
#     all_docs = pickle.load(handle)

#   term_doc_index = run(all_docs)