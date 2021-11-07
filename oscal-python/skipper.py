#!/usr/bin/env python3
import uuid
import oscal

"""
Skipper Data Processing

This file is used to generate Skipper related Data

(c) 6 NOV 2021 - Will G // Sniper7Kills LLC

"""

def generateModules(root, project, Namespaces):
    for rootNS in Namespaces:
        module = root.createElement('module')
        module.setAttribute('name', '\\' + rootNS)
        module.setAttribute('local-name', rootNS)
        module.setAttribute('namespace', '\\' + rootNS)
        module.setAttribute('local-namespace', rootNS)
        module.setAttribute('export-format', 'Laravel')
        module.setAttribute('export-path', '.')
        module.setAttribute('uuid', str(uuid.uuid4()))
        
        generateRegions(root, module, Namespaces[rootNS])

        project.appendChild(module)
    return

def generateRegions(root, module, Namespaces):
    for regionName in Namespaces:
        region = root.createElement('region')
        region.setAttribute('caption', regionName)
        parentNS = module.getAttribute('namespace')
        region.setAttribute('namespace', parentNS + '\\' + regionName)
        region.setAttribute('uuid', str(uuid.uuid4()))
        
        generateRegions(root, region, Namespaces[regionName])

        module.appendChild(region)
    return

def generateEntities(root, project, Objects, Fields):
    # Loop over every Entity we need to add
    for object in Objects:
        entityNamespace = oscal.generateClassNamespaceFromID(object)
        parts = entityNamespace.split('\\')

        # Create the Entity to add
        entity = root.createElement('entity')
        entity.setAttribute('name', entityNamespace)
        entity.setAttribute('local-name', parts[-1])
        entity.setAttribute('namespace', '\\' + '\\'.join(parts[:-1]))
        entity.setAttribute('uuid', str(uuid.uuid4()))
            
        # Primary Key
        field = root.createElement('field')
        field.setAttribute('name', 'internal_id')
        field.setAttribute('description', 'Internal Primary Key')
        field.setAttribute('type', 'uuid')
        field.setAttribute('uuid', str(uuid.uuid4()))
        attributes = {'required': 'true', 'unique': 'true', 'primary': 'true'}
        for attribute in attributes:
            field.setAttribute(attribute, attributes[attribute])
        entity.appendChild(field)
        
        # Add Fields
        for propertyName in Objects[object]['properties']:
            fieldDefinition = Objects[object]['properties'][propertyName]
            required = propertyName in Objects[object]
            field = generateField(root, propertyName, fieldDefinition, Fields, required)
            if field is not None:
                entity.appendChild(field)

        # Find where to add the Entity to
        found = False
        if len(parts) == 2:
            # Find module to add Entity To
            for target in project.getElementsByTagName("module"):
                if target.getAttribute('name') == '\\' + parts[0]:
                    found = True
                    break
            # Exit if not found
            if not found:
                print("Unable to find root Module.")
                exit()
        elif len(parts) > 2:
            # Find Region to add Entity To
            for target in project.getElementsByTagName("region"):
                if target.getAttribute('namespace') == '\\' + '\\'.join(parts[:-1]):
                    found = True
                    break
            # Exit if not found
            if not found:
                print("Unable to find region Module.")
                exit()
        # Saftey Check
        else:
            print("Error... We Should never Get Here!")
            exit()

        # Add the Entity to the Target
        target.appendChild(entity)
    return

