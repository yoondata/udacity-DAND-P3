import update as UD
import re

lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')



def transform_address_k_v(addr_k, addr_v):

	'''
	A function that transforms address-related data
	'''

	transformed_k = ""
	transformed_v = ""

    #######  Transform k  #######

    # Specific transformation
 	if addr_k.startswith("addr:substreet"):
		transformed_k = "substreet"

	# General transformation - Process input string with one colon
	elif lower_colon.search(addr_k):
		transformed_k = addr_k[5:]

	#######  Transform v  #######

	# Update a house number
	if (transformed_k == "housenumber"):
		transformed_v = UD.update_housenumber(addr_v)

	# Update a street name
	elif (transformed_k in ["street", "substreet"]):
		transformed_v = UD.update_street(addr_v)

	# Return the original
	else:
		transformed_v = addr_v

	return (transformed_k, transformed_v)



def transform_amenity_k_v(amenity_k, amenity_v):

	'''
	A function that transforms data related to amenity
	'''

	transformed_k = ""
	transformed_v = ""
    
    #######  Transform k  #######
    
	if amenity_k in ["amenity", "amenity:disused"]:
		transformed_k = "amenity"
    
    # Exception handling: Return the original for later auditing and cleaning
	else:
		transformed_k = amenity_k
    
    #######  Transform v  #######

	if amenity_k in ["amenity", "amenity:disused"]:
		transformed_v = UD.update_amenity_type(amenity_v)
    
    # Exception handling: Return the original for later auditing and cleaning
	else:
		transformed_v = amenity_v

	return (transformed_k, transformed_v)


