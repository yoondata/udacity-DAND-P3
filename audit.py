import xml.etree.cElementTree as ET
from collections import defaultdict
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
lower_colon_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')



def check_tags(file_name):
    '''
    A function that returns unique tags and their 
    respective occurrence in an XML document
    '''
    
    osm_file = open(file_name, "r")
    
    events = ET.iterparse(osm_file, events=("start",))
    _, root = next(events)  # Grabbing the root element
    
    tags = {}
    for event, elem in events:
        if (event == "start"):
            if elem.tag in tags.keys():
                tags[elem.tag] += 1
                root.clear()  # Freeing up memory by clearing the root element
            else:
                tags[elem.tag] = 1
                root.clear()  # Freeing up memory by clearing the root element
    
    osm_file.close()
    
    return tags



def check_attributes(file_name):
    '''
    A function that returns unique attribute keys for each tag
    '''
    
    osm_file = open(file_name, "r")
    
    events = ET.iterparse(osm_file, events=("start",))
    _, root = next(events)  # Grabbing the root element
    
    attrib_dict = defaultdict(set)
    for event, elem in events:
        if (event == "start"):
            for attribute_name in elem.keys():
                attrib_dict[elem.tag].add(attribute_name)
                root.clear()  # Freeing up memory by clearing the root element
    
    osm_file.close()
    
    return attrib_dict



def audit_k_v(file_name, parent_tag_list):
    '''
    A function that returns unique "k" and "v" values in a dictionary form
    '''
    
    osm_file = open(file_name, "r")
    
    events = ET.iterparse(osm_file, events=("start",))
    _, root = next(events)  # Grabbing the root element
    
    k_v_dict = {}
    for event, elem in events:
        if (event == "start"):
            if elem.tag in parent_tag_list:
                for tag in elem.iter("tag"):
                    k_val = tag.attrib["k"]
                    v_val = tag.attrib["v"]
                    if k_val not in k_v_dict.keys():
                        k_v_dict[k_val] = set()
                        k_v_dict[k_val].add(v_val)
                    else:
                        k_v_dict[k_val].add(v_val)
                root.clear()  # Freeing up memory by clearing the root element
    
    osm_file.close()
    
    return k_v_dict



def classify_k_multilevel(file_name):
    '''
    A function that classifies problem "k" values
    '''
    
    # Get the list of all unique "k" values
    all_k_v_dict = audit_k_v(file_name, ["node", "way", "relation"])
    all_k_list = all_k_v_dict.keys()
    
    # Classify "k" values according to colon inclusion
    k_lower = list()
    k_lower_colon = list()
    k_lower_colon_colon = list()
    for key in all_k_list:
        if lower.search(key):
            k_lower.append(key)
        elif lower_colon.search(key):
            k_lower_colon.append(key)
        elif lower_colon_colon.search(key):
            k_lower_colon_colon.append(key)
    
    ## Identify "k" values with no colon that appear 
    ## in other "k" values with a colon or two
    k_multilevel_one = set()
    for key_one in k_lower:
        key_single_colon = key_one + ":"
        for key_two in k_lower_colon:
            if key_two.startswith(key_single_colon):
                k_multilevel_one.add(key_one)
                break
        for key_three in k_lower_colon_colon:
            if key_three.startswith(key_single_colon):
                k_multilevel_one.add(key_one)
                break
    
    ## Identify "k" values with one colon that appear 
    ## in other "k" values with two colons
    k_multilevel_two = set()
    for key_two in k_lower_colon:
        key_double_colon = key_two + ":"
        for key_three in k_lower_colon_colon:
            if key_three.startswith(key_double_colon):
                k_multilevel_two.add(key_two)
                break
    
    return (k_multilevel_one, k_multilevel_two)


