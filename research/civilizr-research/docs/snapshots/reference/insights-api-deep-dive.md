Qloo's Insights API helps uncover the underlying factors that shape human preferences, offering cultural intelligence about how people relate to different entities like brands, artists, destinations, and more. It draws from billions of signals to deliver nuanced, taste-based insights that reflect real-world behavior and affinities.

This Deep Dive is designed to help users explore the full capabilities of the Insights API, emphasizing how different parameters shape results. It allows you to view and test the complete set of supported parameters directly on this page, making it easier to explore functionality in context and understand how different inputs impact responses.

# Helpful Resources

- Need to understand how current parameters map to legacy fields? Visit the [Parameter Reference.](parameters.md)
- Want to know which parameters are valid for each entity type (like Actor, Destination, or Brand)? See the [Entity Type Parameter Guide](available-parameters-by-entity-type.md).

filter.type

string

enum

required

Filter by the category of entity to return (urn:entity:place).

urn:entity:artisturn:entity:bookurn:entity:brandurn:entity:destinationurn:entity:movieurn:entity:personurn:entity:placeurn:entity:podcasturn:entity:tv\_showurn:entity:videogameurn:heatmap

Show 11 enum values

bias.trends

string

enum

The level of impact a trending entity has on the results. Supported by select categories only.

lowofflowmediumhigh

Allowed:

`off``low``medium``high`

diversify.by

string

enum

Limits results to a set number of high-affinity entities per geographic group. Set to `properties.geocode.city` to diversify by city, or to `properties.geocode.metro` to diversify by metro area.
Groups are ranked based on the highest-affinity entity within them. Entities within each group are ordered by individual affinity.

properties.geocode.cityproperties.geocode.cityproperties.geocode.metro

Allowed:

`properties.geocode.city``properties.geocode.metro`

diversify.take

integer

>= 1

Sets the maximum number of results to return per city when using "diversify.by": "properties.geocode.city". For example, if set to 5, the response will include up to 5 entities with the highest affinities in each city.

feature.explainability

boolean

When set to `true`, the response includes explainability metadata for each recommendation and for the overall result set. Default is `false`.
**Per recommendation**: Each result includes a `query.explainability` section showing which input entities (e.g., `signal.interests.entities`) contributed to the recommendation, with normalized scores between 0 and 1. Entities scoring >= 0.1 are always included; lower-impact entities may be omitted to reduce response size.
**Aggregate impact**: The top-level `query.explainability` object shows the average influence of each input entity across top-N result subsets (e.g., top 3, 5, 10, all).
**Note**: If explainability cannot be computed, a warning is returned under `query.explainability.warning`, but results are still returned as normal.

truetruefalse

filter.address

string

length >= 1

Filter by address using a partial string match. Supports comma-separated terms.

filter.content\_rating

string

enum

Filter by a comma-separated list of content ratings based on the MPAA film rating system, which determines suitability for various audiences.

PGGPGPG-13RNC-17

Allowed:

`G``PG``PG-13``R``NC-17`

filter.date\_of\_birth.max

date

Filter by the most recent date of birth desired for the queried person.

filter.date\_of\_birth.min

date

Filter by the earliest date of birth desired for the queried person.

filter.date\_of\_death.max

date

Filter by the most recent date of death desired for the queried person.

filter.date\_of\_death.min

date

Filter by the earliest date of death desired for the queried person.

filter.exclude.tags

string

Exclude entities associated with a comma-separated list of tags.

operator.exclude.tags

string

enum

Specifies how multiple `filter.exclude.tags` values are combined in the query. Use "union" (equivalent to a logical "or") to exclude results that contain at least one of the specified tags, or "intersection" (equivalent to a logical "and") to exclude only results that contain all specified tags. The default is "union".

unionunionintersection

Allowed:

`union``intersection`

filter.exists

string

enum

Filter results to include only entities that contain the specified property. For example, use `properties.image` to return only entities that include an image URL, or `properties.description` to filter for entities with a text description.

properties.imageproperties.imageproperties.description

Allowed:

`properties.image``properties.description`

filter.external.exists

string

Filter by a comma-separated list of external keys. (`resy`\|`michelin`\|`tablet`).

operator.filter.external.exists

string

enum

