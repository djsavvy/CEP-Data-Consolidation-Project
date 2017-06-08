#!/usr/bin/python

# This python file takes in the following arguments:
# - the name of the cep database you wish to crawl
# - the collection within that db you are interested in
# It then splits the task of determining all the fields in the collection into several parallelizable processes, combines the output, and presents it. 

# This is a true multiprocessing implementation of the crawler based off of collection_crawler.py

# Note that it is best to run this using python3, as it is much more efficient that way

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
    print('collection_crawler.py --username <username> --password <password> --db <cep_database_name> --coll <collection_name>')
    sys.exit(2)


def mongoConnectionCreator(username, password, db_name, coll_name, do_connect = True):
    uri = "mongodb://%s:%s@%s" % (quote(username), quote(password), quote('molspace.rc.fas.harvard.edu/'))
#    print(uri)
    client = pymongo.MongoClient(uri, connect = do_connect, maxPoolSize = None)
    db = client[db_name]
    coll = db[coll_name]
    return (db, coll, client)


# only runs at exit
def exitInfoDisplayer(total_records_read):
    print( "Total number of records read: ", str(total_records_read))
    print("Here are all the fields: ", fields)
    print("----- The program ran in ", str(time.time() - start_time), " seconds -----")
    print("Goodbye!")
    sys.stdout.flush()


def process_field_accumulator(process_fields_list):
    global fields
    fields = reduce(or_, process_fields_list)


def processCursor(process_fields_list, total_records_read, cursor, pdb, pcoll, pclient, lock):
    process_fields = set() 
    process_records_read = 0
    for document in cursor:
        for key in document:
           process_fields.add(key)
#           with lock:
#               total_records_read.value += 1
        process_records_read += 1
    cursor.close()
    pclient.close()
    with lock:
        process_fields_list.append( process_fields )
        total_records_read.value += process_records_read
    print("A cursor was finished. Total number of records read so far: ", total_records_read)
        


# this function is somewhat ripped from the pymongo source code itself
# shouldn't ever need kwargs, but left it in there just to make sure this behaves exactly as expected
# each element of the output looks like this: {'firstbatch' : [], 'ns' : db_name.coll_name, 'id': <some id>}
# the sock_info.address is just ('molspace.rc.fas.harvard.edu', 27017)
def custom_parallel_scan(collection, num_cursors, **kwargs):
    cmd = SON([('parallelCollectionScan', collection._Collection__name), ('numCursors', num_cursors)])
    cmd.update(kwargs)

    with collection._socket_for_reads() as (sock_info, slave_ok):
        result = collection._command(sock_info, cmd, slave_ok, read_concern = collection.read_concern)
#    return [CommandCursor(collection, cursor['cursor'], sock_info.address) for cursor in result['cursors']
    return [cursor['cursor'] for cursor in result['cursors']]


    
def ccursorToCursor(ccursor, username, password, db_name, coll_name):
    (pdb, pcoll, pclient) = mongoConnectionCreator(username, password, db_name, coll_name)
    address = ('molspace.rc.fas.harvard.edu', 27017)
#    return (CommandCursor(pclient[pdb][pcoll], ccursor, address), pdb, pcoll, pclient)
    return (CommandCursor(pcoll, ccursor, address), pdb, pcoll, pclient)


def fullProcessCcursor(process_fields_list, total_records_read, ccursor, username, password, db_name, coll_name, lock):
    cursor, pdb, pcoll, pclient = ccursorToCursor(ccursor, username, password, db_name, coll_name)
    processCursor(process_fields_list, total_records_read, cursor, pdb, pcoll, pclient, lock)
    pclient.close()


def main(argv):
    
    # Read in arguments
    username = ''
    password = ''
    db_name = ''
    coll_name = ''

    try:
        opts, args = getopt.getopt(argv, "", ["db=", "coll=", "username=", "password="])
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
        else:
            quitter()
    if db_name == '' or coll_name == '':
        quitter()

    manager = multiprocessing.Manager()
    total_records_read = manager.Value('i', 0)
    records_lock = multiprocessing.Lock()
    process_fields_list = manager.list()

    # now we can do the atexit registration, since all_connections is defined
    atexit.register(exitInfoDisplayer, total_records_read)

    
    (db, coll, client) = mongoConnectionCreator(username, password, db_name, coll_name)
    # determine how to split up the records that are read in
    total_records = coll.count()
    print("Total records that are going to be read: ", str(total_records))
    
    cpu_count = multiprocessing.cpu_count()
    print("CPU cores for parallelization: ", str(cpu_count), " (not relevant to this implementation)")

    cursors = coll.parallel_scan(cpu_count)
#    cursors = coll.parallel_scan(100)
    print("Number of cursors provided by the server: ", len(cursors))
    client.close()



    jobs = []
    custom_cursors = custom_parallel_scan(coll, cpu_count)
    for ccursor in custom_cursors:
        p = multiprocessing.Process(target = fullProcessCcursor, args = (process_fields_list, total_records_read, ccursor, username, password, db_name, coll_name, records_lock))
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()


    process_field_accumulator(process_fields_list)





if __name__ == "__main__":
#    atexit.register(dbConnectionsKiller)
    main(sys.argv[1:])


