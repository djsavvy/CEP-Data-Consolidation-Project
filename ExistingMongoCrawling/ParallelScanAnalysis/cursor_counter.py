#!/usr/bin/python

# This python file takes in the following arguments:
# - the name of the cep database you wish to crawl
# - the collection within that db you are interested in
# - the max number of cursors you want to create


import time
import pymongo
import sys, getopt
import multiprocessing
import atexit
import threading
from operator import or_
from bson.son import SON
from pymongo.command_cursor import CommandCursor
from collections import defaultdict
from functools import reduce
from urllib.parse import quote


start_time = time.time()
fields = set()


# only runs when user calls this python program incorrectly
def quitter():
    print('Format for calling this parser is: ')
    print('collection_crawler.py --username <username> --password <password> --db <cep_database_name> --coll <collection_name> --numcursors <max_num_cursors>')
    sys.exit(2)


def mongoConnectionCreator(username, password, db_name, coll_name, do_connect = True):
    uri = "mongodb://%s:%s@%s" % (quote(username), quote(password), quote('molspace.rc.fas.harvard.edu/'))
#    print(uri)
    client = pymongo.MongoClient(uri, connect = do_connect, maxPoolSize = None)
    db = client[db_name]
    coll = db[coll_name]
    return (db, coll, client)


# only runs at exit
def exitInfoDisplayer():
    print("----- The program ran in ", str(time.time() - start_time), " seconds -----")
    print("Goodbye!")
    sys.stdout.flush()



# this function is somewhat ripped from the pymongo source code itself
# shouldn't ever need kwargs, but left it in there just to make sure this behaves exactly as expected
# each element of the output looks like this: {'firstbatch' : [], 'ns' : db_name.coll_name, 'id': <some id>}
# the sock_info.address is just ('molspace.rc.fas.harvard.edu', 27017)
def custom_parallel_scan(collection, num_cursors, **kwargs):
    cmd = SON([('parallelCollectionScan', collection._Collection__name), ('numCursors', num_cursors)])
    cmd.update(kwargs)
    with collection._socket_for_reads() as (sock_info, slave_ok):
        result = collection._command(sock_info, cmd, slave_ok, read_concern = collection.read_concern)
#    return [cursor['cursor'] for cursor in result['cursors']]
    return result['cursors']






def main(argv):
    
    # Read in arguments
    username = ''
    password = ''
    db_name = ''
    coll_name = ''
    numcursors = 0

    try:
        opts, args = getopt.getopt(argv, "", ["db=", "coll=", "username=", "password=", "numcursors="])
    except getopt.GetoptError:
        quitter()
    for opt, arg in opts:
        if opt == "--db":
            db_name = arg
        elif opt == "--coll":
            coll_name = arg
        elif opt == "--username":
            username = arg
        elif opt == "--password":
            password = arg
        elif opt == "--numcursors":
            numcursors = int(arg)
        else:
            quitter()
    if db_name == '' or coll_name == '':
        quitter()

    atexit.register(exitInfoDisplayer)
    
    (db, coll, client) = mongoConnectionCreator(username, password, db_name, coll_name)
    # determine how to split up the records that are read in
    total_records = coll.count()
    print("Total records: ", str(total_records))
    
    cpu_count = multiprocessing.cpu_count()
    print("CPU cores for parallelization: ", str(cpu_count), " (not relevant to this implementation)")

#    cursors = coll.parallel_scan(cpu_count)
#    cursors = custom_parallel_scan(coll, numcursors)
    cursors = coll.parallel_scan(numcursors)
    print("Number of cursors provided by the server: ", len(cursors))
    print(cursors[0].__iter__().count())
#    cursorlengths = [cursor.count() for cursor in cursors]
#    print(cursorlengths)
    client.close()




if __name__ == "__main__":
#    atexit.register(dbConnectionsKiller)
    main(sys.argv[1:])


