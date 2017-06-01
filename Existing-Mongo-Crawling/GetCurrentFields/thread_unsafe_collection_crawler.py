#!/usr/bin/python

# This python file takes in the following arguments:
# - the name of the cep database you wish to crawl
# - the collection within that db you are interested in
# It then splits the task of determining all the fields in the collection into several parallelizable processes, combines the output, and presents it. 

# run this using Python2

import time
import pymongo
import sys, getopt
import multiprocessing
import atexit
import threading
from urllib import quote


start_time = time.time()
all_connections = []
fields = set()
total_records_read = 0


# only runs when user calls this python program incorrectly
def quitter():
    print 'Format for calling this parser is: '
    print 'collection_crawler.py --username <username> --password <password> --db <cep_database_name> --coll <collection_name>'
    sys.exit(2)


def mongoConnectionCreator(username, password, db_name, coll_name):
    uri = "mongodb://%s:%s@%s" % (quote(username), quote(password), quote('molspace.rc.fas.harvard.edu/'))
    client = pymongo.MongoClient(uri, maxPoolSize = 250)
    db = client[db_name]
    coll = db[coll_name]
    all_connections.append( tuple([db, coll]) )
    return (db, coll)


# only runs at exit
def dbConnectionsKiller():
    for conn in all_connections:
        conn[0].logout()
        print "A db connection was killed."
    print "Total number of records read: ", total_records_read
    print "Here are all the fields: ", fields
    print "----- The program ran in ", str(time.time() - start_time), " seconds -----"
    print "Goodbye!"
    sys.stdout.flush()


def processCursor(cursor):
    global total_records_read
    for document in cursor:
        for key in document:
           fields.add(key)
        total_records_read += 1
    cursor.close()
    print "A cursor was finished. Total number of records read so far: ", total_records_read
        


def main(argv):
    
    # Read in arguments
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

    (db, coll) = mongoConnectionCreator(username, password, db_name, coll_name)
    

    # determine how to split up the records that are read in
    total_records = coll.count()
    print "Total records that are going to be read: ", str(total_records)
    
    cpu_count = multiprocessing.cpu_count()
    print "CPU cores for parallelization: ", str(cpu_count), " (not relevant to this implementation)"

    cursors = coll.parallel_scan(200)
    print "Number of cursors provided by the server: ", len(cursors)

    threads = [
            threading.Thread(target = processCursor, args = (cursor,)) for cursor in cursors]

    for thread in threads:
        thread.start()
        thread.join()
    



if __name__ == "__main__":
    atexit.register(dbConnectionsKiller)
    main(sys.argv[1:])


