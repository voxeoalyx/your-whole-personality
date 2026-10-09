type

string

enum

required

The category to receive trending entities within. Currently only supports urn:entity:brand, and in beta form urn:entity:tv\_show and urn:entity:movie.

urn:entity:actor, urn:entity:album, urn:entity:artist, urn:entity:author, urn:entity:book, urn:entity:brand, urn:entity:destination, urn:entity:director, urn:entity:locality, urn:entity:movie, urn:entity:person, urn:entity:place, urn:entity:podcast, urn:entity:tv\_show, urn:entity:videogame, urn:tag, urn:demographics, urn:entity:offer, urn:entity:editorial

Show 19 enum values

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

# 200 OK

# 404 No results

# 429 Rate limit exceeded

```
curl --request GET \
     --url 'https://api.qloo.com/trends/category?type=urn%3Aentity%3Aactor&page=1&take=20' \
     --header 'accept: application/json'
```

Click `Try It!` to start a request and see the response here! Or choose an example:

application/json
