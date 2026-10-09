The following query parameters are required when calling the `/v2/trending` endpoint. All must be provided and valid for the request to succeed:

- `signal.interests.entities`
- `filter.type`
- `filter.start_date`
- `filter.end_date`

signal.interests.entities

array of strings

Allows you to supply a list of entities to influence affinity scores. For GET requests, provide a comma-separated list of entity IDs.

filter.type

string

enum

required

Filter by the category of entity to return (urn:entity:place).

urn:entity:artist, urn:entity:book, urn:entity:brand, urn:entity:destination, urn:entity:movie, urn:entity:person, urn:entity:place, urn:entity:podcast, urn:entity:tv\_show, urn:entity:videogame, urn:heatmap

Show 11 enum values

filter.start\_date

date

required

Start date for the trending analysis period in ISO 8601 format (YYYY-MM-DD).

filter.end\_date

date

required

End date for the trending analysis period in ISO 8601 format (YYYY-MM-DD).

take

integer

1 to 50

Defaults to 20

The number of results to return. Default is `20`. The maximum allowed is `50`.
To retrieve additional results, use the `page` parameter to access the next page of results. This is the recommended approach for pagination.
For specific cases, the `offset` parameter can be used with `take` to skip a set number of results.

offset

integer

The number of results to skip, starting from 0. Allows arbitrary offsets but is less commonly used than `page`.

page

integer

>= 1

The page number of results to return. This is equivalent to take + offset and is the recommended approach for most use cases.

# 200 Successful Operation

400 Bad Request -- invalid parameters or missing required fields

500 Internal Server Error

```
curl --request GET \
     --url 'https://api.qloo.com/v2/trending?filter.type=urn%3Aentity%3Aartist&take=20' \
     --header 'accept: application/json'
```

Click `Try It!` to start a request and see the response here! Or choose an example:

application/json
