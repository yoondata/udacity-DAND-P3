import xml.etree.cElementTree as ET
import audit as AD
import transform as TF
import codecs
import json
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
lower_colon_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid" ]

k_multilevel_one = set()
k_multilevel_two = set()



class AutoVivification(dict):
    '''
    Define a new class for the deeper nested structure 
    of the output dictionary ("document" in MongoDB)

    [ Implementation of perl's autovivification feature ]
    
    Reference:
    http://stackoverflow.com/questions/2600790/multiple-levels-of-collection-defaultdict-in-python
    '''
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value



def shape_element(element):
    doc = AutoVivification()
    if element.tag in ["node", "way", "relation"]:
        
        # Identify the category
        doc["category"] = element.tag
        
        # Check if the "pos" key should be created
        if "lat" in element.keys():
            doc["pos"] = [0, 0]
        
        # Process same-level attributes
        for attrib_name in element.keys():
            if attrib_name in CREATED:
                doc["created"][attrib_name] = element.attrib[attrib_name]
            elif (attrib_name == "lat"):
                doc["pos"][0] = float( element.attrib[attrib_name] )
            elif (attrib_name == "lon"):
                doc["pos"][1] = float( element.attrib[attrib_name] )                
            else:
                doc[attrib_name] = element.attrib[attrib_name]
        
        # Process lower-level "tag" attributes
        if (element.find("tag") != None):
            
            # Make modifications
            for tag in element.iter("tag"):
                key = tag.attrib["k"]
                value = tag.attrib["v"]
                if not problemchars.search(key):
                    
                    # Clean and shape data related to address
                    if key.startswith("addr:"):
                        addr_key, addr_val = TF.transform_address_k_v(key, value)
                        doc["address"][addr_key] = addr_val

					# Clean and shape data related to amenity
                    elif key.startswith("amenity"):
                        amenity_key, amenity_val = TF.transform_amenity_k_v(key, value)
                        if (key == "amenity:disused"):
                            doc["disused"][amenity_key] = amenity_val
                        else:
                            doc[amenity_key] = amenity_val
                    
                    
                    ########################################################
                    #####  (Add more field-specific transformations!)  #####
                    ########################################################
                    
                    
                    # Shape other data into default model
                    elif lower.search(key):
                        if key in k_multilevel_one:
                            doc[key]["basic_info"] = value
                        else:
                            doc[key] = value                    
                    elif lower_colon.search(key):
                        key_upper = key.split(":")[0]
                        key_lower = key.split(":")[1]
                        if key in k_multilevel_two:
                            doc[key_upper][key_lower]["basic_info"] = value
                        else:
                            doc[key_upper][key_lower] = value
                    elif lower_colon_colon.search(key):
                        key_upper = key.split(":")[0]
                        key_middle = key.split(":")[1]
                        key_lower = key.split(":")[2]
                        doc[key_upper][key_middle][key_lower] = value
        
        # Process lower-level "nd" attributes
        if (element.find("nd") != None):
            doc["node_refs"] = []
            for nd in element.iter("nd"):
                ref_num = nd.attrib["ref"]
                doc["node_refs"].append(ref_num)
        
        # Process lower-level "member" attributes
        if (element.find("member") != None):
            doc["member"] = []
            for mb in element.iter("member"):
                mb_dict = {}
                mb_dict["ref"] = mb.attrib["ref"]
                mb_dict["type"] = mb.attrib["type"]
                # Some members do not have a value for "role"
                if (mb.attrib["role"] != ""):
                    mb_dict["role"] = mb.attrib["role"]
                doc["member"].append(mb_dict)
        
        return doc
    
    else:
        return None



def make_dict(osm_file):
    '''
    A function that turns an OSM file into a list of Python dictionaries
    '''

    global k_multilevel_one
    global k_multilevel_two
    k_multilevel_one, k_multilevel_two = AD.classify_k_multilevel(osm_file)

    events = ET.iterparse(osm_file, events=("start",))
    _, root = next(events)  # Grabbing the root element
    
    data = []
    for _, element in events:
        el = shape_element(element)
        if el:
            data.append(el)
            root.clear()  # Freeing up memory by clearing the root element
    
    return data



def process_map(file_in, pretty=False):
    '''
    A function that turns and saves an OSM file into a JSON file
    '''
    
    file_out = "{0}.json".format(file_in)
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")


