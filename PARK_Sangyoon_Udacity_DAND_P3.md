# P3: Wrangling OpenStreetMap Data
### *Sangyoon Park | 16 APR 2016*



## Map Area of Choice

For this project, I chose to examine Oxford in England as it is a well-known college town. I expected that the city, being one of the oldest college towns in the world, would reveal many interesting characteristics that are not found in modern metropolitan areas. The map data was obtained from [https://mapzen.com/data/metro-extracts/](https://mapzen.com/data/metro-extracts/) on March 22, 2016. I have also consulted several OpenStreetMap Wiki pages [1-3].



## Overall Strategy and Procedure

Since the original data set is quite large (64MB), I derived a sample (1/10 of the original in size) and used it for data auditing and cleaning. Assuming the sample is representative of the original data set and its problems, I then applied the same cleaning principles and procedures to the original data set.

It would be ideal to individually audit and clean all data, but this would require unreasonably large amount of time. Hence, I chose to focus on *personally interesting* fields/variables that can benefit from *programmatic (i.e. systematic) cleaning*.

For uncleaned fields/variables, I tried to retain as much information in the original data set as possible by deploying a flexible default data model (details will follow below). With this flexible data model that (almost) fully captures information in the original data set, we can later resume our data cleaning if needed.



## Problems and Fixes

### 1. Structural Problem

After auditing the sample, it became clear that the data set has a major structural problem in its `“tag”` elements: `“tag”` elements have some `"k"` values that have both one-level and two-level appearances (e.g., `"building"`, `"building:levels"`). This makes it hard to convert the original data (in `“tag”` elements) to JSON documents as a simple key-value pair (e.g., `{ "building" : "hospital" }`) is structurally incompatible with a more nested pair (e.g., `{ "building" : { "levels" : "3" } }`). In fact, one overwrites the other when forced on conversion. The same problem is present in some lower-level `"k"` values as well (e.g., `"building:levels"`, `"building:levels:underground"`).

I resolved this problem by coding to automatically create a midlevel key called `"basic_info"` whenever the problem is detected. For instance,
```
<tag k="building" v="university" />
<tag k="building:levels" v="4" />
<tag k="building:levels:underground" v="1" />
```
would be turned into
```
{
	"building" : {
		"basic_info" : "university",
		"levels" : {
			"basic_info" : "4"
			"underground" : "1"
		}
	}
}
```
This schematization then served as the default data model for conversion into JSON.

### 2. Address

Auditing revealed that data related to address have several problems. First, house numbers were all coded in a single string format regardless of what they represent: some represented a single house number (e.g., `"304"`) while others represented a list or a range of multiple house numbers (e.g., `"315,315A,315B"`, `"25-30"`). Hence, some standardization was needed. I decided to turn each entry into a list of discrete numbers in string format. For instance, `"304"` would be turned into `["304"]`; `"315,315A,315B"` into `["315", "315A", "315B"]`; and `"25-30"` into `["25", "26", "27", "28", "29", "30"]`. I expected this transformation would help to systematically count the number of houses for a certain query.

As shown above, some house numbers bear a letter suffix. This is to denote such cases as an extra property inserted at a later date between two consecutively numbered properties [4]. But both upper- and lowercases are in use to express the letter suffix, requiring some standardization. Following what I identified as the standard practice in the UK, I decided to standardize each letter suffix into lowercase.

Finally, many street names do not follow the desired standard format (street type specified at the end). Due to context and cultural differences, however, no simple programmatic fix is possible for all such names. But abbreviations can be programmatically fixed. I found that some street names contain such abbreviations as "Rd" and "St", so I replaced them with their full spellings.

### 3. Amenity

Data related to amenity had two minor problems. First, some `"v"` values contained uppercase letters while the standard seemed using only lowercase letters (and underscores). Hence, all `"v"` values related to amenity were turned into lowercase.

Second, a `"k"` value named `"amenity:disused"` not only posed the structural problem mentioned earlier () but also deviated from the standard currently followed by OpenStreetMap. In OpenStreetMap, map features not in use are specified as `"disused"` first and then are described in detail [5]. Accordingly, we find in our data set such fields as `"disused:amenity"` and `"disused:highway"`. Hence, the same standard was applied to all entries whose `"k"` value is `"amenity:disused"`. That is,
```
<tag k="amenity:disused" v="pub" />
```
would be turned into
```
{
	"disused" : {
		"amenity" : "pub"
	}
}
```



## Data Overview

### 1. File Sizes
```
oxford_england.osm .......... 64.0MB
oxford_england.osm.json ..... 74.5MB
```

### 2. Basic Profile

#### Number of Documents
```python
db.oxford.find().count()
```
`324550`

#### Number of Nodes
```python
db.oxford.find( { "category" : "node" } ).count()
```
`273182`

#### Number of Ways
```python
db.oxford.find( { "category" : "way" } ).count()
```
`50351`

#### Number of Relations
```python
db.oxford.find( { "category" : "relation" } ).count()
```
`1017`

#### Number of Unique Users
```python
unique_users = db.oxford.distinct( "created.user" )
len(unique_users)
```
`1176`

#### Top 5 Contributing Users
```python
top_users = db.oxford.aggregate([
        { "$group" : { "_id" : "$created.user",
                       "count" : { "$sum" : 1 } } },
        { "$project" : { "proportion" : { "$divide" : [ "$count", 324550 ] } } },
        { "$sort" : { "proportion" : -1 } },
        { "$limit" : 5 }   # Getting only the top 5
    ])

for user in top_users:
    pprint.pprint(user)
```
```
{u'_id': u'Andrew Chadwick', u'proportion': 0.12107225389000154}
{u'_id': u'craigloftus', u'proportion': 0.11503620397473424}
{u'_id': u'GordonFS', u'proportion': 0.08929286704668002}
{u'_id': u'Max--', u'proportion': 0.05713141272531197}
{u'_id': u'Richard Mann', u'proportion': 0.05309813588044986}
```



## More Queries

### 1. Amenities

#### Number of Amenities
```python
db.oxford.find( { "amenity" : { "$exists" : 1 } } ).count()
```
`3682`

#### Number of Unique Amenities
```python
unique_amenities = db.oxford.distinct( "amenity" )
len(unique_amenities)
```
`124`

#### Most Numerous Amenities
```python
top_amenities = db.oxford.aggregate([
        { "$match" : { "amenity" : { "$exists" : 1 } } },
        { "$group" : { "_id" : "$amenity",
                       "count" : { "$sum" : 1 } } },
        { "$project" : { "proportion" : { "$divide" : [ "$count", 3682 ] } } },
        { "$sort" : { "proportion" : -1 } },
        { "$limit" : 10 }   # Getting only the top 10
    ])

for amenity in top_amenities:
    pprint.pprint(amenity)
```
```
{u'_id': u'parking', u'proportion': 0.20369364475828355}
{u'_id': u'bicycle_parking', u'proportion': 0.14095600217273221}
{u'_id': u'post_box', u'proportion': 0.09016838674633351}
{u'_id': u'bench', u'proportion': 0.049429657794676805}
{u'_id': u'place_of_worship', u'proportion': 0.045898967952199894}
{u'_id': u'pub', u'proportion': 0.04481260184682238}
{u'_id': u'telephone', u'proportion': 0.038565996740901685}
{u'_id': u'restaurant', u'proportion': 0.03476371537208039}
{u'_id': u'school', u'proportion': 0.031233025529603477}
{u'_id': u'cafe', u'proportion': 0.029060293318848452}
```

It is quite interesting that there are more places of worship than restaurants or cafes! Could this mean that Oxford is a highly religious city? It is also noteworthy that bicycle parking is the second most numerous amenity. This in fact agrees with our conception of Oxford as a college town.

### 2. Buildings

#### Number of Buildings
```python
db.oxford.find( { "building" : { "$exists" : 1 } } ).count()
```
`20760`

#### Level of the Highest Building
```python
highest_bldg = db.oxford.aggregate([
        { "$match" : { "building.levels.basic_info" : { "$exists" : 1 } } },
        { "$project" : { "level" : "$building.levels.basic_info" } },
        { "$sort" : { "level" : -1 } },
        { "$limit" : 1 }   # Getting only the top 1
    ])

for building in highest_bldg:
    pprint.pprint(building)
```
`{u'_id': ObjectId('570fec362054c17a26f47f42'), u'level': u'9'}`

#### Predominant Building Levels
```python
num_bldgs_level = db.oxford.find( { "building.levels.basic_info" : { "$exists" : 1 } } ).count()
most_num_level = db.oxford.aggregate([
        { "$match" : { "building.levels.basic_info" : { "$exists" : 1 } } },
        { "$group" : { "_id" : "$building.levels.basic_info",
                       "count" : { "$sum" : 1 } } },
        { "$project" : { "proportion" : { "$divide" : [ "$count", num_bldgs_level ] } } },
        { "$sort" : { "proportion" : -1 } },
        { "$limit" : 3 }   # Getting only the top 3
    ])

for level in most_num_level:
    pprint.pprint(level)
```
```
{u'_id': u'1', u'proportion': 0.47619047619047616}
{u'_id': u'2', u'proportion': 0.19327731092436976}
{u'_id': u'4', u'proportion': 0.1400560224089636}
```

The result shows that 9 is the highest building level in Oxford and one-story buildings are predominant in the city. This also agrees with our conception of Oxford as a college town.

### 3. Religion

We noted earlier that Oxford seems a religious city. Then, a natural question to ask is: What do they believe? Let's try to answer this through our data.

#### Religion in Oxford
```python
db.oxford.distinct( "religion" )
```
```
[u'christian',
 u'muslim',
 u'buddhist',
 u'jewish',
 u'spiritualist',
 u'multifaith']
```

#### Religion by Level of Representation
```python
num_doc_religion = db.oxford.find( { "religion" : { "$exists" : 1 } } ).count()
religion_by_num = db.oxford.aggregate([
        { "$match" : { "religion" : { "$exists" : 1 } } },
        { "$group" : { "_id" : "$religion",
                       "count" : { "$sum" : 1 } } },
        { "$project" : { "proportion" : { "$divide" : [ "$count", 207 ] } } },
        { "$sort" : { "proportion" : -1 } }
    ])

for faith in religion_by_num:
    pprint.pprint(faith)
```
```
{u'_id': u'christian', u'proportion': 0.9371980676328503}
{u'_id': u'muslim', u'proportion': 0.024154589371980676}
{u'_id': u'jewish', u'proportion': 0.014492753623188406}
{u'_id': u'buddhist', u'proportion': 0.014492753623188406}
{u'_id': u'multifaith', u'proportion': 0.004830917874396135}
{u'_id': u'spiritualist', u'proportion': 0.004830917874396135}
```

As expected, Christianity is the predominant religion in Oxford. But the extreme level of predominance is still quite surprising, especially considering the city's being a college town where new ideas and practices often prevail.



## Additional Ideas

It should be reminded that the cleaning that has been done is very rudimentary: the data set contains many fields/variables that were largely untouched and future endeavor is needed to audit and clean them.

In the present project, I have cleaned the data set *during* its transformation into JSON, meaning I have primarily worked with the XML format. With the transformation done, however, future cleaning endeavors should work directly with the JSON format. In particular, future endeavors should take advantage of the default data model that was used in this project to systematize their own cleaning process.

Auditing has revealed that many fields/variables suffer from ineffective schematization, so it is necessary to audit them and come up with new, more efficient labeling/classification schemes. For instance, the `"payment"` field is currently represented as follows:
```
> db.oxford.findOne( { "payment" : { "$exists" : 1 } }, { "payment" : 1, "_id" : 0 } )
```
```
{
	"payment" : {
		"credit_cards" : "yes",
		"notes" : "no",
		"coins" : "yes",
		"debit_cards" : "yes",
		"telephone_cards" : "no"
	}
}
```
As we can see, this representation of data is somewhat redundant. A better schematization would suggest the following transformation:
```
{
	"payment" : {
		"accepted" : [
			"credit_cards",
			"coins",
			"debit_cards"
		],
		"unaccepted" : [
			"notes",
			"telephone_cards"
		]
	}
}
```
Again, the transformation would be directly implemented on the JSON file.



## References

- [1] OpenStreetMap document explaining map data structure in XML: [https://wiki.openstreetmap.org/wiki/OSM_XML](https://wiki.openstreetmap.org/wiki/OSM_XML)

- [2] OpenStreetMap document explaining elements in map data: [https://wiki.openstreetmap.org/wiki/Elements](https://wiki.openstreetmap.org/wiki/Elements)

- [3] OpenStreetMap document explaining various features in map data: [https://wiki.openstreetmap.org/wiki/Map_Features](https://wiki.openstreetmap.org/wiki/Map_Features)

- [4] Document explaining the UK address elements: [http://support.qas.com/all_you_need_to_know_about_uk_address_elements_1478.htm](http://support.qas.com/all_you_need_to_know_about_uk_address_elements_1478.htm)

- [5] OpenStreetMap document explaining use of the key `"disused"`: [http://wiki.openstreetmap.org/wiki/Key:disused:](http://wiki.openstreetmap.org/wiki/Key:disused:)