Specifies how multiple `filter.external.exists` values are combined in the query. Use "union" (equivalent to a logical "or") to return results that match at least one of the specified external keys (e.g., resy, michelin, or tablet), or "intersection" (equivalent to a logical "and") to return only results that match all specified external keys. The default is "union".

unionunionintersection

Allowed:

`union``intersection`

filter.external.resy.count.max

integer

>= 0

Filter places to include only those with a Resy rating count less than or equal to the specified maximum. Applies only to entities with `filter.type` of `urn:entity:place`.

filter.external.resy.count.min

integer

>= 0

Filter places to include only those with a Resy rating count greater than or equal to the specified minimum. Applies only to entities with `filter.type` of `urn:entity:place`.

filter.external.resy.party\_size.max

integer

>= 1

Filter by the maximum supported party size required for a Point of Interest.

filter.external.resy.party\_size.min

integer

>= 1

Filter by the minimum supported party size required for a Point of Interest.

filter.external.resy.rating.max

number

0 to 5

Filter places to include only those with a Resy rating less than or equal to the specified maximum (1-5 scale). Applies only to entities with `filter.type` of `urn:entity:place`.

filter.external.resy.rating.min

number

0 to 5

Filter places to include only those with a Resy rating greater than or equal to the specified minimum (1-5 scale). Applies only to entities with `filter.type` of `urn:entity:place`.

filter.external.tripadvisor.rating.count.min

integer

>= 0

Filter places to include only those with a Tripadvisor review count greater than or equal to the specified minimum. This filter only applies to entities with `filter.type` of `urn:entity:place`.

filter.external.tripadvisor.rating.count.max

integer

>= 0

Filter places to include only those with a Tripadvisor review count less than or equal to the specified maximum. This filter only applies to entities with `filter.type` of `urn:entity:place`.

filter.external.tripadvisor.rating.max

number

0 to 5

Filter places to include only those with a Tripadvisor rating less than or equal to the specified maximum. This filter only applies to entities with `filter.type` of `urn:entity:place`.

filter.external.tripadvisor.rating.min

number

0 to 5

Filter places to include only those with a Tripadvisor rating greater than or equal to the specified minimum. This filter only applies to entities with `filter.type` of `urn:entity:place`.

filter.finale\_year.max

integer

Filter by the latest desired year for the final season of a TV show.

filter.finale\_year.min

integer

Filter by the earliest desired year for the final season of a TV show.

filter.gender

string

Filter results to align with a specific gender identity. Used to personalize output based on known or inferred gender preferences.

filter.geocode.admin1\_region

string

Filter by `properties.geocode.admin1_region`. Exact match (usually state).

filter.geocode.admin2\_region

string

Filter by `properties.geocode.admin2_region`. Exact match (often county or borough).

filter.geocode.country\_code

string

Filter by `properties.geocode.country_code`. Exact match (two-letter country code).

filter.geocode.name

string

Filter by `properties.geocode.name`. Exact match (usually city or town name).

filter.hotel\_class.max

integer

1 to 5

Filter by the maximum desired hotel class (1-5, inclusive).

filter.hotel\_class.min

integer

1 to 5

Filter by the minimum desired hotel class (1-5, inclusive).

filter.hours

string

enum

Filter by the day of the week the Point of Interest must be open (Monday, Tuesday, etc.).

mondaymondaytuesdaywednesdaythursdayfridaysaturdaysunday

Allowed:

`monday``tuesday``wednesday``thursday``friday``saturday``sunday`

filter.latest\_known\_year.max

integer

Filter by a certain maximum year that shows were released or updated.

filter.latest\_known\_year.min

integer

Filter by a certain minimum year that shows were released or updated.

filter.location

string

Used to filter by a WKT `POINT`, `POLYGON`, `MULTIPOLYGON` or a single Qloo ID for a named `urn:entity:locality`. WKT is formatted as X then Y, therefore longitude is first (`POINT(-73.99823 40.722668)`). If a Qloo ID or WKT `POLYGON` is passed, `filter.location.radius` will create a fuzzy boundary when set to a value > 0.

filter.exclude.location

string

Exclude results that fall within a specific location, defined by either a WKT `POINT`, `POLYGON`, `MULTIPOLYGON`, or a Qloo ID for a named `urn:entity:locality`. WKT is formatted with longitude first (e.g., `POINT(-73.99823 40.722668)`). When using a locality ID or a WKT `POLYGON`, setting `filter.location.radius` to a value > 0 creates a fuzzy exclusion boundary.

