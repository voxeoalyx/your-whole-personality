# Protocol notes, recorded before the main profiles

- The official City District page has no coordinates. An unscoped Qloo CBD search
  returned other cities and was rejected. A second lookup adds Orlando coordinates
  and a five-mile search radius. That also failed (Little Saigon and Park Central,
  both rejected). Before profiling, use the saved Orlando downtown anchor coordinate
  (28.5421109, -81.3790304) with the same 1 km polygon, explicitly labeled a
  downtown anchor proxy. This does not substitute the Orlando locality polygon
  for City District, and does not claim to be the district's centroid. Its selected
  district label is weaker than the other controls; report the limitation.
- The audited brand pool has 59 eligible brands, exceeding the documented
  `take=50` limit. Before any new geographic profile, retain all 25 eligible brands
  in the independent, location-free lookup and select 24 eligible pooled brands by
  SHA-256 of `civilizr-exp2:<entity ID>`. Their union is the main fixed panel;
  retain the entire audit. This is a budget/conformance choice, not an outcome filter.
- Native tags use 12 food, 8 arts and 8 wellness categories. The arts panel includes
  several museum subcategories; a result there is not independent evidence from
  eight unrelated cultural behaviors. All tags were verified in saved API outputs.

## After the pilot / main requests

- Fixed output filters work, but do not guarantee scoring every requested item.
  Pine Hills omitted seven brands; both pilot areas omitted three tags. A direct
  missing-only query returned empty lists (tags also tested without the parent
  filter). Do not repair this by imputing zeros or dropping those IDs. Main and
  perturbation requests retain the frozen panels; only complete domain/subpanel
  profiles enter descriptive comparisons. Invalid domains cannot satisfy GO.
- Additional 200 m east shifts cover the other six Orlando proxies to meet the
  user's request to quantify each neighborhood. These are supplementary; the
  prespecified robustness gate still uses the original nine perturbations only.
- After all nine primary perturbations returned exactly identical tag scores,
  add a diagnostic for Winter Park, Mills 50 and Pine Hills using POINT plus an
  explicit 1,000 m radius (brands and tags). This is a **post-result diagnostic**,
  not a substitute for the primary test. A circle and the 32-gon differ by about
  0.6% in area, but Qloo documents different dynamic-density semantics for explicit
  point radii. Differences cannot be attributed solely to physical boundary area.
- The independent inventory is sparse at two controls (1 mapped selected-category
  venue in Pine Hills, 0 in Azalea Park). This does not establish that they have no
  businesses. Report provisional fits and a >=10-mapped-venue sensitivity subset;
  this cannot resolve the venue-baseline challenge across all nine areas.
