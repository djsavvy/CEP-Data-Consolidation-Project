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
- convert my PyMongo test script into one that remotely connects to Docker instance running the database (essentially create a local, simulated mallspace.rc to run tests with)
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
