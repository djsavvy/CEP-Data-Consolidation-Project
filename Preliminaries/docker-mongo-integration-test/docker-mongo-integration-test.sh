#!/bin/bash

# Make sure docker's mongo container is up-to-date and that mongo_integration_test does not exist already
docker pull mongo > /dev/null
docker kill mongo_integration_test > /dev/null
docker rm mongo_integration_test > /dev/null

# Start mongo instance
docker run -p 27017:27017 --name mongo_integration_test --detach mongo

# Determine the container 
CONTAINER="$(docker ps | grep mongo_integration_test | awk '{print $1}')"
echo "Mongo running in Docker container" "${CONTAINER}"