def generateField(root, fieldName, fieldDefinition, Fields, isRequired = False):
    skipTypes = [
        'array',
        'object'
    ]
    textFields = [
        'remarks',
        'description',
        'prose'
    ]

    if 'type' in fieldDefinition:
        if fieldDefinition['type'] not in skipTypes:
            field = root.createElement('field')
            field.setAttribute('name', fieldName)

            description = ""
            if 'description' in fieldDefinition:
                description = description + fieldDefinition['description']
            if 'pattern' in fieldDefinition:
                description = description + ':pattern:' + fieldDefinition['pattern']

            field.setAttribute('description', description)
            if 'enum' in fieldDefinition:
                enumValues = '\'' + '\', \''.join(fieldDefinition['enum']) + '\''
                field.setAttribute('type', "enum")
                field.setAttribute('enum-values', enumValues)
            elif 'string' == fieldDefinition['type']:
                if fieldName in textFields:
                    field.setAttribute('type', 'text')
                else:
                    field.setAttribute('type', fieldDefinition['type'])
            else:
                field.setAttribute('type', fieldDefinition['type'])

            if isRequired:
                field.setAttribute('required', 'true')

            field.setAttribute('uuid', str(uuid.uuid4()))
        
            return field
    elif '$ref' in fieldDefinition:
        if fieldDefinition['$ref'] in Fields:
            field = root.createElement('field')
            field.setAttribute('name', fieldName)

            fieldDefinition = Fields[fieldDefinition['$ref']]

            description = ""
            if 'description' in fieldDefinition:
                description = description + fieldDefinition['description']
            if 'pattern' in fieldDefinition:
                description = description + fieldDefinition['pattern']

            field.setAttribute('description', description)

            if 'enum' in fieldDefinition:
                enumValues = '\'' + '\', \''.join(fieldDefinition['enum']) + '\''
                field.setAttribute('type', "enum")
                field.setAttribute('enum-values', enumValues)
            elif 'string' == fieldDefinition['type']:
                if fieldName in textFields:
                    field.setAttribute('type', 'text')
                else:
                    field.setAttribute('type', fieldDefinition['type'])
            else:
                field.setAttribute('type', fieldDefinition['type'])

            field.setAttribute('uuid', str(uuid.uuid4()))
        
            return field
    else:
        # We should really never end up here
        print(fieldDefinition)
        exit()

    return None

def generateRelationRegions(root, module, relationClass):
    parts = relationClass[1:].split('\\')[1:-1]
    
    for part in parts:
        found = False
        for region in module.getElementsByTagName('region'):
            if region.getAttribute('caption') == part:
                found = True
                break
        if not found:
            # Create Region and
            region = root.createElement('region')
            region.setAttribute('caption', part)
            parentNS = module.getAttribute('namespace')
            region.setAttribute('namespace', parentNS + '\\' + part)
            region.setAttribute('local-namespace', part)
            region.setAttribute('uuid', str(uuid.uuid4()))
            # Append to the parent
            module.appendChild(region)

        module = region
    return

def generateRelationEntities(root, module, relationClass):
    parts = relationClass.split('\\')[1:-1]

    found = False
    for region in module.getElementsByTagName('region'):
        if region.getAttribute('namespace') == '\\' + '\\'.join(parts):
            found = True
            # Create the Entity to add
            entity = root.createElement('entity')
            entity.setAttribute('name', relationClass)
            entity.setAttribute('local-name', relationClass.split('\\')[-1])
            entity.setAttribute('namespace', '\\'.join(relationClass.split('\\')[:-1]))
            entity.setAttribute('uuid', str(uuid.uuid4()))
            # Relationship ID
            field = root.createElement('field')
            field.setAttribute('name', 'internal_id')
            field.setAttribute('description', 'Relationship Primary Key')
            field.setAttribute('type', 'uuid')
            field.setAttribute('uuid', str(uuid.uuid4()))

            attributes = {'required': 'true', 'unique': 'true', 'primary': 'true'}
            for attribute in attributes:
                field.setAttribute(attribute, attributes[attribute])
            entity.appendChild(field)
            region.appendChild(entity)
            break
    if not found:
        print("Unable to find Relation Region")
        exit()

def addAbleFields(root, module, relationClass, ableString):
    if '\\' in ableString:
        ableString = ableString.split('\\')[-1].lower()
    for entity in module.getElementsByTagName('entity'):
        if entity.getAttribute('name') == relationClass:
            field = root.createElement('field')
            field.setAttribute('name', ableString[:-4] + '_id')
            field.setAttribute('description', 'ID of ' + ableString[:-4] + ' model.')
            field.setAttribute('type', 'uuid')
            field.setAttribute('uuid', str(uuid.uuid4()))
            entity.appendChild(field)
            field = root.createElement('field')
            field.setAttribute('name', ableString + '_id')
            field.setAttribute('description', 'ID of related  model.')
            field.setAttribute('type', 'uuid')
            field.setAttribute('uuid', str(uuid.uuid4()))
            entity.appendChild(field)
            field = root.createElement('field')
            field.setAttribute('name', ableString + '_type')
            field.setAttribute('description', 'Type of related model.')
            field.setAttribute('type', 'string')
            field.setAttribute('uuid', str(uuid.uuid4()))
            entity.appendChild(field)
            break;

