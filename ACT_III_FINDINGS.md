# Act III influence reveal investigation

October 24, 2026. The repeated “NO SINGLE CULPRIT” was primarily a presentation collapse: several distinct, informative outcomes shared one message. No scoring thresholds, Qloo parameters, candidate panels, recorded responses, model prompts, prediction logic or Act IV verdict rules were changed.

## Evidence inspected before implementation

The sample includes **all three recorded starter profiles** in `data/demos.json` and **all six complete mixed-signal games** in `research/prototype/activity-signals/game_1.json` through `game_6.json`. Captured October 8, these are actual archived Qloo results, not invented recommendation fixtures. They cover three entity-only taste mixes, three hobby audiences, two content tags and a five-input mix. Investigator comparison runs repeatedly reuse the overthinker panels, so they are not counted as independent games. No player reactions or private sessions were collected for this investigation.

Each profile discovers two held-out categories, normally 20 candidates each, then rescores exactly those candidates with all selected inputs and with each input removed. Every other signal and its default family weighting stays fixed. The measure compares **ranking order**, not affinity magnitude, accuracy, personal importance or causal attribution. Leave-one-out effects need not be additive; interactions and redundant signals are possible.

The unchanged strict calculation in `scoring.py` is:

1. Assign mean ranks to tied affinities. Compute `(1 − Spearman rho) / 2` within each fixed panel.
2. Average the two category distances equally. Missing scores, fewer than four candidates, or a flat rank vector give an undefined distance, never zero.
3. Split each panel into alternating halves after sorting candidate IDs; compute the two-category average independently on each half.
4. Require all interests' full and half comparisons to be defined. Name a winner only if the largest mean is **above 0.10**, **strictly greater than twice the runner-up**, and leads on **both halves**.

The half checks assess dependence on the selected candidates; they are not independent resampling or statistical confidence intervals. The full-profile candidate selection itself also makes the result panel-dependent.

## Diagnosis

All nine games had complete full and half-panel comparisons; none of these no-culprit results came from missing or flat data. All nine largest means exceeded 0.10. Eight failed the greater-than-double requirement; five of those also failed the half-panel leader check. The strict rule correctly avoids calling a modest or unstable lead dominance, but the UI treated “not dominant” as though there were no interesting comparison to report.

**Four profiles have different category leaders**, and one more has changing half-panel leaders despite the same full-panel leader in both categories. Distances are nonnegative: there is no signed cancellation. Equal averaging can nevertheless conceal which interest leads each category. Three profiles have consistent leaders that simply fall short of the double-runner requirement. There is no evidence here that lowering that requirement would establish robust dominance, so it remains intact.

| Profile / selected interests | Largest mean | Runner-up mean | Ratio | Category leaders | Strict before | Reveal after |
| --- | ---: | ---: | ---: | --- | --- | --- |
| Overthinker: Radiohead, Blue Bottle Coffee, Severance | Severance 0.382 | Radiohead 0.330 | 1.155 | Movies: Blue Bottle; games: Severance | No single culprit | Domain-specific; Severance still named as largest average |
| Comfort: Taylor Swift, Starbucks, Friends | Friends 0.355 | Taylor Swift 0.241 | 1.471 | Friends in both; half leaders Starbucks / Friends | No single culprit | Shared, candidate-sensitive; Friends named as largest average |
| Side quest: Metallica, Nike, Elden Ring | Elden Ring 0.299 | Nike 0.295 | 1.014 | TV: Metallica; movies: Elden Ring | No single culprit | Domain-specific; nearly equal aggregate effects |
| Activity 1: Radiohead, Blue Bottle, Running audience | Radiohead 0.470 | Blue Bottle 0.247 | 1.907 | Radiohead in both | No single culprit | Largest without dominance: Radiohead |
| Activity 2: Radiohead, Blue Bottle, Yoga audience | Radiohead 0.366 | Blue Bottle 0.314 | 1.168 | TV: Radiohead; movies: Blue Bottle | No single culprit | Domain-specific |
| Activity 3: Radiohead, Blue Bottle, Architecture audience | Blue Bottle 0.396 | Radiohead 0.373 | 1.061 | TV: Radiohead; movies: Blue Bottle | No single culprit | Domain-specific |
| Activity 4: Radiohead, Blue Bottle, Architecture books tag | Architecture tag 0.502 | Blue Bottle 0.291 | 1.727 | Architecture tag in both | No single culprit | Largest without dominance: Architecture tag |
| Activity 5: Radiohead, Blue Bottle, Yoga music tag | Radiohead 0.504 | Yoga music tag 0.225 | 2.242 | Radiohead in both | Dominant: Radiohead | Dominant: Radiohead |
| Activity 6: Radiohead, Blue Bottle, Architecture books tag, Running and Yoga audiences | Architecture tag 0.556 | Running audience 0.282 | 1.976 | Architecture tag in both | No single culprit | Largest without dominance: Architecture tag |

Values are rounded here, never before classification. Scores from different panels are not calibrated effect sizes and should not be compared across games. Audience removal measures cohort context; a content tag and a named favorite are different signal types.

## Before / after distribution

| Player-facing finding | Before | After |
| --- | ---: | ---: |
| Clear dominant interest | 1 / 9 | 1 / 9 |
| Largest influence without dominance | 0 / 9 | 3 / 9 |
| Shared or domain-specific influence | 0 / 9 | 5 / 9 |
| Insufficient evidence | 0 / 9 | 0 / 9 |
| Undifferentiated “NO SINGLE CULPRIT” | 8 / 9 | 0 / 9 |

