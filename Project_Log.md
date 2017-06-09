# Savvy's Summer 2017 Project Log

## Monday, May 22

- First day on the job! :)
- Alex thought I was starting next week, so everything was a little bit disorganized. However, this is a good thing in my eyes because it allows more flexibility and we are all on the same page. 
- We started by going over some basic expectations and taking care of some initial operational stuff. 
	+ Created a shared Trello to outline tasks, etc. [Link to First Week Planning Trello board](https://trello.com/b/rSJNqnK7/first-week)
	+ Alex gave me a very high-level overview of the job -- still need to find out more. 
- Took care of I-9 form and card swipe access with Felix -- **still need to get Slack set up, Mailing List Access, Group Calendar**
- Established communication protocols:
	+ Trello (see above)
	+ Daily meeting with Alex around 11am
	+ Weekly meeting with entire team on Thursday afternoons
- Alex treated me to lunch :smile:
	+ said he's leaving the lab in August :cry:
- Went through a review of UNIX shell [Link here](https://software.rc.fas.harvard.edu/training/workshop_intro_unix/latest/#(1))
- Research Computing (RC) and Odyssey:
	+ Created an account
	+ Read through several of the docs pages
	+ Watched the introduction video, completed the online quiz and survey (done with necessary steps)
		* [Located here](https://www.rc.fas.harvard.edu/training/introduction-to-odyssey-online/)
	+ Practiced using SCP to transfer files from Odyssey to my local machine
	+ Still need to familiarize myself more with file structure of the Work Units -- going to wait until next week to do that since Odyssey will go down for maintenance tonight through the next 3 days
- Did some general customization/installation on the Mac that has been assigned to me for the summer
	+ installed Sublime Text, Chrome
	+ went through all the settings
	+ generally familiarized myself with the operating system -- feeling much more comfortable
	+ generally started establishing a workflow for myself
- Created a GitHub repository for the project
- Reviewed GitHub markdown syntax to create my log and schedule files
- Created a [Rough Draft Schedule](/Rough_Draft_Schedule.md) and asked Alex for feedback -- currently waiting for his response
- *Note:* I won't be able to use Odyssey until Wednesday noon *at least* so I have to put a lot of my tasks on hold. Best to focus on working with the other technologies as best as I can. 


### Goals for tomorrow:

- Check with Siria on:
	+ Slack
	+ Mailing List
	+ Group Calendar
- Check with Alex on:
	+ Draft Schedule
- Start learning about MongoDB and/or Docker
	+ spin up Mongo instance in Docker
	+ both write and query data to/from it
- Also use an Anaconda environment with MongoDB
	+ useful later for re-parsing CEP files
- Also research (if I hit a wall) Jupyter notebooks
	+ cool interactions between Sage and Jupyter
	+ not directly related to this project, just more for my own sake	


### Goals for after Odyssey comes back up:

- Ask Alex to introduce me to the directory structure (or just explore it myself)
	+ *Note:* Don't forget to somehow enable "show hidden files and folders" while browsing to make sure I don't miss anything!
	+ /n/aspuru_lab versus /n/aspuru_lab2 -- why two directories?
		* Alex is not sure what's in these
		* another one too -- aag, a2g2
		* a lot of stuff in /n/aagfs01, some of which is old CEP stuff consolidated (missing a lot though)
		* be SUPER careful in those directories -- I have admin rights
	+ non-Odyssey data sources -- Alex mentioned that Harvard's own data centers would be overwhelmed by the computations needed and that they are sent to IBM -- determine locations of those




## Tuesday, May 23

### Morning Tasks:

- Added to Slack, mailing list, and calendar!
- Alex approved the first draft of my 
- Read through the "Introduction" section of the MongoDB docs and relevant links


### Meeting with Alex:

This afternoon I should create some sort of test app with Mongo -- insert, read, and modify data -- to get the hang of things. 

However, in the longer term, as discussed before (i.e. during my interview), Mongo probably is not the best technology to use for the project, as future analyses for the project might want to capitalize on having relationships between data (i.e. a relational database is probably best for the job). 

Regardless of the database system we end up using, we will have a few standard fields, with an amorphous "blob" field, stored as JSON (object : value pairs). 

Possible solutions:
- Use PostgreSQL -- has a JSON field
- Pure SQL, but with an entity-attribute-value system
	+ essentially, instead of one row per molecule, have one row per feature per molecule

The latter design has a number of advantages:
- Allows parsing to be done modularly (i.e. instead of writing one giant parser, you can choose only to parse specifically the fields that you want at once -- easy to add in data from new fields later)
- Allows analysis to be done modularly -- the schema can be blind to whatever future modes of analysis must be done (i.e. don't need to plan ahead for what types of analysis others might want to do -- it's all there)
- You can always create views or data-dump microtables containing arbitrary subsets of data
- Easier to manage gaps in data -- i.e. different QChem outputs with different fields included or missing


### Afternoon Tasks:

- Practiced using the Python interface to connect to MongoDB, insert documents, run queries, and update the database: [MongoDB-test/test.py](/MongoDB-test/test.py)
- Played around with Robomongo (a MongoDB GUI client)
- Went through the Docker tutorial


### Goals for Tomorrow:

Alex suggested a project that would combine Docker and MongoDB:
- create a MongoDB instance within Docker
- convert my PyMongo test script into one that remotely connects to Docker instance running the database (essentially create a local, simulated molspace.rc to run tests with)
- run this new Python script inside a Conda environment (requires a separate script to set up) that imports PyMongo



## Wednesday, May 24

- Started off by going through a Vim tutorial -- I was already familiar with the best text editor in the Universe, albeit barely:
	+ Only really knew how to switch between normal and insert mode, as well as how to write and quit -- not really the best competency. 
	+ I'm going to have to learn to edit text files purely within the terminal anyway to work with Odyssey, so this is well worth the invested time. 
- Alex told me to map Caps Lock to ESC -- quite awesome!
- Alex also gave me BitBucket access to some of the previous CEB/a2g2 code just for reference.
- I updated yesterday's Pymongo project to connect to a MongoDB instance within Docker
	+ This tripped me up for several hours, as I was having issues with port connection; the stupid thing I was missing was that I had to map port 27107 (the mongo port) to itself. Not really sure why that fixed the issue, but it did. 
	+ There was no modification to the actual Python code, or even the database connection code. My mapping 27017 in docker to 27017, I got mongo to connect to the docker instance instead of a local one
	+ I even tested this by uninstalling mongodb locally and making sure it still worked within Docker!
	+ Location of bash script: [docker-mongo-integration.sh](/docker-mongo-integration-test/docker-mongo-integration-test.sh)
- Received information to connect to the existing Odyssey MongoDBs (both as an administrator and a read-only user)



## Thursday, May 25

- Struggled quite a bit with the sheer size of the database -- I tried running some simple queries (i.e. an array field exists and has nonempty results) and they took 20+ minutes to run. Furthermore, I am having a weird issue where that query runs correctly on small datasets (i.e. 100K records) but fails on the entire collection (77M records). Not really sure what is going on there. 
- Also apparently my administrator mongo connection does not have access to view running operations and kill them -- need to try and get access for that. 
- Possible solutions to the size issues for when I am testing my scripts:
	+ Pre-query limiting -- I can do this with mongo's aggregate function using $limit
	+ Create my own db by copying some documents from the CEP databases
	+ Build a test DB from scratch and populate it with my own data to test scripts

### Meeting with Alex

I am going to try taking a slightly different direction in the project -- instead of going with a depth-first approach of trying to understand/investigate the databases one collection at a time, one column at a time, I will instead compile a list of columns for each database -- this will give me a list of all columns and let me determine relationships between them. Useful to choose a list of columns for when I create the new, consolidated database. Two possible approaches:
- Search around for mongo metadata -- technically not supposed to use this, but probably works, if I can access some list of all the columns. 
- (more likely result) I will have to write a script to search for all top-level (calculations) and second-level (metadata) fields. 
	+ I can do this with a python script that collects list of columns into a set

List of resources to parallelize programs:
- GNU parallel program -- give it a command and it runs it on different cores on the local machine
- wihtin Python -- multiprocessing -- have to actually alter code
- Python async I/O (relatively new)
- The little book of Semaphores by Allen Downey -- cool resource to check out 


## Friday, May 25 - Friday, June 2

- Unfortunately, I got really sick :(
	+ Took Friday off, Monday was a holiday, have been working half-days since then
- I wrote a few different versions of a program to get all the fields from a collection in a db in the molspace.rc.fas.harvard.edu server
	+ One is a thread unsafe version that uses multithreading but no concurrency, and is not actually thread-safe
		* This was my first implementation
	+ The second one uses multiprocessing to run it in parallel, is process-safe
		* Took me a long time to figure out, very hackish solution
		* It would be worth it for me to do a writeup on how I got it to work, since nobody online who asked this question got an answer
- I made sure both versions of the program did not include the login credentials so I could safely push them to github


## Monday, June 5 - Friday, June 9

- I got a LOT done this week :)
- Spent a couple days writing scripts to determine all the top-level fields in any given collection by scanning every single row
	+ used a multiprocessing approach to speed things up significantly
	+ this was quite tricky -- Pymongo connections are thread-safe but not fork-safe
	+ I tried using threads at first, and it worked, but I realized that Python's implementation of multithreading does not actually provide a speedup since the threads run linearly
	+ switched to using Python's multiprocessing library, which required me to use forks
	+ Due to the non-fork-safe pymongo connections, and Pymongo's built-in connection pooling, when I ran a parallel collection scan I could not actually iterate over the resulting cursors in the same connection
	+ I had to look at the pymongo source code, copy part of it, and modify it -- I created a custom parallel_scan method that returned cursor objects I could reference using a new connection, making it fork-safe
- Unfortunately, I never ended up directly using the top-level field analysis done above. Instead, we proceeded as follows:
- I wrote scripts to download all of the mongo data onto my local machine
- Wrote scripts to enumerate all the species present in each collection
	+ uses a probabilistic approach, only samples about 1000 records from each collection but does so in a way that we can be reasonably confident we have not missed any species
- Wrote scripts to parse these species into a pretty format
	+ organized by database, by collection
	+ lists a "superspecies" for each collection -- a list of all the fields in that collection
	+ lists the individual species as sets of fields missing from the superspecies
	+ lists the intersection of all species -- the list of fields present in every single record in the collection
- Unfortunately, I had some unexpected personal issues come up in the last couple of days and so today is my last day in the lab :(
- However, Alex said I was still able to accomplish quite a bit that would be helpful for the CEP team in the future, so I am glad that I was able to make an impact in my three weeks here. 
- The [Species Enumeration README](/ExistingMongoCrawling/SpeciesEnumeration/README.md) is a file that has much more depth regarding the last stage of the project. It is also designed to be an introduction to whoever continues this project or decieds to build on my work. 