def addRelatedFields(root, module, relationClass, ownerClass, inverseClass):
    for entity in module.getElementsByTagName('entity'):
        if entity.getAttribute('namespace') == '\\'.join(relationClass.split('\\')[:-1]) and entity.getAttribute('name') == relationClass:
            field = root.createElement('field')
            if ownerClass == inverseClass:
                field.setAttribute('name', 'parent_' + ownerClass.lower() + '_id')
            else:
                field.setAttribute('name', ownerClass.lower() + '_id')
            field.setAttribute('description', 'ID of ' + ownerClass + ' model.')
            field.setAttribute('type', 'uuid')
            field.setAttribute('uuid', str(uuid.uuid4()))
            entity.appendChild(field)
            field = root.createElement('field')
            field.setAttribute('name', inverseClass.lower() + '_id')
            field.setAttribute('description', 'ID of ' + inverseClass + '  model.')
            field.setAttribute('type', 'uuid')
            field.setAttribute('uuid', str(uuid.uuid4()))
            entity.appendChild(field)
            break


def createRelationObjects(root, project, Objects, InverseRelations):

    Modules = project.getElementsByTagName('module')
    found = False
    for module in Modules:
        if module.getAttribute('local-name') == 'Relations':
            found = True
            break
    if not found:
        module = root.createElement('module')
        module.setAttribute('name', '\\Relations')
        module.setAttribute('local-name', 'Relations')
        module.setAttribute('namespace', '\\Relations')
        module.setAttribute('local-namespace', 'Relations')
        module.setAttribute('export-format', 'Laravel')
        module.setAttribute('export-path', '.')
        module.setAttribute('uuid', str(uuid.uuid4()))
        project.appendChild(module)

    # Iterate Through Each Object
    for ownerOscalID in Objects:
        # Convert the Owner ID into PHP namespace
        ownerClass = oscal.generateClassNamespaceFromID(ownerOscalID)
        if ownerOscalID in InverseRelations:
            for relationType in InverseRelations[ownerOscalID]:
                if relationType == 'BM' and len(InverseRelations[ownerOscalID]['BM']) > 1:
                    ableString = oscal.generateClassNamespaceFromID(ownerOscalID) + 'able'
                    PolymorphicClass = '\\Relations\\Polymorphic\\' + ableString
                    generateRelationRegions(root, module, PolymorphicClass)
                    generateRelationEntities(root, module, PolymorphicClass)
                    addAbleFields(root, module, PolymorphicClass, ableString)
                elif relationType == 'BM' and len(InverseRelations[ownerOscalID]['BM']) == 1:
                    inverse = InverseRelations[ownerOscalID]['BM'][0]
                    inverseClass = oscal.generateClassNamespaceFromID(inverse).split('\\')[-1]
                    objectClass = oscal.generateClassNamespaceFromID(ownerOscalID).split('\\')[-1]
                    relationClass = '\\Relations\\BelongsToMany\\' + objectClass + '_' +  inverseClass
                    generateRelationRegions(root, module, relationClass)
                    generateRelationEntities(root, module, relationClass)
                    addRelatedFields(root, module, relationClass, oscal.generateClassNamespaceFromID(ownerOscalID).split('\\')[-1], oscal.generateClassNamespaceFromID(inverse).split('\\')[-1])

