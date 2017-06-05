#!/usr/bin/python

#make sure mongod is already running locally!
#also use python3


import time
import atexit
from urllib.parse import quote
import pymongo
import sys, getopt
from pymongo import CursorType


start_time = time.time()


# only runs when user calls this python program incorrectly
def quitter():
    print('Format for calling this parser is: ')
    print('--username <username> --password <password> --db <cep_database_name>')
    sys.exit(2)


def mongoConnectionCreator(username, password, db_name, islocal = False):
    if not islocal:
        uri = "mongodb://%s:%s@%s" % (quote(username), quote(password), quote('molspace.rc.fas.harvard.edu/'))
        remote_client = pymongo.MongoClient(uri)
        remote_db = remote_client[db_name]
        return remote_db, remote_client
    else:
        local_client = pymongo.MongoClient()
        local_db = local_client[db_name]
        return local_db, local_client


# only runs at exit
def exitInfoDisplayer(remote_client, local_client):
    remote_client.close()
    print("----- The program ran in ", str(time.time() - start_time), " seconds -----")
    print("Goodbye!")
    sys.stdout.flush()


def copyCollection(remote_coll, local_coll):
    # works for small data but runs out of RAM for bigger ones
#    local_coll.insert_many(remote_coll.find({}))
    cursor = remote_coll.find({}, cursor_type = CursorType.EXHAUST)
    for document in cursor:
        local_coll.insert_one(document)

def main(argv):
    
    # Read in arguments
    username = ''
    password = ''
    db_name = ''

    try:
        opts, args = getopt.getopt(argv, "", ["db=", "username=", "password="])
    except getopt.GetoptError:
        quitter()
    for opt, arg in opts:
        if opt == "--db":
            db_name = arg
        elif opt == "--username":
            username = arg
        elif opt == "--password":
            password = arg
        else:
            quitter()
    if db_name == '':
        quitter()

    remote_db, remote_client = mongoConnectionCreator(username, password, db_name)
    local_db, local_client = mongoConnectionCreator(username, password, db_name, islocal = True)

    print("Database name:", db_name)
    collection_names = remote_db.collection_names(include_system_collections=False)
    print("Collection list:", collection_names)    
    atexit.register(exitInfoDisplayer, remote_client, local_client)
    

    for coll_name in collection_names:
        local_db.drop_collection(coll_name)
        remote_coll = remote_db[coll_name]
        local_coll = local_db[coll_name]
        copyCollection(remote_coll, local_coll)
        print("Collection ", coll_name, " inserted.")



    








if __name__ == "__main__":
#    atexit.register(dbConnectionsKiller)
    main(sys.argv[1:])


