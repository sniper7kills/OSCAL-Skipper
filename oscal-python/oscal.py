#!/usr/bin/env python3

"""
OSCAL Data Processing

This file is used to store functions related to the processing of OSCAL data.

(c) 6 NOV 2021 - Will G // Sniper7Kills LLC

"""

def gatherFields(source):
    fields = {}
    for field in source['definitions']:
        definitionID = source['definitions'][field]['$id']
        definition = source['definitions'][field]
        definitionType = definition['type']
        if '#field_' in definitionID:
            if definitionType != 'object':
                fields[definitionID] = definition
        else:
            if 'properties' not in definition:
                definition['type'] = 'boolean'
                fields[definitionID] = definition
    return fields

def gatherObjects(source, childDefID = None):
    objects = {}
    if childDefID is None:
        for object in source['definitions']:
            definitionID = source['definitions'][object]['$id']
            definition = source['definitions'][object]
            definitionType = definition['type']
            if '#field_' in definitionID:
                if definitionType == 'object':
                    if 'properties' in definition:
                        objects[definitionID] = definition
            else:
                if 'properties' in definition:
                    objects[definitionID] = definition
                    mergeObjects = gatherChildObjects(definition, definitionID)
                    for key in mergeObjects:
                        objects[key] = mergeObjects[key]
    else:
        if 'type' in source:
            if source['type'] == 'object':
                objects[childDefID] = source
                mergeObjects = gatherChildObjects(source, childDefID)
        else:
            print(source)
            exit()
    return objects

def gatherChildObjects(definition, parentDefinitionID):
    objects = {}
    if 'properties' in definition:
        for field in definition['properties']:
            fieldDefinition = definition['properties'][field]
            if 'type' in fieldDefinition:
                fieldType = fieldDefinition['type']
                if fieldType == 'object':
                    if '$id' in fieldDefinition:
                        childDefID = fieldDefinition['id']
                    else:
                        childDefID = parentDefinitionID + '+' + fieldDefinition['title']

                    if 'properties' in fieldDefinition:
                        objects[childDefID] = fieldDefinition
                        mergeObjects = gatherChildObjects(fieldDefinition, childDefID)
                        for key in mergeObjects:
                            objects[key] = mergeObjects[key]
                elif fieldType == 'array':
                    if 'items' in fieldDefinition:
                        if 'type' in fieldDefinition['items']:

                            if '$id' in fieldDefinition['items']:
                                childDefID = fieldDefinition['items']['id']
                            else:
                                childDefID = parentDefinitionID + '+' + fieldDefinition['items']['title']

                            mergeObjects = gatherObjects(fieldDefinition['items'], childDefID)
                            for key in mergeObjects:
                                objects[key] = mergeObjects[key]
                        elif '$ref' not in fieldDefinition['items']:
                            print(fieldDefinition['items'])
                            exit()
                    else:
                        print("Array Field!")
                elif fieldType != 'string' and fieldType != 'integer':
                    print(fieldType)
                    print("Error! We should not get here!")
                    exit()
    return objects

def gatherRelations(models):
    relations = {}
    for model in models:
        definition = models[model]
        if 'properties' in definition:
            for propName in definition['properties']:
                prop = definition['properties'][propName]
                if 'type' in prop:
                    if prop['type'] == 'object':
                        if model + '+' + prop['title'] in models:
                            if model in relations:
                                relations[model]['hasOne'].append(model + '+' + prop['title'])
                            else:
                                relations[model] = { 'hasMany': [], 'hasOne': [model + '+' + prop['title']]}
                    elif prop['type'] == 'array':
                        if 'items' in prop:
                            if '$ref' in prop['items']:
                                if prop['items']['$ref'] in models:
                                    if model in relations:
                                        relations[model]['hasMany'].append(prop['items']['$ref'])
                                    else:
                                        relations[model] = { 'hasMany': [prop['items']['$ref']], 'hasOne': []}
                            else:
                                if model + '+' + prop['items']['title'] in models:
                                    if model in relations:
                                        relations[model]['hasMany'].append(model + '+' + prop['items']['title'])
                                    else:
                                        relations[model] = { 'hasMany': [model + '+' + prop['items']['title']], 'hasOne': []}
                        else:
                            print(prop)
                            exit()
                elif '$ref' in prop:
                    if prop['$ref'] in models:
                        if model in relations:
                            relations[model]['hasOne'].append(prop['$ref'])
                        else:
                            relations[model] = { 'hasMany': [], 'hasOne': [prop['$ref']]}
                else:
                    print(definition)
                    exit()
        else:
            print("No Properties in relation?")
            print(model)
            exit()
    return relations