def createRelationFields(root, project, Objects, InverseRelations):
    for object in Objects:
        if object in InverseRelations:
            # Get the Entity Model
            found = False
            for entity in project.getElementsByTagName('entity'):
                if entity.getAttribute('name') == oscal.generateClassNamespaceFromID(object):
                    found = True
                    break
            if not found:
                print("Unable to find 'Owner' Entity for Relationship creation")
                print(oscal.generateClassNamespaceFromID(object))
                exit()
            for relationType in InverseRelations[object]:
                if relationType == 'BT' and len(InverseRelations[object]['BT']) > 1:
                    ableString = ''.join(oscal.generateClassNamespaceFromID(object).split('\\')[-1:]).lower() + 'able'
                    # Add Fields To Object
                    field = root.createElement('field')
                    field.setAttribute('name', ableString.lower() + '_id')
                    field.setAttribute('description', 'ID of ' + ableString + ' model.')
                    field.setAttribute('type', 'uuid')
                    field.setAttribute('uuid', str(uuid.uuid4()))
                    entity.appendChild(field)
                    field = root.createElement('field')
                    field.setAttribute('name', ableString.lower() + '_type')
                    field.setAttribute('description', 'Type of ' + ableString + ' model.')
                    field.setAttribute('type', 'string')
                    field.setAttribute('uuid', str(uuid.uuid4()))
                    entity.appendChild(field)
                elif relationType == 'BT' and len(InverseRelations[object][relationType]) == 1:
                    for inverse in InverseRelations[object][relationType]:
                        inverseClass = oscal.generateClassNamespaceFromID(inverse).split('\\')[-1]
                        # Add Field to Object
                        field = root.createElement('field')
                        field.setAttribute('name', inverseClass.lower() + '_id')
                        field.setAttribute('description', 'ID of ' + inverseClass + ' model.')
                        field.setAttribute('type', 'uuid')
                        field.setAttribute('uuid', str(uuid.uuid4()))
                        entity.appendChild(field)

