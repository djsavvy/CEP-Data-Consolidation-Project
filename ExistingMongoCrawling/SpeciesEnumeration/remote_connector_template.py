#!/usr/bin/python

import time
import atexit
from urllib.parse import quote
import pymongo
import sys, getopt
from pymongo import CursorType
import pprint


start_time = time.time()


def bad_input_quitter():
    print('Format for calling this program is: ')
    print('--user <username> --pass <password> -db <cep_database_name> --coll <collection_name>')
    sys.exit(2)


def exitInfoDisplayer(client):
    client.close()
    print("----- The program ran in ", str(time.time() - start_time), " seconds -----")
    print("Goodbye!")
    sys.stdout.flush()


def mongoConnectionCreator(username, password, db_name, coll_name):
    uri = "mongodb://%s:%s@%s" % (quote(username), quote(password), quote('molspace.rc.fas.harvard.edu/'))
    remote_client = pymongo.MongoClient(uri)
    remote_db = remote_client[db_name]
    remote_coll = remote_db[coll_name]
    return remote_db, remote_coll, remote_client


def main(argv):

    username = ''
    password = ''
    db_name = ''
    coll_name = ''

    try:
        opts, args = getopt.getopt(argv, "", ["user=", "pass=", "db=", "coll="])
    except getopt.GetoptError:
        bad_input_quitter()
    for opt, arg in opts:
        if opt == "--db":
            db_name = arg
        elif opt == "--coll":
            coll_name = arg
        elif opt == "--user":
            username = arg
        elif opt == "--pass":
            password = arg
        else:
            bad_input_quitter()
    if db_name == '':
        bad_input_quitter()
        
    db, coll, client = mongoConnectionCreator(username, password, db_name, coll_name)
    print("Connected to ", db_name, ".", coll_name, ".")
    atexit.register(exitInfoDisplayer, client)
    pprint.pprint(coll.find_one())



if __name__ == "__main__":
     main(sys.argv[1:])