def invertRelations(relations):
    invertedRelations = {}
    for inverse in relations:
        for belongs in relations[inverse]['hasOne']:
            if belongs in invertedRelations:
                invertedRelations[belongs]['BT'].append(inverse)
            else:
                invertedRelations[belongs] = {'BT': [inverse], 'BM': []}
        for belongs in relations[inverse]['hasMany']:
            if belongs in invertedRelations:
                invertedRelations[belongs]['BM'].append(inverse)
            else:
                invertedRelations[belongs] = {'BT': [], 'BM': [inverse]}

    return invertedRelations

###
# OSCAL NAMING CONVERSION
###

badStartWords = [
    'oscal',
    'complete',
    '#assembly'
]

noUpperCaseWords = [
    'and',
    'task',
    'risk',
    'part',
    'plan',
    'item',
    'by',
    'id',
    'of',
    'data',
    'flow',
    'date',
    'base',
    'set',
    'user',
    'port',
    'add',
    'all',
    'as',
    'is',
    'addr',
    'line',
    'last',
    'hash',
    'role',
    'link',
    'uuid',
    'back',
    'test',
    'step',
    'type',
    'log',
    'uses',
    'on'
]

noAddSWords = [
    'by',
    'id',
    'of',
    'as',
    'is',
    'on'
]

classWordToNamespace = [
    'assessment',
    'system',
    'select',
    'parameter',
    'responsible',
]

fieldItemsToCopy = [
    'title',
    'description',
    'pattern',
    'type',
    'format',
    'minItems',
    'enum',
    'multipleOf',
    'minimum'
]

modelItemsToCopy = [
    'title',
    'description',
    'required',
]

keepEndS = [
    'status',
    'address',
    'implementationstatus',
    'findingtarget\objectivestatus',
    'system\component\status'
]

###
# Helper Functions
###

def formatWordForPHPNamespace(word):
    if len(word) < 3 and word.lower() not in noAddSWords:
        word = 'S' + word.upper()
    elif len(word) < 5 and word.lower() not in noUpperCaseWords:
        word = word.upper()
    else:
        word = word.capitalize()
    return word

def oscalClassNameToPHP(oscalModelName):
    parts = oscalModelName.split('-')
    name = ''
    isNS = True
    x=0
    for part in parts:
        x = x+1
        if isNS and part in classWordToNamespace and x < len(parts):
            name = formatWordForPHPNamespace(part) + '\\'
        elif '_' in part:
            wordSplit = part.split('_')
            name = name + formatWordForPHPNamespace(wordSplit[0]) + '\\' + formatWordForPHPNamespace(wordSplit[1])
        else:
            isNS = False
            name = name + formatWordForPHPNamespace(part)
    if name[-1] != 's' or name.lower() in keepEndS:
        return name

    return name[:-1]


def removeStartWords(partsArray):
    global badStartWords
    if len(partsArray) > 1:
        if partsArray[0] in badStartWords:
            return removeStartWords(partsArray[1:])
    return partsArray


def oscalNamespaceToPHP(oscalNamespace):
    parts = oscalNamespace.split('-')
    parts = removeStartWords(parts)
    namespace = ''
    for part in parts:
        namespace = namespace + formatWordForPHPNamespace(part) + '\\'
    return namespace

def generateClassNamespaceFromID(oscalID):
    if ':' in oscalID:
        [modelNameSpace, modelName] = oscalID.split(':', 1)
        return oscalNamespaceToPHP(modelNameSpace) + oscalClassNameToPHP(modelName)
    elif '#assembly_' in oscalID or '#field_' in oscalID:
        if '#field_' in oscalID:
            oscalID = oscalID[len('#field_'):]
        elif '#assembly_' in oscalID:
            oscalID = oscalID[len('#assembly_'):]
        [modelNameSpace, modelName]  = oscalID.split('_')
        return oscalNamespaceToPHP(modelNameSpace) + oscalClassNameToPHP(modelName.replace('+', '_').replace(' ', '-'))
    else:
        return oscalClassNameToPHP(oscalID.replace(' ', '-'))

###
# OSCAL NAMING CONVERSION END
###