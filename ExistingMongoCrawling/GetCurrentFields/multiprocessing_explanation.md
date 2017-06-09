# An Explanation of my Struggles using PyMongo with Multiprocessing

As part of my work for the Harvard Clean Energy Project, I wrote a script called [`mp_collection_crawler.py`](/ExistingMongoCrawling/GetCurrentFields/mp_collection_crawler.py). This program, given the name of a database and a collection within that database, scans every single document in the collection and returns a set of all the top-level fields found anywhere in the collection. 

Linearly scanning the data is quite slow, with some of the collections in the Clean Energy Project databases reaching from 75 to 140 million records a piece. Therefore, I decided to use Python's [`multiprocessing`](https://docs.python.org/3.6/library/multiprocessing.html) library to get some speedup (and at least prevent my local machine from being the bottleneck in the operation -- this was ran before I copied all of the CEP data to my machine, when it was still hosted only on the `molspace` server). 

By far the biggest challenge in this was figuring out how to use `multiprocessing` efficiently and safely. First, I made a [threaded implementation](/ExistingMongoCrawling/GetCurrentFields/thread_unsafe_collection_crawler.py) that, while yielding the correct result, did not actually run any processes in parallel due to the nature of threads in Python. While `multiprocessing` runs completely different processes in parallel, `threading` runs separate threads serially. This makes the code a lot easier to write, but fails to provide any speedup on a multicore machine. 

When I switched to `multiprocessing` from `threading`, the first challenge I faced was making sure that all of my data was being written safely. Being new to `multiprocessing` (both the Python library and the concept in general), I learned how to safely update a shared counter among different processes using `manager.Value()`. I also learned how to send data from my helper processes to the main one using `manager.list()`. Although I ran into some logical issues initially trying to use `multiprocessing.Queue`, none of them were particularly challenging or meaningful for someone familiar with the subject. By far the most difficult -- and head-banging-worthy -- aspect of this code was getting `multiprocessing` and PyMongo to play nice with each other.


### The General Approach

The problem we are trying to solve can essentially be reduced to iterating through a collection in MongoDB efficiently using Python's `multiprocessing` library. 

However, before we write any Python code, we need to figure out the best way to do this in pure Mongo. PyMongo is just a driver between a MongoDB server running a `mongod` instance and the Python code that actually processes the data read from the server. 

Fortunately, Mongo's official documentation points us to a command called [`parallelCollectionScan`](https://docs.mongodb.com/manual/reference/command/parallelCollectionScan/). It was introduced in version 2.6, which thankfully is the version the CEP server is running (the current version is 3.4). `parallelCollectionScan` outputs a list of cursors that you can iterate over in parallel, and together they are guaranteed to return the entire collection. Handy, no?

Unfortunately, we run into a few problems. Firstly, the records of the collection are not guaranteed to be evenly distributed among the cursors (essentially iterators on a subset of a database) returned by `parallelCollectionScan`. For instance, on one collection with 77 million records, the first cursor of 200 returned by `parallelCollectionScan` had exactly 2 records. The second had 16. 

Fortunately, this uneven distribution of cursors does not pose too much of a problem. In fact, it allows us to start 200 different processes at once -- one for each cursor -- and have some of them finish very quickly. This has the advantage of returning output immediately after the program is started, giving some basic sanity checks. Furthermore, as the number of running processes drops sharply, less CPU time is spent switching between processes and the true benefits of multiprocessing can be reaped. In the final version of my script, I used `multiprocessing.cpu_count()` to determine the number of virtual CPUs on the system and only created that many processes, thereby eliminating most of the process-switching overhead. 

Howevever, there is a much bigger problem that is not as easy to fix. 

### Hitting a Wall

Mongo's `parallelCollectionScan` returns a set of cursors we can safely iterate over in parallel. As mentioned above, threads in Python do not provide speedup through parallelism, so we must use the `multiprocessing` library. The problem with `multiprocessing` is that, while it is thread-safe, it is not fork safe. According to the [PyMongo FAQ](http://api.mongodb.com/python/current/faq.html#using-pymongo-with-multiprocessing), `MongoClient` instances cannot be copied from a parent process to a child process. 

What this means is that I can't just pass a cursor from `parallel_scan` (PyMongo's method that calls Mongo's `parallelCollectionScan`) to another process and iterate over it, since that process would copy the `MongoClient` object used to create the cursor in the first place. 

I clearly wasn't the only one to run into this problem. [This article](https://derickrethans.nl/parallelcollectionscan.html) by Derick Rethams demonstrates use of the `parallelCollectionScan` method of the [PHP-Mongo driver](https://pecl.php.net/package/mongodb) but notes that:
> the cursors are still iterated over sequentially, and not in parallel. 

[This short thread](http://grokbase.com/t/gg/mongodb-user/14cs38006q/parallel-collection-scan-for-query-results) suggests forgoing `parallelCollectionScan` altogether and instead performing multiple queries based on index values. However, without knowing the exact distribution of index values in advance, this method is impractical. 

An official PyMongo maintainer said [here](https://jira.mongodb.org/browse/PYTHON-1078) that such a solution would never be possible to implement in PyMongo (or even Python in general). 

There were some solutions suggested using [`Map_reduce`](https://stackoverflow.com/questions/15092884/how-can-i-return-an-array-of-mongodb-objects-in-pymongo-without-a-cursor-can), but these have two problems: 1. they do not support arbitrary processing of documents nearly as easily as Python does, and 2. `Map_reduce` significantly increases load on the server during the duration of the calculation, and if there is insufficient memory on the server to process everything at once the command will fail. 

Also, since both [`Cursor`s](http://api.mongodb.com/python/current/api/pymongo/cursor.html) and [`CommandCursor`s](http://api.mongodb.com/python/current/api/pymongo/command_cursor.html) are not [picklable](https://docs.python.org/3.6/library/pickle.html), they cannot be passed in pipes or queues among processes, further increasing the complexity of the problem. 

It seems like we have truly reached an impasse. Either we must give up on the idea of concurrency and process the cursors returned by `parallel_scan` serially, or we must be willing to take the risk of unsafely duplicating `MongoClient` connections across processes. Right?

### Digging Under It

After a couple long days of digging through hundreds of abandoned StackOverflow threads and documentation pages, I was about ready to call it quits and just run my threaded implementation on the entire CEP dataset. However, in a final act of desparation, I decided to look at the [source code](https://github.com/mongodb/mongo-python-driver) of PyMongo itself. 

Here's the source for `parallel_scan()` in [`collection.py`](mongo-python-driver/pymongo/collection.py) after stripping out comments:

```python
    def parallel_scan(self, num_cursors, **kwargs):
        cmd = SON([('parallelCollectionScan', self.__name),
                   ('numCursors', num_cursors)])
        cmd.update(kwargs)

        with self._socket_for_reads() as (sock_info, slave_ok):
            result = self._command(sock_info, cmd, slave_ok,
                                   read_concern=self.read_concern)

        return [CommandCursor(self, cursor['cursor'], sock_info.address)
                for cursor in result['cursors']]
```
