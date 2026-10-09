query

string

The text to search against.

types

array of strings

The category to search against.

filter.location

string

A geolocational position to base searches on. The radius expands from this point. The format should be "latitude,longitude".

filter.radius

float

0 to 100

Defaults to 10

The max distance in miles from the location to base results on. This only applies to categories with geolocation data. Default is 10 miles.

filter.exists

array of strings

Filter results by existential property check like `external.resy` or `external.michelin`

filter.tags

array of strings

Filter results by a tag

filter.rating

double

0 to 5

Filter by the lowest desired business rating.

filter.exclude.tags

array of strings

exclude entities from results with tags

filter.popularity

double

0 to 1

The minimum value of popularity an entity must have to be output.

operator.filter.tags

string

enum

Defaults to union

The operator.filter.tags parameter controls whether the API returns results matching all ("intersection") or any ("union") of the input tags.

Allowed:

`intersection` `union`

operator.filter.exclude.tags

string

enum

Defaults to union

The operator.filter.exclude.tags parameter controls whether the API returns results excluding all ("intersection") or any ("union") of the input tags.

Allowed:

`intersection` `union`

page

int32

1 to 100

Defaults to 1

The page number

take

integer

1 to 100

Defaults to 20

The number of records to return.

sort\_by

string

enum

Defaults to match

Sort results by criteria

Allowed:

`match` `distance` `popularity`

# 200 OK

# 404 No results

# 429 Rate limit exceeded

```
curl --request GET \
     --url 'https://api.qloo.com/search?filter.radius=10&operator.filter.tags=union&operator.filter.exclude.tags=union&page=1&take=20&sort_by=match' \
     --header 'accept: application/json'
```

Click `Try It!` to start a request and see the response here! Or choose an example:

application/json
