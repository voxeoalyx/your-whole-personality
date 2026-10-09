entity\_id

uuid

required

The entity to base the trending insight on.

start\_date

date

required

The date to begin pulling trending data for.

end\_date

date

The date to end pulling trending data for.

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
     --url 'https://api.qloo.com/trends/entity?page=1&take=20' \
     --header 'accept: application/json'
```

Click `Try It!` to start a request and see the response here! Or choose an example:

application/json
