import preprocess


class Expansion:

  def increment(self, query, docs_list):
    doc_tokens = preprocess.create_index(docs_list)
    freq_counter = preprocess.create_reverse_index(doc_tokens)
    counter = 0
    for item in freq_counter:
      if item[0] not in query:
        query.append(item[0])
        counter += 1
        if counter >= 2:
          break
    return query


# def run(all_docs):
#   # get term-doc index
#   return preprocess.create_index(all_docs)

# if __name__ == '__main__':
#   # with open('relev_doc.pickle', 'rb') as handle:
#   #    docs = pickle.load(handle)

#   with open('result.pickle', 'rb') as handle:
#     all_docs = pickle.load(handle)

#   term_doc_index = run(all_docs)
