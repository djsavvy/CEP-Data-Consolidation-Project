# An Explanation of my Struggles using PyMongo with Multiprocessing

As part of my work for the Harvard Clean Energy Project, I wrote a script called [`mp_collection_crawler.py`](/ExistingMongoCrawling/GetCurrentFields/mp_collection_crawler.py). This program, given the name of a database and a collection within that database, scans every single document in the collection and returns a set of all the top-level fields found anywhere in the collection. 

Linearly scanning the data is quite slow, with some of the collections in the Clean Energy Project databases reaching from 75 to 140 million records a piece. Therefore, I decided to use Python's [`multiprocessing`](https://docs.python.org/3.6/library/multiprocessing.html) library to get some speedup (and at least prevent my local machine from being the bottleneck in the operation -- this was ran before I copied all of the CEP data to my machine, when it was still hosted only on the `molspace` server). 

By far the biggest challenge in this was figuring out how to use `multiprocessing` efficiently and safely. First, I made a [threaded implementation](/ExistingMongoCrawling/GetCurrentFields/thread_unsafe_collection_crawler.py) that, while correct, did not actually run any processes in parallel due to the nature of threads in Python. While `multiprocessing` runs completely different processes in parallel, `threading` runs separate threads serially. This makes the code a lot easier to write, but fails to provide any speedup on a multicore machine. 

When I switched to `multiprocessing` from `threading`, the first challenge I faced was making sure that all of my data was being written safely. Being new to `multiprocessing` (both the Python library and the concept in general), I learned how to safely update a shared counter among different processes using `manager.Value()`. I also learned how to send data from my helper processes to the main one using `manager.list()`. Although I ran into some logical issues initially trying to use `multiprocessing.Queue`, none of them were particularly challenging or meaningful for someone familiar with the subject. By far the most difficult -- and head-banging-worthy -- aspect of this code was getting `multiprocessing` and PyMongo to play nice with each other.


### The General Approach



It says right in the [PyMongo FAQ](http://api.mongodb.com/python/current/faq.html#using-pymongo-with-multiprocessing) that `MongoClient` instances cannot be copied from a parent process to a child process. 
