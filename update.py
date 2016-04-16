import re

str_capital = re.compile(r'[A-Z]')
num_capital = re.compile(r'\d[A-Z]')
num_single = re.compile(r'^\d+[a-z]?$')
num_comma = re.compile(r'^\d+[a-z]?(\s?,\s?\d+[a-z]?)*$')
num_semicolon = re.compile(r'^\d+[a-z]?(\s?;\s?\d+[a-z]?)*$')
num_dash = re.compile(r'^\d+\s?-\s?\d+$')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)



def update_housenumber(num_string):

    '''
    A function that updates a house number
    '''
    
    # Standardize each letter suffix into lowercase
    if num_capital.search(num_string):
        num_string = num_string.lower()
    
    # Process an input string that expresses a single housenumber
    if num_single.search(num_string):
        housenumber_list = [num_string]
    
    # Process an input string that expresses range
    elif num_dash.search(num_string):
        pair = num_string.replace(" ","").split("-")
        lower_bound = int(pair[0])
        upper_bound = int(pair[1]) + 1
        housenumber_list = range(lower_bound, upper_bound)
        housenumber_list = map(str, housenumber_list)  # For consistent format
    
    # Process an input string that uses comma listing
    elif num_comma.search(num_string):
        housenumber_list = num_string.replace(" ","").split(",")
    
    # Process an input string that uses semicolon listing
    elif num_semicolon.search(num_string):
        housenumber_list = num_string.replace(" ","").split(";")
    
    else:
        housenumber_list = [num_string]
    
    housenumber_list.sort()
    
    return housenumber_list



def update_street(street_name):
    
    '''
    A function that fixes abbreviated street types
    '''

    mapping = { "St": "Street",
                "Rd" : "Road" }
    
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            correct_type = mapping[street_type]
            street_name = street_type_re.sub(correct_type, street_name)
    
    return street_name



def update_amenity_type(string):

    '''
    A function that updates an amenity type
    '''

    if str_capital.search(string):
        string = string.lower()
    return string