def createAssociations(root, project, Objects, InverseRelations):
    
    MMES = []

    for object in Objects:
        if object in InverseRelations:
            # Get the Entity Model
            found = False
            if len(oscal.generateClassNamespaceFromID(object).split('\\')) > 2:
                for region in project.getElementsByTagName('region'):
                    if region.getAttribute('namespace') == '\\' + '\\'.join(oscal.generateClassNamespaceFromID(object).split('\\')[:-1]):
                        found = True
                        break
                if not found:
                    print("Unable to find 'Owner' region for Relationship creation")
                    print('\\' + '\\'.join(oscal.generateClassNamespaceFromID(object).split('\\')[:-1]))
                    exit()
            else:
                for region in project.getElementsByTagName('entity'):
                    if region.getAttribute('namespace') == '\\' + '\\'.join(oscal.generateClassNamespaceFromID(object).split('\\')[:-1]):
                        found = True
                        break
                if not found:
                    print("Unable to find 'Owner' entity for Relationship creation")
                    print('\\' + '\\'.join(oscal.generateClassNamespaceFromID(object).split('\\')[:-1]))
                    exit()

            # Direct Relations
            if len(InverseRelations[object]['BT']) > 1:
                ableString = ''.join(oscal.generateClassNamespaceFromID(object).split('\\')[-1:]).lower() + 'able'
                for inverse in InverseRelations[object]['BT']:
                    inverseClass = oscal.generateClassNamespaceFromID(inverse)
                    objectClass = oscal.generateClassNamespaceFromID(object)
                    Relation = root.createElement('association')
                    Relation.setAttribute('from', objectClass)
                    Relation.setAttribute('to', inverseClass)
                    Relation.setAttribute('caption', inverseClass + ' Has one ' + objectClass)
                    oAlias = ''.join(objectClass.split('\\')[-1:])
                    Relation.setAttribute('owner-alias', oAlias.lower())
                    iAlias = ''.join(inverseClass.split('\\')[-1:])
                    Relation.setAttribute('inverse-alias', iAlias.lower())
                    Relation.setAttribute('many-owner', 'true')
                    Relation.setAttribute('many-inverse', 'false')
                    Relation.setAttribute('uuid', str(uuid.uuid4()))
                    RelationDetail = root.createElement('association-polymorph')
                    RelationDetail.setAttribute('id-field', ableString + '_id')
                    RelationDetail.setAttribute('type-field', ableString + '_type')
                    RelationDetail.setAttribute('name', ableString)
                    RelationDetail.setAttribute('uuid', str(uuid.uuid4()))
                    Relation.appendChild(RelationDetail)
                    region.appendChild(Relation)
            elif len(InverseRelations[object]['BT']) == 1:
                for inverse in InverseRelations[object]['BT']:
                    inverseClass = oscal.generateClassNamespaceFromID(InverseRelations[object]['BT'][0])
                    objectClass = oscal.generateClassNamespaceFromID(object)
                    Relation = root.createElement('association')
                    Relation.setAttribute('from', '\\' + objectClass)
                    Relation.setAttribute('to', '\\' + inverseClass)
                    Relation.setAttribute('caption', inverseClass + ' Has ' + objectClass + 's')
                    oAlias = ''.join(objectClass.split('\\')[-1:])
                    Relation.setAttribute('owner-alias', oAlias.lower())
                    iAlias = ''.join(inverseClass.split('\\')[-1:])
                    Relation.setAttribute('inverse-alias', iAlias.lower())
                    Relation.setAttribute('uuid', str(uuid.uuid4()))
                    RelationDetail = root.createElement('association-field')
                    fieldName = oscal.generateClassNamespaceFromID(InverseRelations[object]['BT'][0]).split('\\')[-1]
                    RelationDetail.setAttribute('from', fieldName.lower() + '_id')
                    RelationDetail.setAttribute('to', 'internal_id')
                    RelationDetail.setAttribute('uuid', str(uuid.uuid4()))
                    Relation.appendChild(RelationDetail)
                    region.appendChild(Relation)

            # Many Relations
            if len(InverseRelations[object]['BM']) > 1:
                # Get Region For Relation
                found = False
                region = None
                for region in project.getElementsByTagName('region'):
                    #print(region.getAttribute('namespace'))
                    if region.getAttribute('namespace') == '\\Relations\\Polymorphic':
                        found = True
                        break
                if not found:
                    print("Unable to find 'Polymorphic' Region for association creation")
                    exit()

                ableString = oscal.generateClassNamespaceFromID(object) + 'able'
                PolymorphicClass = '\\Relations\\Polymorphic\\' + ableString
                if '\\' in ableString:
                    ableString = ableString.split('\\')[-1]
                for relation in InverseRelations[object]['BM']:
                    relationString = oscal.generateClassNamespaceFromID(relation).split('\\')[-1]
                    Relation = root.createElement('many-to-many')
                    Relation.setAttribute('mn-entity', PolymorphicClass)
                    Relation.setAttribute('caption', relationString + ' is ' + ableString)
                    Relation.setAttribute('uuid', str(uuid.uuid4()))
                    # Owning
                    owningEntity = root.createElement('many-to-many-entity')
                    owningEntity.setAttribute('name', '\\' + oscal.generateClassNamespaceFromID(object))
                    owningEntity.setAttribute('owning-side', "true")
                    if relationString + 'able' == ableString:
                        owningEntity.setAttribute('alias', 'parent_' + oscal.generateClassNamespaceFromID(object).split('\\')[-1].lower() + 's')
                    else:
                        owningEntity.setAttribute('alias', oscal.generateClassNamespaceFromID(object).split('\\')[-1].lower() + 's')
                    mme = str(uuid.uuid4())
                    owningEntity.setAttribute('uuid', mme)
                    MMES.append(mme)
                    # Owning Field
                    owningEntityField = root.createElement('many-to-many-field')
                    owningEntityField.setAttribute('from', ableString[:-4].lower() + '_id')
                    owningEntityField.setAttribute('to', 'internal_id')
                    owningEntityField.setAttribute('uuid', str(uuid.uuid4()))
                    
                    owningEntity.appendChild(owningEntityField)
                    Relation.appendChild(owningEntity)
                    

                    polymorphRelation = root.createElement('many-to-many-polymorph')
                    polymorphRelation.setAttribute('id-field', ableString.lower() + '_id')
                    polymorphRelation.setAttribute('type-field', ableString.lower() + '_type')
                    polymorphRelation.setAttribute('name', ableString.lower() )
                    polymorphRelation.setAttribute('uuid', str(uuid.uuid4()))
                    Relation.appendChild(polymorphRelation)

                    # relation Entity
                    relationEntityField = root.createElement('many-to-many-entity')
                    relationEntityField.setAttribute('name', '\\' + oscal.generateClassNamespaceFromID(relation))
                    relationEntityField.setAttribute('owning-side', "false")
                    relationEntityField.setAttribute('alias', oscal.generateClassNamespaceFromID(relation).split('\\')[-1].lower() + 's')
                    mme = str(uuid.uuid4())
                    relationEntityField.setAttribute('uuid', mme)
                    MMES.append(mme)
                    Relation.appendChild(relationEntityField)
                
                    region.appendChild(Relation)
            elif len(InverseRelations[object]['BM']) == 1:
                # Get Region For Relation
                found = False
                region = None
                for region in project.getElementsByTagName('region'):
                    if region.getAttribute('namespace') == '\\Relations\\BelongsToMany':
                        found = True
                        break
                if not found:
                    print("Unable to find 'BelongsToMany' region for association creation")
                    exit()

                inverse = InverseRelations[object]['BM'][0]
                inverseClass = oscal.generateClassNamespaceFromID(inverse).split('\\')[-1]
                objectClass = oscal.generateClassNamespaceFromID(object).split('\\')[-1]
                relationClass = '\\Relations\\BelongsToMany\\' + objectClass + '_' +  inverseClass

                Relation = root.createElement('many-to-many')
                Relation.setAttribute('mn-entity', relationClass)
                Relation.setAttribute('caption', objectClass + ' HasMany ' + inverseClass)
                Relation.setAttribute('uuid', str(uuid.uuid4()))

                # Owner
                owningEntity = root.createElement('many-to-many-entity')
                owningEntity.setAttribute('name', objectClass)
                owningEntity.setAttribute('owning-side', 'true')
                if objectClass == inverseClass:
                    owningEntity.setAttribute('alias', 'parent_' + objectClass.lower() + 's')
                else:
                    owningEntity.setAttribute('alias', objectClass.lower() + 's')
                owningEntity.setAttribute('uuid', str(uuid.uuid4()))
                owningEntityField = root.createElement('many-to-many-field')
                owningEntityField.setAttribute('name', objectClass.lower() + '_id')
                owningEntityField.setAttribute('from', objectClass.lower() + '_id')
                owningEntityField.setAttribute('to', 'internal_id')
                mme = str(uuid.uuid4())
                owningEntityField.setAttribute('uuid', mme)
                MMES.append(mme)
                #Append
                owningEntity.appendChild(owningEntityField)
                Relation.appendChild(owningEntity)

                # Inverse
                inverseEntity = root.createElement('many-to-many-entity')
                inverseEntity.setAttribute('name', inverseClass)
                inverseEntity.setAttribute('owning-side', 'false')
                inverseEntity.setAttribute('alias', inverseClass.lower() + 's')
                inverseEntity.setAttribute('uuid', str(uuid.uuid4()))
                inverseEntityField = root.createElement('many-to-many-field')
                inverseEntityField.setAttribute('name', inverseClass.lower() + '_id')
                inverseEntityField.setAttribute('from', inverseClass.lower() + '_id')
                inverseEntityField.setAttribute('to', 'internal_id')
                mme = str(uuid.uuid4())
                inverseEntityField.setAttribute('uuid', mme)
                MMES.append(mme)
                #Append
                inverseEntity.appendChild(inverseEntityField)
                Relation.appendChild(inverseEntity)

                #Add to Region
                region.appendChild(Relation)

    if len(root.getElementsByTagName('visual-data')) > 0:
        visualData = root.getElementsByTagName('visual-data')[0]
    else:
        visualData = root.createElement('visual-data')

    for mme in MMES:
        split = root.createElement('many-to-many-association-entity')
        split.setAttribute('uuid', mme)
        split.setAttribute('split', "1")
        visualData.appendChild(split)
        
    project.appendChild(visualData)