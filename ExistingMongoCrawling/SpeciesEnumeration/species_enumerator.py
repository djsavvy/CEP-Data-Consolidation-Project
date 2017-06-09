#!/usr/bin/python

import time
import atexit
from urllib.parse import quote
import pymongo
import sys, getopt
from pymongo import CursorType
import pprint
import uuid
import json




def extract_nested_key_list(document):
    result_list = []
    for key, value in document.items():
        if isinstance(value, dict):
            result_list.append( {key : extract_nested_key_list(value)} )
        else:
            result_list.append(key)
    return tuple(sorted(result_list,
        key = lambda x : list(x.keys())[0] if isinstance(x, dict) else x
        ))


# assumes that all keys are strings (including within nested dicts)
def generate_hash(nested_key_list):
    return hash(json.dumps(nested_key_list, sort_keys = True))


def process_document(document):
    nested_key_list = extract_nested_key_list(document)
    doc_hash = generate_hash(nested_key_list)
    global distinct_species
    if doc_hash not in distinct_species.keys():
        distinct_species[doc_hash] = nested_key_list
    return


def process_multiple_documents(cursor):
    for document in cursor:
        process_document(document)
    return


def extract_sample_cursors(collection):
    cursors = []
    doc_count = collection.count({})
    for i in range(4):
        skip_amount = i * (doc_count//8)
        cursors.append( collection.find({}, skip = skip_amount, limit = 100, no_cursor_timeout = True).sort("_id", 1) )
        cursors.append( collection.find({}, skip = skip_amount, limit = 100, no_cursor_timeout = True).sort("_id", -1) )
    return cursors


def process_collection(collection):
    for cursor in extract_sample_cursors(collection):
        process_multiple_documents(cursor)
    return


# more efficient since we only need to traverse the collection once, and finding by _id is pretty quick because of the index (at least I think so)
def new_process_collection(collection):
    doc_count = collection.count({})
    skip_amount = 700
    cursor = collection.find({}, limit = 100).sort("_id", 1) 
    currentObjectId = None

#    cur_cursor_count = 1

    while cursor.count() > 100 + skip_amount + 2:
        for document in cursor:
            process_document(document)
            currentObjectId = document.get('_id')

        cursor = collection.find({"_id" : {"$gt" : currentObjectId}}, skip = skip_amount, limit = 100).sort("_id", 1)
#        cur_cursor_count += 1
#        print('got cursor', str(cur_cursor_count))
#        print("Got a cursor!")
    return 



def bad_input_quitter():
    print('Format for calling this program is: ')
    print('-db <cep_database_name>')
    sys.exit(2)


def exitInfoDisplayer(client):
    client.close()
    global start_time
    print("----- The program ran in ", str(time.time() - start_time), " seconds -----")
    print("Goodbye!")
    sys.stdout.flush()


def mongoConnectionCreator():
    client = pymongo.MongoClient('localhost', 27017)
    return client





start_time = time.time()
distinct_species = {}


client = mongoConnectionCreator()
atexit.register(exitInfoDisplayer, client)

print("List of databases found: ", client.database_names())

for db_name in client.database_names():
    if db_name == 'admin' or db_name == 'local':
        continue
    
    database = client[db_name]
    print("Starting on database ", db_name)
    for coll_name in database.collection_names(include_system_collections = False):
        collection = database[coll_name]
        distinct_species = {} 
        print("Starting on ", db_name, coll_name)
        process_collection(collection)
#        new_process_collection(collection)
        print("Found ", len(distinct_species.keys()), " distinct species.")
        print("They are: ")
        pprint.pprint(distinct_species)

        outputFile = open("output/" + db_name + "." + coll_name + ".species_enumeration.txt", 'w')
        print("Found ", len(distinct_species.keys()), " distinct species.", file = outputFile)
        pprint.pprint(distinct_species, outputFile)
        outputFile.flush()
        outputFile.close()

        count = 0
        for key, value in distinct_species.items():
            outfile = open("output/" + db_name + "." + coll_name + ".species" + str(count) + ".txt", 'w')
            print("Hash: ", str(key), file = outfile)
            pprint.pprint(value, outfile)
            count += 1

        
        print("Ouput files written.")
        print("This collection finished ", str(time.time() - start_time), " seconds after the main program was started.")


