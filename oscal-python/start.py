#!/usr/bin/env python3

"""
== OSCAL Skipper Project Generation Script ==
The following script was created in order to generate a Skipper18 Project based on the OSCAL metaschema.

This script is the entry point; and will use the oscal and skipper files to process
their data respectively.

Download and Store the "oscal_complete_schema.json" file and store it one directory above where this file is located.
/root
/root/oscal_complete_schema.json
/root/oscal-python/start.py
/root/oscal-python/oscal.py
/root/oscal-python/skipper.py

To anyone reading this code in the future;
And espically to anyone that needs to maintain this in the future....

I am truly sorry for the lack of documentation.
This is V5 during development, and is much better than V1 was...
But that is no excuse. All code should be readable, and documented.

I could get hit by a bus tomorrow, and someone else will need to maintain this.
I truly hope they (you) will forgive me, and that the Code Gods will have mercy on my source code.

(c) 6 NOV 2021 - Will G // Sniper7Kills LLC

"""

import json
import oscal
import skipper
import uuid
from xml.dom import minidom

###
#
###

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

def getNamespaceJson(namespace):
    split = namespace.split('\\')
    temp = {}
    if len(split) > 2:
        temp[split[0]] = getNamespaceJson('\\'.join(split[1:]))
    else:
        temp[split[0]] = {}
    return temp

###
#
###

# Read File
with open("../oscal_complete_schema.json", "r") as read_file:
    OSCALsource =  json.load(read_file)

# List of Referenced Fields
Fields = oscal.gatherFields(OSCALsource)
# List of Objects
Objects = oscal.gatherObjects(OSCALsource)
# List of Relations
Relations = oscal.gatherRelations(Objects)
# List of Inverse Relations
InverseRelations = oscal.invertRelations(Relations)

# Namespace Mapping
Namespaces = {}
for object in Objects:
    namespace = oscal.generateClassNamespaceFromID(object)
    nsJson = getNamespaceJson(namespace)
    Namespaces = merge(Namespaces, nsJson)

# Generate The Root Document
root = minidom.Document()

# Define the Project
project = root.createElement('skipper') 
project.setAttribute('version', "3.2.35.1768")
project.setAttribute('mvc', "Laravel")
project.setAttribute('orm', "Laravel")
project.setAttribute('name', "OSCAL - Automated")
project.setAttribute('uuid', str(uuid.uuid4()))

# Generate Modules and Regions
skipper.generateModules(root, project, Namespaces)

# Generate Entities
skipper.generateEntities(root, project, Objects, Fields)

# Create Entities that will store relations
skipper.createRelationObjects(root, project, Objects, InverseRelations)

# Create Fields in Entities for relations
skipper.createRelationFields(root, project, Objects, InverseRelations)

# Create Associations
skipper.createAssociations(root, project, Objects, InverseRelations)

# Append the Project to the Document
root.appendChild(project)

# Output the root Document to Screen
print(root.toprettyxml(indent ="\t"))