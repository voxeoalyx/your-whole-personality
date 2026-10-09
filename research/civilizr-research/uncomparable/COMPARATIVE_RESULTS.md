# A/B/C comparison

A and B were frozen before Qloo requests. Every method uses the same property fact record in `properties.json`. B's predicted cultural leads are hypotheses, not documented relationships. C adds Qloo observations; it does not turn them into property facts. Assessment is unblinded and provisional. Search expansion and supplementary lead validation occurred after the baseline freeze.

## Herbert and Katherine Jacobs House (Jacobs I)

**A — conventional facts.** A 1930s house in Madison using mixed natural materials and open living spaces.

**B — provenance plus LLM.** Its significance is a domestic design experiment in affordability and spatial efficiency, not simply the prestige of Wright’s name. That distinguishes it from a bespoke landscape retreat. Likely discovery leads include Taliesin, organic architecture, American craft, Japanese design, and Wright’s books; these are predictable leads to verify, not evidence of a buyer audience.

**C — same facts plus Qloo.** No direct cultural profile: the correctly resolved house was rejected as an Insights interest. Its Usonian tag returned a flat brand vector. Wright author recommends mainly technology brands; using it would erase the distinction from Fallingwater.

**Increment over B.** None demonstrated. B gives the more faithful property explanation.