filter.location.query

A query used to search for one or more named `urn:entity:locality` Qloo IDs for filtering requests, equivalent to passing the same Locality Qloo ID(s) into `filter.location`.

- For **GET requests**: Provide a single locality query as a string.
- For **POST requests**:

  - You can still send a single locality as a string.
  - Or you can send an array of locality names to query multiple localities at once. When multiple localities are provided, their geographic shapes are merged, and the system returns results with the highest affinities across the combined area.

Locality queries are fuzzy-matched and case-insensitive. Examples include `New York City`, `Garden City`, `New York`, `Los Angeles`, `Lower East Side`, and AKAs like `The Big Apple`. When a single locality is supplied, the response JSON includes `query.locality.signal` with the matched Qloo entity. If multiple are supplied, this field is omitted. By default, the API includes a tuning that also captures nearby entities just outside the official boundaries of the locality. To turn this off and limit results strictly to within the locality, set `filter.location.radius=0`. If no localities are found, the API returns a 400 error.

string

array

filter.exclude.location.query

A query used to exclude results based on one or more named `urn:entity:locality` Qloo IDs, resolved from fuzzy-matched locality names. This is equivalent to passing the resolved Locality Qloo ID(s) into `filter.exclude.location`.

- For **GET requests**: Provide a single locality query as a string. - For **POST requests**:

  - You can still send a single locality as a string.
  - Or send an array of locality names to exclude multiple areas at once. When multiple localities are provided, their geographic shapes are merged, and the system excludes results from across the combined area.

Locality queries are case-insensitive and support common AKAs (e.g., `The Big Apple` for New York). When a single locality is supplied, the response includes `query.locality.exclude.signal` with the matched Qloo entity. If multiple are supplied, this field is omitted. If no localities are matched, the API returns a 400 error.

string

array

filter.location.geohash

string

Filter by a geohash. Geohashes are generated using the Python package pygeohash with a precision of 12 characters. This parameter returns all POIs that start with the specified geohash. For example, supplying `dr5rs` would allow returning the geohash `dr5rsjk4sr2w`.

filter.exclude.location.geohash

string

Exclude all entities whose geohash starts with the specified prefix. Geohashes are generated using the Python package `pygeohash` with a precision of 12 characters. For example, supplying `dr5rs` would exclude any result whose geohash begins with `dr5rs`, such as `dr5rsjk4sr2w`.

filter.location.radius

integer

Filter by the radius (in meters) when also supplying `filter.location` or `filter.location.query`.
When this parameter is **not provided**, the API applies a default tuning that slightly expands the locality boundary to include nearby entities outside its official shape.
To **disable** this behavior and strictly limit results to entities inside the defined locality boundary, set `filter.location.radius=0`.

filter.parents.types

string

enum

Filter by a comma-separated list of parental entity types.

urn:audience:communitiesurn:audience:communitiesurn:audience:global\_issuesurn:audience:hobbies\_and\_interestsurn:audience:investing\_interestsurn:audience:leisureurn:audience:life\_stageurn:audience:lifestyle\_preferences\_beliefsurn:audience:political\_preferencesurn:audience:professional\_areaurn:audience:spending\_habits

Show 10 enum values

filter.popularity.max

number

0 to 1

Filter by the maximum popularity percentile a Point of Interest must have (float, between 0 and 1; closer to 1 indicates higher popularity, e.g., 0.98 for the 98th percentile).

filter.popularity.min

number

0 to 1

Filter by the minimum popularity percentile required for a Point of Interest (float, between 0 and 1; closer to 1 indicates higher popularity, e.g., 0.98 for the 98th percentile).

filter.price\_level.max

integer

1 to 4

Filter by the maximum price level a restaurant can have. Accepts values 1-4, where higher numbers indicate more expensive restaurants (similar to dollar signs). Applies only to Places entities.

filter.price\_level.min

integer

1 to 4

Filter by the minimum price level a restaurant can have. Accepts values 1-4, where higher numbers indicate more expensive restaurants (similar to dollar signs). Applies only to Places entities.

filter.price\_range.max

integer

0 to 1000000

Filter by the maximum price in the desired hotel price range. Accepts an integer between 0 and 1,000,000. Applies only to Places entities.

