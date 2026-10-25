// Replay every archived starter and mixed-signal profile once, without API calls.
// Run: node tools/analyze_influence.mjs > .cache/influence-report.json
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { influenceReveal, recommendationChanges } from '../static/logic.js';

const root = new URL('../', import.meta.url);
const read = path => JSON.parse(readFileSync(new URL(path, root), 'utf8'));
export const profiles = [
  ...Object.entries(read('data/demos.json')).map(([id, game]) => ({ id, path: `data/demos.json#${id}`, game })),
  ...Array.from({length:6}, (_, i) => {
    const path = `research/prototype/activity-signals/game_${i + 1}.json`;
    return { id: `activity_${i + 1}`, path, game: read(path) };
  }),
];

export function analyze() {
  const before = {}, after = {}, details = {};
  const results = profiles.map(({id, path, game}) => {
    const s = game.sensitivity, reveal = influenceReveal(game);
    const old = s.status !== 'complete' ? 'insufficient' : s.winner ? 'dominant' : 'no_single_culprit';
    before[old] = (before[old] || 0) + 1;
    after[reveal.kind] = (after[reveal.kind] || 0) + 1;
    details[reveal.detail] = (details[reveal.detail] || 0) + 1;
    return { id, path, captured:game.generated_at, interests:game.interests.map(e => e.label || e.name),
      before:old, after:reveal.kind, detail:reveal.detail, strict_status:s.status, strict_winner:s.winner,
      strict_check_failures:reveal.reasons,
      top_runner_ratio:s.rows[1].value ? s.rows[0].value / s.rows[1].value : null,
      rows:s.rows,
      domains:reveal.domains.map(d => ({domain:d.domain, leaders:d.leaders.map(r => r.name), missing:d.missing.map(r => r.name)})),
      examples:game.interests.map(e => ({removed:e.label || e.name, domains:game.domains.map(domain => {
        const c = recommendationChanges(game.full[domain], game.ablations[e.id]?.[domain]);
        const compact = x => ({title:x.name, before:x.before.rank, after:x.after.rank});
        return { domain, available:c.available, entrants:c.entrants?.map(compact), exits:c.exits?.map(compact), moves:c.moves?.slice(0,2).map(compact) };
      })})),
    };
  });
  return { scope:'Nine archived example profiles, not a population estimate; synthetic edge cases excluded. Repeated investigator runs reuse the overthinker panel and are not counted again.',
    total:results.length, before, after, details, results };
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) console.log(JSON.stringify(analyze(), null, 2));