Of the five shared reveals, four identify different category leaders and one identifies changing half-panel leaders. The **strict metric is still 1 winner and 8 non-winners**. This is a paired replay of nine curated profiles, not a population estimate of live-game frequency or evidence of improved player satisfaction. Missing-data outcomes are tested separately with controlled fixtures and are excluded from this distribution.

## Descriptive reveal rules

`influenceReveal` in `static/logic.js` reads the existing sensitivity object without modifying it:

- **Dominant:** only the existing complete strict winner earns this outcome.
- **Largest without dominance:** all full-panel means are comparable and one is largest; no conflicting category leaders or defined half-panel leaders. Copy explicitly disclaims dominance. Small movement and unavailable halves are qualified. No new effect-size threshold is introduced.
- **Shared / domain-specific:** different category leaders, tied means, or tied/changing half-panel leaders. Where a largest full-panel mean exists it is still named, with the disagreement explained. Valid zero movement gets “THE MIX HOLDS ITS GROUND,” not insufficient evidence.
- **Partial evidence:** stays within the shared/category-specific family and identifies leaders only among measured competitors within a category. Missing interests are named; no overall ranking is claimed. Valid full-panel means can still support a qualified largest result when only the half checks are undefined.
- **Insufficient:** no category permits comparison of at least two selected interests. Unfinished calculations keep the loading state instead.

Only a `1e-12` numerical equality tolerance is used for descriptive ties. A microscopic unique lead can be called “largest measured,” but never becomes strict dominance through this layer. Category leaders are descriptive observations, not individually validated dominant causes.

The original strict object, including domain distances, half distances and method, is included under `strict_dominance` in the visible investigator trace for both live and recorded games. The exported session retains `sensitivity` and adds `influence_reveal`. Act IV keeps its original deterministic scoring and strict-winner rule.

## Concrete receipts

Act III defaults to the relevant leading interest rather than the first pick. Every selected interest remains available through “Try without.” For each category it names entries/exits from the top three, with original and reduced ranks; both top-three lists remain expandable.

- **Remove Severance from the overthinker mix:** Kenshi rises **#17 → #1**, CrossCode **#14 → #2**, Control falls **#1 → #19**. Among movies, Lost in Translation rises **#11 → #1**, while Moon falls **#1 → #7**.
- **Remove Blue Bottle Coffee from the same mix:** Primer enters movies' top three **#4 → #2**; Gattaca leaves **#3 → #4**. This supports its category-specific credit even though Severance has the largest average across movies and games.
- **Remove Radiohead from the Running-audience mix:** The Final Table rises **#18 → #1** in TV and Black Mirror falls **#1 → #18**. Radiohead is the largest measured influence here, but its 1.907 ratio does not meet the unchanged strict rule.
- **Remove Radiohead from the Yoga-music mix:** Moon falls **#1 → #18**, Children of Men **#3 → #20**, and The Good Lie rises **#5 → #1**. This game already passed strict dominance before the UI change.

These are movements within the existing fixed panels, not newly discovered recommendations or measured preference changes. Tied positions use rank ranges; the whole tie at the third-place boundary is included. Reordering equally scored titles, changing only score magnitudes, absent candidates, duplicates, too-small panels and flat comparisons cannot manufacture a swap. When top-three membership is unchanged, genuine movements elsewhere on the panel can still be shown.

## Reproduce and verify

```sh
node tools/analyze_influence.mjs > .cache/influence-report.json
node --test tests/logic.test.js
python -m unittest discover -s tests -v
python tools/audit_repository.py --history
```

The replay script outputs per-profile original strict metrics, rule failures, domain leaders, ratios and title-level movements. It makes no API calls and does not modify archived recordings. Regression tests recompute all nine archived strict results from their underlying panels (including typed labels), exercise all four new outcome families plus partial/zero/tied/unstable cases, and check exact recorded recommendation movements. Browser checks cover the normal recorded round through Acts II–IV, switching removed interests, the original strict trace, and separate archived dominant/largest plus simulated insufficient-evidence rounds. The temporary browser fixture server does not change the app's demo data.

Validation passed: **53 application Python tests, 27 JavaScript tests and 24 archived research tests**. The index/history security scan checked 2,313 indexed files and 2,471 objects with zero findings; a separate scan of all nine changed/new files also found no credentials or forbidden patterns. No browser console errors were observed in the checked rounds. No new live Qloo/NVIDIA calls were needed. These browser checks are desktop verification, not a new real-device accessibility or player study.

## Follow-up: carry the finding into Act IV and sharing

The final screen, copied verdict and PNG now use one `influenceSummary` derived from the same Act III reveal. Category leaders retain their categories; a largest mean is explicitly qualified; tied and changing half-panel leaders are named; partial comparisons retain their scope and unavailable interests. Valid zero movement and insufficient comparisons remain distinct. Typed labels and recorded-example attribution survive sharing. The session export also includes the exact `influence_summary` displayed.

The original `verdict` function and strict winner remain unchanged. `finalResult` adds the descriptive summary without using it to choose the verdict category or calculate predictability. In particular, insufficient familiar reactions do not erase valid influence evidence, and a descriptive leader never becomes a strict winner.

The PNG measures and wraps every name and qualification before drawing. Standard cards remain 1080×1350; unusually long receipts grow vertically rather than clipping names, hiding qualifications or shrinking text excessively. A dedicated influence section also lets the HTML card wrap long labels.

Nine additional regression tests bring the JavaScript suite to **36 passing tests**. They check unchanged verdict fields across all nine archived profiles, named category/half-panel leaders, dominance qualifications, partial and zero evidence, typed labels, source attribution, and PNG layout bounds with long Unicode names.