filter.price\_range.min

integer

0 to 1000000

Filter by the minimum price in the desired hotel price range. Accepts an integer between 0 and 1,000,000. Applies only to Places entities.

filter.properties.business\_rating.max

float

enum

Filter by the highest desired business rating.

312345

Allowed:

`1``2``3``4``5`

filter.properties.business\_rating.min

float

enum

Filter by the lowest desired business rating.

312345

Allowed:

`1``2``3``4``5`

filter.publication\_year.max

number

Filter by the latest desired year of initial publication for the work.

filter.publication\_year.min

number

Filter by the earliest desired year of initial publication for the work.

filter.rating.max

number

0 to 5

Filter by the maximum Qloo rating a Point of Interest must have (float, between 0 and 5).

filter.rating.min

number

0 to 5

Filter by the minimum Qloo rating a Point of Interest must have (float, between 0 and 5).

filter.references\_brand

array of strings

Filter by a comma-separated list of brand entity IDs. Use this to narrow down place recommendations to specific brands. For example, to include only Walmart stores, pass the Walmart brand ID. Each ID must match exactly.

filter.references\_brand
ADD string

filter.release\_country

array of strings

Filter by a list of countries where a movie or TV show was originally released.

filter.release\_country
ADD string

operator.filter.release\_country

string

enum

