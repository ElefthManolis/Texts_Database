import os
import sys
from typing import Dict
import re

import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
from gensim.test.utils import common_texts
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

sys.path.append(os.getcwd())
from db.postgresql import TextDB
from config.config import Config



"""
Some preproccesing functions
"""
def text_lowercase(text):
    return text.lower()

def remove_punctuations(text):
    return re.sub(r'[\.\?\!\,\:\;\"]', '', text)


def open_file(path) -> str:
    txt = "" # initialized as empty doc
    try:
        with open(path, 'r') as f:
            txt = f.read()
    except:
        print('The file has non ascii character and skipped from the process')
        return None
    return txt


def vectorizer(model) -> Dict:
    vector_dict = {'doc_id': [], 'embedding': []}
    docs_links = {'doc_id': [], 'doc_name': [], 'folder_name': []}
    directory = os.getcwd() + "/data/20news-bydate/"
    doc_id_counter = 0
    for folder in os.listdir(directory):
        for filename in os.listdir(directory + folder):
            doc = open_file(directory + folder + "/" + filename)
            if doc is None:
                continue
            doc = text_lowercase(doc)
            doc = remove_punctuations(doc)
            tokenized_doc = word_tokenize(doc) # first step is to make the tokenization
            vectorized_doc = model.infer_vector(tokenized_doc) # finally the tokenization
            vector_dict['doc_id'].append(doc_id_counter)
            vector_dict['embedding'].append(vectorized_doc)
            docs_links['doc_id'].append(doc_id_counter)
            docs_links['doc_name'].append(filename)
            docs_links['folder_name'].append(folder)
            doc_id_counter += 1


    df = pd.DataFrame(data = docs_links)
    df.to_csv("data.csv", index=False)

    # return all the vectors (embeddings) of the documents
    return vector_dict
    
    
def query_embedding(query):
    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(common_texts)]
    embed_model = Doc2Vec(documents, vector_size=50, window=3, min_count=1, workers=4)
    query = text_lowercase(query)
    query = remove_punctuations(query)
    tokenized_query = word_tokenize(query) # first step is to make the tokenization
    vectorized_query = embed_model.infer_vector(tokenized_query) # finally the tokenization
    return vectorized_query

def main():
    db_config = Config()
    postgre_db = TextDB(db_config)
    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(common_texts)]
    embed_model = Doc2Vec(documents, vector_size=50, window=3, min_count=1, workers=4)
    doc_vectors = vectorizer(embed_model)
    postgre_db.insert_documents(doc_vectors)

if __name__ == '__main__':
    main()
