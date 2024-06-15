import os
import pickle
import psycopg2
from scipy.spatial import distance
import numpy as np
import pandas as pd
from typing import Dict
from config.config import Config



class TextDB:
    def __init__(self, config: Config):
        self.database = config.db
        self.user = config.user
        self.password = config.password
        self.host = config.host
        self.port = config.port


    def insert_documents(self, embeddings: Dict):
        cols = embeddings['doc_id']
        records = [embeddings['embedding'][x] for x in cols]
        try:
            connection = self.connect()
            print("PostgreSQL connection is started")
            cursor = connection.cursor()
            query = """
                    INSERT INTO doc_vectors(doc_id, embeddings) 
                    VALUES (%s, %s)
                    """
            for idx, record in enumerate(records):
                cursor.execute(query, (cols[idx], pickle.dumps(record)))
            connection.commit()
        except (Exception, psycopg2.Error) as error:
            print("Failed to insert records", error)
        finally:
            # closing database connection.
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")



    def connect(self):
        connection = psycopg2.connect(user=self.user,
                                password=self.password,
                                host=self.host,
                                port=self.port,
                                database=self.database)
        connection.autocommit = True
        return connection


    def fetch_documents(self, prompt, K, distance_measure):
        try:
            connection = self.connect()
            print("PostgreSQL connection is started") 
            cursor = connection.cursor()
            query = """
                    SELECT * 
                    FROM doc_vectors; 
                    """
            cursor.execute(query)
            documents = cursor.fetchall()
            cursor.close()
            connection.close()
            filtered_documents = self.filter_documents(documents, prompt, K, distance_measure)
            return filtered_documents
        except (Exception, psycopg2.Error) as error:
            print("Failed accur on the data fetching or filtering", error)
            return None
        
    


    def filter_documents(self, documents, query, K, distance_measure):
        distances = []
        record_ids = []
        for record in documents:
            record_id = record[0]
            deserialised_record = pickle.loads(record[1])
            dist = distance.cdist(deserialised_record.reshape(1, 50), query.reshape(1, 50), distance_measure)
            distances.append(float(dist[0][0]))
            record_ids.append(record_id)
        
        #convert the lists into numpy arrays
        distances = np.array(distances)
        record_ids = np.array(record_ids)

        ascending_order_indices = np.argsort(distances) # the np.argsort sort the in ascending order
        descending_order_indices = ascending_order_indices[::-1] # in this line I revert the order to descending

        distances = list(distances[descending_order_indices])
        record_ids = list(record_ids[descending_order_indices])
        
        filtered_record_ids = record_ids[:K]
        documets = pd.read_csv(os.getcwd() + "/data.csv")
        filtered_documents = documets.loc[documets['doc_id'].isin(filtered_record_ids)]
        docs = self.fetch_documnets_text_from_disk(filtered_documents)
        return docs
    


    def fetch_documnets_text_from_disk(self, filtered_documents):
        docs = []
        for index, row in filtered_documents.iterrows():
            with open(os.getcwd() + "/data/20news-bydate/" + row['folder_name'] + "/" + str(row['doc_name'])) as f:
                content = f.read()
                docs.append(content)
        return docs
    