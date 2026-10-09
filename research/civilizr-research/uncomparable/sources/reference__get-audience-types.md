filter.parents.types

string

enum

Filter by a comma-separated list of parental entity types.

urn:audience:communities, urn:audience:global\_issues, urn:audience:hobbies\_and\_interests, urn:audience:investing\_interests, urn:audience:leisure, urn:audience:life\_stage, urn:audience:lifestyle\_preferences\_beliefs, urn:audience:political\_preferences, urn:audience:professional\_area, urn:audience:spending\_habits

Show 10 enum values

page

integer

>= 1

The page number of results to return. This is equivalent to take + offset and is the recommended approach for most use cases.

take

integer

1 to 50

Defaults to 20

The number of results to return. Default is `20`. The maximum allowed is `50`.
To retrieve additional results, use the `page` parameter to access the next page of results. This is the recommended approach for pagination.
For specific cases, the `offset` parameter can be used with `take` to skip a set number of results.

# 200 Successful Operation

400 Bad Request

500 Internal Server Error

```
curl --request GET \
     --url 'https://api.qloo.com/v2/audiences/types?take=20' \
     --header 'accept: application/json'
```

Click `Try It!` to start a request and see the response here! Or choose an example:

application/json