Specifies how multiple \`filter.release\_country\`\` values are combined in the query. Use "union" (equivalent to a logical "or") to return results that match at least one of the specified countries, or "intersection" (equivalent to a logical "and") to return only results that match all specified countries. The default is "union".

unionintersectionunion

Allowed:

`intersection``union`

filter.release\_date.max

date

Filter by the latest desired release date.

filter.release\_date.min

date

Filter by the earliest desired release date.

filter.release\_year.max

integer

Filter by the latest desired release year.

filter.release\_year.min

integer

Filter by the earliest desired release year.

filter.results.entities

string

Filter by a comma-separated list of entity IDs. Often used to assess the affinity of an entity towards input.

filter.results.entities.query

Search for one or more entities by name to use as filters. - For **GET requests**: Provide a single entity name as a string. - For **POST requests**: You can provide a single name or an array of names.

string

array

filter.exclude.entities

string

A comma-separated list of entity IDs to remove from the results.

filter.exclude.entities.query

array

This parameter can only be supplied when using POST HTTP method, since it requires JSON encoded body. The value for `filter.exclude.entities.query` is a JSON array with objects containing the `name` and `address` properties. For a fuzzier search, just include an array of strings. When supplied, it overwrites the `filter.exclude.entities` object with resolved entity IDs. The response will contain a path `query.entities.exclude`, with partial Qloo entities that were matched by the query. If no entities are found, the API will throw a `400` error.

filter.exclude.entities.query
ADD

filter.results.tags

array of strings

Filter by a comma-separated list of tag IDs. Often used to assess the affinity of a tag towards input.

filter.results.tags
ADD string

filter.tags

string

Filter by a comma-separated list of tag IDs (urn:tag:genre:restaurant:Italian).

operator.filter.tags

string

enum

Specifies how multiple `filter.tags` values are combined in the query. Use "union" (equivalent to a logical "or") to return results that match at least one of the specified tags, or "intersection" (equivalent to a logical "and") to return only results that match all specified tags. The default is "union".

unionunionintersection

Allowed:

`union``intersection`

offset

integer

The number of results to skip, starting from 0. Allows arbitrary offsets but is less commonly used than `page`.

output.heatmap.boundary

string

Indicates the type of heatmap output desired: The default is geohashes. The other options are a city or a neighborhood.

page

integer

>= 1

The page number of results to return. This is equivalent to take + offset and is the recommended approach for most use cases.

signal.demographics.age

string

enum

A comma-separated list of age ranges that influence the affinity score. (24\_and\_younger | 25\_to\_29 | 30\_to\_34 | 35\_to\_44 | 45\_to\_54 | 55\_and\_older)

35\_to\_4424\_and\_younger25\_to\_2930\_to\_3435\_to\_4445\_to\_5455\_and\_older

Allowed:

`24_and_younger``25_to_29``30_to_34``35_to_44``45_to_54``55_and_older`

signal.demographics.age.weight

Specifies the extent to which results should be influenced by age-based demographic signals. Higher values increase the influence of age data; lower values reduce its impact.

number

string

signal.demographics.audiences.weight

Specifies the extent to which results should be influenced by the preferences of the selected audience. Higher values increase the influence of audience preferences; lower values reduce their impact.

number

string

signal.demographics.audiences

array of strings

A comma-separated list of audiences that influence the affinity score. Audience IDs can be retrieved via the v2/audiences search route.

signal.demographics.audiences
ADD string

signal.demographics.gender

string

enum

Influence the affinity score based on gender (male\|female).

malemalefemale

Allowed:

`male``female`

signal.demographics.gender.weight

Specifies the extent to which results should be influenced by gender-based demographic signals. Higher values increase the influence of gender data; lower values reduce its impact.

number

string

signal.interests.entities

array of strings

Allows you to supply a list of entities to influence affinity scores. For GET requests, provide a comma-separated list of entity IDs.

signal.interests.entities
ADD string

signal.interests.entities.query

array

This parameter can only be supplied when using POST HTTP method, which requires a JSON-encoded body. The value should be a JSON array of objects with 'name' and 'address' properties; supports 'resolve\_to' for specifying resolution to place, brand, or both.

signal.interests.entities.query
ADD

signal.interests.entities.weight

Specifies the extent to which results should be influenced by the relevance of entities (in-domain or cross-domain). Higher values increase the influence of entities; lower values reduce their impact.

number

string

signal.interests.tags

Allows you to supply a list of tags to influence affinity scores. You can also include a `weight` property that will indicate the strength of influence for each tag in your list.

- For GET requests: Provide a comma-separated list of tag IDs.
- For POST requests, you can either:
  - Send the same string of comma-separated values.
  - Send an array of objects with "tag" and "weight" properties, such as:
    \[
    { "tag": "urn:tag:genre:media:horror", "weight": 7 },
    { "tag": "urn:tag:genre:media:thriller", "weight": 20 }
    \]
    Weights must be greater than 0 and are relative. So, a weight of 20 means that tag will more heavily influence affinity scores than a weight of 7.

array

array

signal.interests.tags.weight

Specifies the extent to which results should be influenced by the presence of tags (taste analysis). Higher values increase the influence of tags; lower values reduce their impact.

number

string

signal.location

string

The geolocation to use for geospatial results. The value will be a WKT POINT, POLYGON or a single Qloo ID for a named urn:entity:locality to filter by. WKT is formatted as X then Y, therefore longitude is first (POINT(-73.99823 40.722668)). Unlike filter.location.radius, signal.location.radius is ignored if a Qloo ID or WKT POLYGON is passed.

signal.location.radius

integer

The optional radius (in meters), used when providing a WKT POINT. We generally recommend avoiding this parameter, as it overrides dynamic density discovery.

signal.location.query

string

A string query used to search for a named urn:entity:locality Qloo ID for geospatial results, effectively equivalent to passing the same Locality Qloo ID into signal.location. Examples of locality queries include New York City, Garden City, New York, Los Angeles, Lower East Side, and AKAs like The Big Apple. These queries are fuzzy-matched and case-insensitive. When filter.location.query is supplied, the response JSON will include query.locality.signal, which contains the partially matched Qloo entity. If no locality is found, the API will return a 400 error.

signal.location.weight

Specifies the extent to which results should be influenced by location-based signals (geospatial). Higher values increase the influence of location; lower values reduce its impact.

number

string

sort\_by

string

enum

This parameter modifies the results sorting algorithm (affinity\|distance). The distance option can only be used when \`filter.location\`\` is supplied.

affinityaffinitydistance

Allowed:

`affinity``distance`

take

integer

1 to 50

Defaults to 20

The number of results to return. Default is `20`. The maximum allowed is `50`.
To retrieve additional results, use the `page` parameter to access the next page of results. This is the recommended approach for pagination.
For specific cases, the `offset` parameter can be used with `take` to skip a set number of results.

# `` 200      Successful Operation

`` 400

Bad Request

`` 500

Internal Server Error

ShellNodeRubyPHPPython

```
xxxxxxxxxx

curl --request GET \
     --url 'https://api.qloo.com/v2/insights?filter.type=urn%3Aentity%3Aartist&take=20' \
     --header 'accept: application/json'
```

Click `Try It!` to start a request and see the response here! Or choose an example:

application/json

``200
