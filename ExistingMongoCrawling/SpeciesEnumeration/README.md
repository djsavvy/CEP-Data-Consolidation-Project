# Species Enumeration README

Alex asked me to create this file before I leave the CEP project to document the code in the last stage of my project -- to enumerate all the different species of data that can be found in all the existing CEP mongo databases. 

## List of Files with Descriptions

- [remote_connector_template.py](/ExistingMongoCrawling/SpeciesEnumeration/) This is a template Python script to connect to the molspace.rc.fas.harvard.edu server containing the existing CEP mongo databases. It handles connecting to the database (taking in the username and password as command line arguments), as well as closing the connection cleanly upon exit (even when that exit is done with a `Ctrl`-C command)
