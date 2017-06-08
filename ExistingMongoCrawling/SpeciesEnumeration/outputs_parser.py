#This program parses the outputs that were created by species_enumerator.py
# Run it in the same directory as species_enumerator (not in the output directory)

import os
import pprint
import json

# We start off with a list of databases, collections, and filenames that we have

database_list = ('cep_hash', 'cep_legacy', 'cep_mol_test', 'cep_perf', 'cep_perf_legacy', 'cep_pred', 'cep_syn')
collection_list = { 'cep_hash' : ('calculation', 'molecule'),
                     'cep_legacy' : ('calculation', 'file_audit_trail', 'molecule'),
                     'cep_mol_test' : ('calculation', 'file_audit_trail', 'molecular_linkage', 'molecule', 'reactive_molecule'),
                     'cep_perf' : ('bitcounts', 'calculation', 'hash_0', 'hash_1', 'hash_2', 'hash_3', 'hash_4', 'hash_5', 
                                   'hash_6', 'hash_7', 'hash_8', 'hash_9', 'hash_10', 'hash_11', 'hash_12', 'hash_13', 
                                   'hash_14', 'hash_15', 'hash_16', 'hash_17', 'hash_18', 'hash_19', 'hash_20', 'hash_21',
                                   'hash_22', 'hash_23', 'hash_24', 'hashes', 'inline', 'molecule', 'trying'),
                     'cep_perf_legacy' : ('calculation', 'molecule', 'tt'),
                     'cep_pred' : ('calculation', 'file_audit_trail', 'molecular_linkage', 'molecule', 'reactive_molecule', 'tt'),
                     'cep_syn' : ('calculation', 'file_audit_trail', 'molecular_linkage', 'molecule', 'reactive_molecule', 'tt') }

filename_list = os.listdir('output/')





# first I will want to take each collection and get the union of all species types to create a sort of super-species
# this super species will serve to represent that collection, since every single subspecies can be represented in that form,
# perhaps missing some fields. 

def file_creator(filename):
    return open('output/' + filename, 'r')


# note that this uses eval() -- NOT good style in general, but here it's okay because the input
# files were created via pprint and are therefore all standardized.
# (note: pprint is also not safe in general, since here we are working with nested data types, 
# however, I am nesting only tuples and dicts, and the data is all very simple, so using eval(pprint()) 
# is acceptable here. 
def file_parser(file_object):
    file_object.readline()
    data = file_object.read().strip()
    parsed_data = eval(data) 
    return parsed_data


def filename_matches_checker(db_name, coll_name, filename):
    return filename.startswith(db_name + '.' + coll_name + '.species') and filename.count('enumerat') == 0


# At this point in the program we need to settle on a data storage format. We choose to store the nested fields in the format
# <outer>.<inner>(. etc)
# This lets us keep track of layer depth but also use Python sets to do efficient merging, etc. 
# This method converts from the pprint nested tuple-dict format to this period-based format
# Note: we use {} to keep track of when we have a dict that is _always_ empty
def convert_to_set(nested_tuple_dict):
    result = set()
    for item in nested_tuple_dict:
        if isinstance(item, str):
            if item != '_cls': #these fields are useless
                result.add(item)
        else: #in this case item is a dict with one key-value pair
            dict_key = list(item.keys())[0]
            subfields = convert_to_set(item[dict_key])
            for x in subfields:
                result.add(dict_key + '.' + x)
            if len(subfields) == 0:
                result.add(dict_key + '.{}')
    return result


def delete_useless_empty_dicts(fields_set):
    sometimes_empty_dicts = []
    for x in fields_set:
        if x.endswith('{}'):
            sometimes_empty_dicts.append(x[0:-2])

    to_be_discarded = []
    for x in fields_set:
        for y in sometimes_empty_dicts:
            if x.startswith(y) and not x.endswith('{}'):
                to_be_discarded.append(y + '{}')

    for x in to_be_discarded:
        fields_set.discard(x)

    return fields_set



# only thing of note here is that we need to get rid of the .{} for dicts if there exist nonempty instances of them at all
def species_generator(db_name, coll_name):
    global filename_list
    filename_matches = [x for x in filename_list if filename_matches_checker(db_name, coll_name, x)]
    extracted_species_old_format = [file_parser(file_creator(filename)) for filename in filename_matches]
    extracted_species = [convert_to_set(x) for x in extracted_species_old_format]
    super_species = set() 
    for x in extracted_species:
        super_species.update(x)

    super_species = delete_useless_empty_dicts(super_species)
    return extracted_species, super_species
    


def determine_missing_fields(super_species_set, species_set):
    # if there is an empty dict in the superset there's gotta be one in the normalset,
    # if there is an empty dict in the normalset AND in superset, difference is empty, 
    # if empty dict only in the normalset then difference is just those elements of the superset
    # either way, we can just discard the empty dicts in the normalsets and take set difference

    # actually the above logic doesn't seem to hold (?)
#    to_be_discarded = []
#    for x in species_set:
#        if x.endswith('{}'):
#            to_be_discarded.append(x)
#
#    for x in to_be_discarded:
#        species_set.discard(x)

    return super_species_set - species_set


def determine_intersection(extracted_species):
    result = extracted_species[0]
    for species in extracted_species:
        result = result & species
    return result




# Then, for each db.coll, output as the following:
# <superspecies>
# <species 1>: missing the following fields: []
# <species 2>: missing the following fields: [a, b, c.d, e.f.g, h]
# This representation will be ordered by the number of fields missing, in increasing order

total_aggregated_super_species = set()



for db_name in database_list:
    for coll_name in collection_list[db_name]:
        extracted_species, super_species = species_generator(db_name, coll_name)
        total_aggregated_super_species = total_aggregated_super_species | super_species
        missing_fields_by_species = [determine_missing_fields(super_species, normal_species) for normal_species in extracted_species]
        missing_fields_by_species.sort(key=len)
        
        outfile = open('parsed-output/' + db_name + '.' + coll_name + '.txt', 'w')
        outfile.write('Super species for ' + db_name + '.' + coll_name + ': ')
        json.dump( sorted(list(super_species)), outfile, indent = "\t" )
        for species in missing_fields_by_species:
            outfile.write('\n\n')
            outfile.write('A single species (fields missing):')
            if len(species) == 0:
                outfile.write('\n\t(no fields missing) -- the super species actually exists!')
            else:
                json.dump( sorted(list(species)), outfile, indent = "\t" )

        outfile.write('\n\n\n')
        outfile.write('-----Fields present in every species:-----')
        json.dump( sorted(list(determine_intersection(extracted_species))), outfile, indent = "\t" )
        outfile.write('\n\n')
        outfile.write('--------------------------------------------------------------------------------------------')
        outfile.write('\n\n\n')

        outfile.close()



total_aggregated_super_species = delete_useless_empty_dicts(total_aggregated_super_species)
outfile = open('parsed-output/total_aggregated_super_species.txt', 'w')
outfile.write('Total aggregated super species: ')
json.dump( sorted(list(total_aggregated_super_species)), outfile, indent = "\t" )
outfile.write('\n\n\n')
outfile.close()
