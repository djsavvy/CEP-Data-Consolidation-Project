#This is a Python file for me to test my knowledge of the Python interface for MongoDB. 
#My goal is to test my ability to write to a database, read from it, and modify the contents. 


#Note that to run this file you need to have an instance of mongod running already

import pymongo
import random

mongoclient = pymongo.MongoClient()
db = mongoclient.testdb
squad = db.test_collection1


#Create a Savvy and insert him into our collection

doc_savvy = {"name" : "Savvy",
			 "type" : "human",
			 "planet" : "C137",
			 "arms" : 2,
			 "legs" : 2,
			 "eyes" : 2}

squad.insert_one(doc_savvy)

#Give him some squad in the collection

docs_friends = []

types = ["cyborg", "android", "rick", "morty", "omnic"]
planets = ["mercury", "venus", "C137", "mars", "jupiter", "saturn", "uranus", "neptune"]
num_arms = num_legs = num_eyes = range(0, 8)


for i in xrange(10000):
	tempdoc = {}
	tempdoc["type"] = random.choice(types)
	tempdoc["planet"] = random.choice(planets)
	tempdoc["arms"] = random.choice(num_arms)
	tempdoc["legs"] = random.choice(num_legs)
	tempdoc["eyes"] = random.choice(num_eyes)
	docs_friends.append(tempdoc)

squad.insert_many(docs_friends)


# We can run some simple queries that return only the first result

print squad.find_one({"type" : 'cyborg'})
print squad.find_one({"type" : 'omnic', "planet" : "C137"})



# We can query for more than one document -- find() returns a cursor that lets us iterate over all matches
# The following searches for omnics on C137 with more than 2 eyes, but fewer than 5, and sorts the results by the number of arms

for being in squad.find({"type" : 'omnic', 
                        "planet" : "C137", 
                        "$and" : [ {"eyes" : {"$lt" : 5}}, {"eyes" : {"$gt" : 2}} ]},
                        sort = [("arms", pymongo.ASCENDING)]):
	print being




# Now we can update the collection by turning all the humans into cyborgs:

squad.update_many({"type" : "human"}, {"$set" : {"type" : "cyborg"}})

# As expected, there are no humans left

print squad.find_one({"type" : "human"})

# We can check to make sure that Savvy is still around, and has been turned into a cyborg:

print squad.find_one({"name" : "Savvy"})



db.logout()