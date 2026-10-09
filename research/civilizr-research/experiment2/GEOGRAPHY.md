# Geographic units and limitations

Primary input is a WGS84 geodesic 32-gon with vertices 1,000 m from a frozen
center. Each has approximate area **3.121445 km²** (0.64% below a circle); 800 m
and 1,200 m variants have areas **1.997725** and **4.494881 km²**. The area formula
uses the local tangent plane; spherical corrections are negligible at this scale.
Centers, exact geometry and source paths are in `geographies.json` and
`geographies.csv`; exact request WKT is in each plan and request metadata.
Supplementary east shifts are saved as `sources/*_east200.geojson` and in plan 08.

These are comparable **central-area proxies**, not claims about whole neighborhoods,
resident catchments or physical cultural boundaries. Original locality centers can
fall in residential areas or include water; district address anchors need not be
centroids. Nearby proxies overlap. `pairwise_baselines.csv` flags pairs whose
1 km enclosing circles overlap; this conservative flag is not polygon intersection
area. Substantial unequal administrative polygons are never compared as equal units.

| Area | Center latitude | Center longitude | Center provenance |
|---|---:|---:|---|
| Winter Park | 28.598802 | -81.344205 | Reviewed Experiment 1 Qloo locality coordinate |
| College Park | 28.575605 | -81.390129 | Reviewed Experiment 1 Qloo locality coordinate |
| Audubon Park | 28.564341 | -81.340749 | Reviewed Experiment 1 Qloo locality coordinate |
| Baldwin Park | 28.569762 | -81.326678 | Reviewed Experiment 1 Qloo locality coordinate |
| Pine Hills | 28.578217 | -81.463278 | Reviewed Experiment 1 Qloo locality coordinate |
| Azalea Park | 28.539260 | -81.298197 | Reviewed Experiment 1 Qloo locality coordinate |
| Mills 50 | 28.558116 | -81.364733 | Official City district address anchor |
| Thornton Park | 28.541061 | -81.370446 | Official City district address anchor |
| City District proxy | 28.542111 | -81.379030 | Saved Qloo Orlando downtown point; district lookup failed |
| Atlanta Midtown | 33.782479 | -84.382087 | Centroid of official City neighborhood polygon |
| Atlanta Inman Park | 33.760728 | -84.356473 | Centroid of official City neighborhood polygon |
| Atlanta West End | 33.737852 | -84.423873 | Centroid of official City neighborhood polygon |

City District is the weakest label: the official listing lacks an anchor, both CBD
lookups failed, and its selected point is a downtown proxy only. We did not accept
Seattle, Little Saigon or Park Central fuzzy matches. Its overlap with Thornton
Park limits independence. The original seven plus the two neutral controls are
not a random sample of metropolitan Orlando. The added controls are selected by
hash within the City's Main Streets frame, which itself favors commercial districts.

## Authoritative boundary references

Orlando publishes [neighborhood maps](https://www.orlando.gov/Our-Government/Records-and-Documents/Map-Library/Neighborhood-Maps),
including [Audubon Park](https://gis.orlando.gov/PDF_Docs/NeighborhoodMaps/IndividualNeighborhoodMaps/AudubonPark.pdf),
[Baldwin Park](https://gis.orlando.gov/PDF_Docs/NeighborhoodMaps/IndividualNeighborhoodMaps/BaldwinPark.pdf),
[College Park](https://gis.orlando.gov/PDF_Docs/NeighborhoodMaps/IndividualNeighborhoodMaps/CollegePark.pdf)
and [Central Business District](https://gis.orlando.gov/PDF_Docs/NeighborhoodMaps/IndividualNeighborhoodMaps/CentralBusDist.pdf).
Its commercial-district maps include
[Mills 50](https://gis.orlando.gov/PDF_Docs/EconomicDevelopmentMaps/Mills50MainStreetProgram.pdf)
and [City District](https://gis.orlando.gov/PDF_Docs/EconomicDevelopmentMaps/CityDistrictMainStreetProgram.pdf).
These are authoritative reference maps, not polygons digitized or silently substituted
into this experiment. Main Street districts and residential neighborhoods differ.
No authoritative machine-readable residential neighborhood polygon was obtained
efficiently for all seven original areas, including unincorporated controls. The
equal-area fallback avoids unequal city/district scales but does not validate labels.

The official [Mills 50 listing](https://www.orlando.gov/Our-Government/Departments-Offices/Economic-Development/Business-Development/Orlando-Main-Streets/Mills-50-District-Main-Street)
and [Thornton Park listing](https://www.orlando.gov/Our-Government/Departments-Offices/Economic-Development/Business-Development/Orlando-Main-Streets/Thornton-Park-District-Main-Street)
provide the archived map coordinates used as anchors.

Atlanta's official [neighborhood GIS layer](https://gis.atlantaga.gov/dpcd/rest/services/AdministrativeArea/GeopoliticalArea/MapServer/1)
supplied actual polygons. Their reported reference areas are roughly 4.24 km²
(Midtown), 1.55 km² (Inman Park) and 2.76 km² (West End). Centers were computed
from their polygon rings and checked for containment. Original geometries and
area metadata are retained; the analysis uses equal-area buffers for cross-city
comparability. The returned last-edited fields date to 2022 and do not establish
neighborhood cultural freshness.