Source facts: [primary source](https://franklloydwright.org/site/herbert-jacobs-house/); [primary source](https://www.loc.gov/item/2016631046/).

Qloo evidence: `05_houses/jacobs_brands`, `03_pilot/usonian`, `08_fixed/usonian_fixed`, `03_pilot/wright`.

## Fallingwater

**A — conventional facts.** A 1930s Pennsylvania retreat with sandstone, glass and concrete terraces above a stream.

**B — provenance plus LLM.** The central appeal is an unusually direct spatial relationship to landscape and water. Unlike Jacobs I, its commission was a bespoke retreat rather than an affordable-house prototype. Site experience and conservation are stronger explanations than a generic luxury label. Predictable cultural leads include Taliesin, the Guggenheim, MoMA, Japanese landscape aesthetics and other Wright sites.

**C — same facts plus Qloo.** Search found the actual Mill Run property after increasing take to 100, but brands and books both rejected it as an interest. Wright author is usable but identical for both Wright properties by construction.

**Increment over B.** None demonstrated for this property. Do not label a shared author proxy a Fallingwater fingerprint.

Source facts: [primary source](https://franklloydwright.org/site/fallingwater/); [primary source](https://fallingwater.org/history/the-kaufmanns-fallingwater/designing-fallingwater/).

Qloo evidence: `04_resolution/fallingwater_retry`, `06_domains/fallingwater_brands`, `06_domains/fallingwater_book`.

## Edith Farnsworth House

**A — conventional facts.** A 1951 Illinois riverside retreat with an elevated steel structure and extensive glazing.

**B — provenance plus LLM.** Radical visual continuity and structural reduction explain its importance; extensive glass and a floodplain also complicate everyday occupation. Likely associations include Bauhaus, Knoll, the Barcelona Pavilion, and minimalist art. These obvious modernist relationships are already available without an affinity API.

**C — same facts plus Qloo.** KNOLL, Arper and Eames Office lead the home-goods recommendations. Cultural places include Crown Hall and Wrightwood 659. The latter has independently documented architecture programming and an Ando-designed space; it is a plausible discovery lead. Chicago-area destinations dominate. The Mies person input fails and International Style is flat.

**Increment over B.** Modest editorial discovery; familiar modernist links and regional geography do not outperform B on architectural explanation. Wrightwood 659 was absent from B but has not been validated as an incremental user benefit.

Source facts: [primary source](https://edithfarnsworthhouse.org/history/).

Qloo evidence: `07_design/farnsworth_design`, `06_domains/farnsworth_place`, `06_domains/farnsworth_destination`, `06_domains/mies_brands`, `08_fixed/international_fixed`.

## Eames House / Case Study House No. 8

**A — conventional facts.** A 1949 California residence and studio using industrial components in a hillside setting.

**B — provenance plus LLM.** Standardized construction and a densely personal collection of objects coexist here. Its appeal is warmer and more experimental than a generic steel-and-glass minimalism label suggests. Herman Miller, Vitra, MoMA, Powers of Ten, film/photography and Case Study architecture are predictable leads. A recommendation of those names alone adds little.

**C — same facts plus Qloo.** The input is Eames Foundation at the verified house address. On the shared home-goods panel it favors Hem, Fritz Hansen, Eames Office, VITRA and KNOLL. Friedman Benda is the second cultural-place recommendation and stays second for the related Ray-author input and half-place panel. A primary exhibition record corroborates an Eames furniture connection. Books are largely contemporary poetry; their relevance to the house is unverified.

**Increment over B.** Strongest narrow discovery case: one corroborated, stable lead absent from B. Not proof an LLM could not find it. The brand-vector correlation with Ray author is negative, so house/design-author proxies are not interchangeable.

Source facts: [primary source](https://eamesfoundation.org/work/case-study-house-8/).

Qloo evidence: `08_fixed/eames_fixed`, `06_domains/eames_place`, `08_fixed/ray_places_fixed`, `09_checks/eames_places_half`, `06_domains/eames_book`.

## Gamble House

**A — conventional facts.** A 1908 Pasadena house with detailed woodwork, art glass and coordinated furnishings.

**B — provenance plus LLM.** Integrated craft and the relationship between building and furniture explain its appeal better than a size comparison. Likely links include Stickley, Arts and Crafts collections, woodworking and Japanese-influenced design. The Huntington is an obvious research institution given its Greene and Greene material. These are thematic hypotheses, not a premium estimate.

**C — same facts plus Qloo.** Unrestricted brands favor Bring A Trailer, Ford Bronco and Canoo, whereas shared home-goods candidates favor Eames Office and KNOLL. Place recommendations favor Pasadena institutions and gardens, including the already predicted Huntington. Books and the film probe do not establish Arts and Crafts specificity. The Craftsman tag is flat; a Stickley brand search yields no result.

**Increment over B.** No convincing improvement in explaining integrated craft. Automotive collecting is a hypothesis with no verified association; a documented Back to the Future celebration does not validate a brand-affinity mechanism. The candidate panel is biased toward modernist home goods.

Source facts: [primary source](https://gamblehouse.org/).

Qloo evidence: `05_houses/gamble_brands`, `08_fixed/gamble_fixed`, `06_domains/gamble_place`, `09_checks/gamble_movie`, `10_panel_audit/stickley`.

## Cedar Hill / Frederick Douglass National Historic Site

**A — conventional facts.** A mid-19th-century Washington house enlarged to 21 rooms.

**B — provenance plus LLM.** Its significance principally follows Douglass’s life, writing and political history rather than a canonical architect. Literature, abolitionist history and African American history institutions are predictable connections. The distinction matters: a cultural history visitor is not thereby a buyer of this architectural style. No demographic or demand inference follows.

**C — same facts plus Qloo.** The historic-site input gives brands such as Black Wall Street App, The Lip Bar and D’IYANU. In the shared home-goods panel Casper, Sleep Number and GE Appliances lead. This differs from the architecture museums but does not distinguish historical identity, visitor culture and building style.

**Increment over B.** No additional property-specific explanation demonstrated. Do not infer visitor or buyer demographics from brand names, or turn historic significance into a price premium.

Source facts: [primary source](https://www.nps.gov/frdo/learn/historyculture/places.htm).

Qloo evidence: `05_houses/douglass_brands`, `08_fixed/douglass_fixed`.

## McKinley Project

**A — conventional facts.** A 2015 Garland house of 1,594 square feet, two floors, three bedrooms and 2.5 baths, with documented efficient construction.

**B — provenance plus LLM.** Verified energy performance and practical domestic use are the supported differentiators. Building science, efficient appliances and sustainable construction are reasonable discovery themes; a famous-designer or collector narrative would be invented. The control tests whether Qloo can represent a home without relying on a museum or famous author.

**C — same facts plus Qloo.** No faithful house entity was found in the recorded search. A Sustainable Architecture decor tag produced the same flat recommendations as Usonian and Craftsman. It is not a validated proxy for this home’s measured energy performance.

**Increment over B.** No usable control fingerprint. This prevents the intended unusual-versus-ordinary comparison; missingness is not a negative cultural score.

Source facts: [primary source](https://www7.eere.energy.gov/buildings/residential/exploredenh/sites/default/files/2024-06/2015hiawinner_carlfranklin_100515.pdf).

Qloo evidence: `02_discovery/mckinley_house`, `06_domains/sustainable_brands`, `08_fixed/sustainable_fixed`.
