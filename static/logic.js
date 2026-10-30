export function predictability(predictions, answers) {
  const reactions = predictions.map(p => answers[p.id]);
  const yes = reactions.filter(x => x === 'yes').length;
  const no = reactions.filter(x => x === 'no').length;
  const unknown = reactions.filter(x => x === 'unknown').length;
  return { yes, no, unknown, known: yes + no, total: predictions.length,
    answered: yes + no + unknown, rate: yes + no ? yes / (yes + no) : null };
}

export function verdict(predictions, answers, sensitivity) {
  const stats = predictability(predictions, answers);
  const winner = sensitivity?.status === 'complete' ? sensitivity.winner : null;
  let result;
  if (stats.known < 3) result = { id: 'evidence', title: 'INSUFFICIENT EVIDENCE. EXCESSIVE CONFIDENCE.', roast: 'The algorithm prepared a speech. You supplied a shrug.', why: 'Fewer than three familiar guesses: too little evidence to call you predictable.' };
  else if (winner) result = { id: 'hijack', title: 'ONE INTEREST TO RULE THEM ALL.', roast: `${winner.name} has requested sole custody of the recommendations.`, why: `${winner.name} caused the clearest ranking change when removed. That is about the model, not your personality.` };
  else if (stats.rate >= .75) result = { id: 'legible', title: 'THE ALGORITHM HAS SEEN YOUR TYPE BEFORE.', roast: 'A few guesses and it is already acting like your oldest friend.', why: 'You confirmed at least three quarters of the guesses you recognized. A small sample. A very smug algorithm.' };
  else if (stats.rate <= .25) result = { id: 'inconvenience', title: 'STATISTICAL INCONVENIENCE.', roast: 'The model would like to speak to your manager.', why: 'You rejected at least three quarters of the guesses you recognized. Its shortlist missed the mark.' };
  else result = { id: 'multitudes', title: 'YOU CONTAIN MULTITUDES.', roast: 'It found a pattern. Then you ruined it by being a person.', why: 'Your familiar guesses got a mixed reception. The algorithm has some work to do.' };
  return { ...result, stats, winner, sensitivityStatus: sensitivity?.status || 'incomplete' };
}

export function summary(v, source) {
  const accuracy = v.stats.known ? `${v.stats.yes}/${v.stats.known} familiar guesses confirmed` : 'No familiar guesses to score';
  const influence = v.influence ? [v.influence.label, ...v.influence.entries.map(e => `${e.label}: ${e.names}`), v.influence.qualification, 'Ranking changes on these fixed shortlists, not shares of personality.'].join('\n') :
    v.winner ? 'Strongest ranking influence: ' + v.winner.name : v.sensitivityStatus === 'complete' ? 'No clear single influence.' : 'Ranking influence: insufficient evidence.';
  return `YOUR WHOLE PERSONALITY\n${v.title}\n${v.roast}\n${accuracy}; ${v.stats.unknown} not tried.\n${influence}\n${v.identity ? `IDENTITY REALITY CHECK: ${v.identity.title}\nOUR RANKINGS: ${v.identity.model}\nI SAY: ${v.identity.self}\nSelf-report, not a psychological measurement.\n` : ''}${source === 'recorded' ? 'Recorded Qloo demo round — not predictions from my own interests.\n' : ''}A tiny taste test, not a personality diagnosis.\nYour turn. Try Your Whole Personality.`;
}

// Descriptive Act III findings. The original strict sensitivity and Act IV score
// remain untouched. This tolerance only absorbs floating-point noise in ties.
const tied = (a, b) => Math.abs(a - b) <= 1e-12;
const finite = value => typeof value === 'number' && Number.isFinite(value);
const leaders = (rows, value) => {
  const ordered = rows.filter(r => finite(value(r))).slice().sort((a, b) => value(b) - value(a));
  return ordered.length && value(ordered[0]) > 1e-12 ? ordered.filter(r => tied(value(r), value(ordered[0]))) : [];
};

export function influenceReveal(game) {
  const s = game.sensitivity;
  if (!s) return { kind: 'pending' };
  const rows = game.interests.map(e => ({ ...s.rows.find(r => r.id === e.id), id: e.id, name: e.label || e.name }));
  const domains = game.domains.map(domain => {
    const measured = rows.filter(r => finite(r.domains?.[domain]));
    return { domain, measured, missing: rows.filter(r => !measured.includes(r)),
      leaders: measured.length >= 2 ? leaders(measured, r => r.domains[domain]) : [] };
  });
  const comparable = domains.filter(d => d.measured.length >= 2);
  const allMeans = rows.length >= 2 && rows.every(r => finite(r.value));
  const tops = allMeans ? leaders(rows, r => r.value) : [];
  const leader = tops.length === 1 ? tops[0] : null;
  const halvesAvailable = rows.every(r => [0, 1].every(h => finite(r.halves?.[h])));
  const halfLeaders = [0, 1].map(h => leaders(rows, r => r.halves?.[h]));
  const stable = Boolean(leader && halvesAvailable && halfLeaders.every(group => group.length === 1 && group[0].id === leader.id));
  const ordered = rows.filter(r => finite(r.value)).sort((a, b) => b.value - a.value);
  const reasons = [];
  if (s.status !== 'complete') reasons.push('incomplete_strict_check');
  if (allMeans) {
    if (ordered[0].value <= .10) reasons.push('below_magnitude');
    if (ordered[0].value <= 2 * ordered[1].value) reasons.push('below_double_runner_up');
    if (!halvesAvailable) reasons.push('halves_unavailable');
    else if (!stable) reasons.push('half_leaders_differ_or_tie');
  }
  const commonLeader = comparable.length && comparable[0].leaders.some(r => comparable.every(d => d.leaders.some(x => x.id === r.id)));
  const split = domains.length > 1 && domains.every(d => d.missing.length === 0 && d.leaders.length) && !commonLeader;
  let kind, detail;
  if (s.status === 'complete' && s.winner) { kind = 'dominant'; detail = 'strict'; }
  else if (!comparable.length) { kind = 'insufficient'; detail = 'no_comparable_domain'; }
  else if (!allMeans || domains.some(d => d.missing.length)) { kind = 'distributed'; detail = 'partial'; }
  else if (split) { kind = 'distributed'; detail = 'domain_specific'; }
  else if (!tops.length) { kind = 'distributed'; detail = 'unchanged'; }
  else if (!leader) { kind = 'distributed'; detail = 'tied'; }
  else if (halvesAvailable && !stable) { kind = 'distributed'; detail = 'unstable'; }
  else { kind = 'largest'; detail = 'qualified'; }
  return { kind, detail, leader, contenders: tops.length > 1 ? tops : ordered.slice(0, 2), domains,
    halfLeaders, stable, reasons, strict: s,
    focus: s.winner?.id || leader?.id || comparable[0]?.leaders[0]?.id || rows[0]?.id };
}

const joinNames = rows => rows.map(r => r.name).join(' / ');
export function influenceCopy(reveal, labels) {
  const { kind, detail, leader, contenders = [], domains = [], halfLeaders = [], reasons = [] } = reveal;
  const names = joinNames(contenders);
  let title, text;
  if (kind === 'dominant') {
    title = 'WE FOUND THE MAIN CHARACTER.';
    text = `${reveal.strict.winner.name} causes the biggest ranking shake-up, clears the strict dominance test, and leads in both half-panel checks. It has taken charge of these shortlists.`;
  } else if (kind === 'largest') {
    title = 'THE LOUDEST VOICE IN THE ROOM.';
    text = `${leader.name} moves these rankings most on average. ${contenders[1]?.value > 0 ? contenders[1].name + ' still has a say.' : 'The other removals leave the rank order unchanged.'} Largest measured influence, without clear dominance.`;
    if (reasons.includes('below_magnitude')) text += ' Even the largest change is small on the strict test’s scale.';
    if (reasons.includes('halves_unavailable')) text += ' Some half-panel checks are unavailable, so stability is unverified.';
  } else if (detail === 'domain_specific') {
    title = 'DIFFERENT DEPARTMENTS. DIFFERENT BOSSES.';
    text = domains.map(d => `${joinNames(d.leaders)} moves ${labels[d.domain] || d.domain} most`).join('; ') + '.';
    if (leader) text += ` ${leader.name} has the largest average, but the category leaders disagree. This mix has a power-sharing arrangement.`;
  } else if (detail === 'unstable') {
    title = 'AN ENSEMBLE CAST. WITH OPINIONS.';
    text = `${leader.name} has the largest average on the full panels, but the half-panel checks disagree or tie. First half: ${joinNames(halfLeaders[0]) || 'no ranking movement'}. Second half: ${joinNames(halfLeaders[1]) || 'no ranking movement'}. The spotlight depends on which recommendations we examine.`;
  } else if (detail === 'tied') {
    title = 'SHARED CUSTODY OF THE ALGORITHM.';
    text = `${names} tie for the largest average ranking change. The evidence calls for an ensemble credit.`;
  } else if (detail === 'unchanged') {
    title = 'THE MIX HOLDS ITS GROUND.';
    text = `${joinNames(domains[0].measured)}: removing any one leaves these rankings in the same order. No solo shake-up on these panels; this does not mean those interests have no effect elsewhere.`;
  } else if (detail === 'partial') {
    title = 'SOME DEPARTMENTS HAVE RECEIPTS.';
    text = domains.filter(d => d.measured.length >= 2).map(d => `${labels[d.domain] || d.domain}: ${d.leaders.length ? joinNames(d.leaders) + ' moves the ranking most' : joinNames(d.measured) + ' leave the order unchanged'} among the measured interests`).join('. ') + '. Some comparisons are missing or flat, so there is no overall ranking of the interests.';
  } else {
    title = 'THE EVIDENCE HAS GAPS.';
    text = `We could not compare at least two of ${joinNames(reveal.strict.rows)} within the same category. Missing, too-short or flat panels prevent an influence comparison. The available receipts are below.`;
  }
  return { title, text };
}

// One presentation object for Act IV, copied text, and the PNG. This enriches
// the result without feeding a descriptive leader back into verdict scoring.
export function finalResult(game, answers, labels = {}) {
  const reveal = influenceReveal(game);
  return { ...verdict(game.predictions, answers, game.sensitivity), influence: influenceSummary(reveal, labels) };
}

export function influenceSummary(reveal, labels = {}) {
  const { kind, detail, leader, contenders = [], domains = [], halfLeaders = [], reasons = [] } = reveal;
  let label, qualification, entries = [];
  if (kind === 'pending') return { label:'INFLUENCE CHECKS PENDING', entries, qualification:'The removal comparisons are still running.', explanation:'The removal comparisons are still running.' };
  if (kind === 'dominant') {
    label = 'DOMINANT ON THESE PANELS';
    entries = [{ label:'Strict winner', names:reveal.strict.winner.name }];
    qualification = 'Passed the strict dominance test, including both half-panel checks.';
  } else if (kind === 'largest') {
    label = 'LARGEST WITHOUT CLEAR DOMINANCE';
    entries = [{ label:'Largest average', names:leader.name }];
    if (contenders[1]?.value > 0) entries.push({ label:'Next-largest', names:contenders[1].name });
    qualification = 'Largest measured ranking change; the strict dominance test was not met.';
    if (reasons.includes('below_magnitude')) qualification += ' Even the largest change is small on the strict scale.';
    if (reasons.includes('halves_unavailable')) qualification += ' Half-panel stability is unverified.';
  } else if (detail === 'domain_specific') {
    label = 'DIFFERENT CATEGORY LEADERS';
    entries = domains.map(d => ({ label:labels[d.domain] || d.domain, names:joinNames(d.leaders) }));
    if (leader) entries.push({ label:'Largest average', names:leader.name });
    qualification = 'Different interests move each category most. No clear overall dominance.';
  } else if (detail === 'unstable') {
    label = 'SHARED INFLUENCE';
    entries = [{ label:'Largest average', names:leader.name }, ...halfLeaders.map((rows, h) => ({ label:`Half-panel ${h + 1} lead`, names:joinNames(rows) || 'No ranking movement' }))];
    qualification = 'The lead changes or ties across half-panel checks. No clear dominance.';
  } else if (detail === 'tied') {
    label = 'TIED LARGEST INFLUENCES';
    entries = [{ label:'Equal largest average', names:joinNames(contenders) }];
    qualification = 'These interests tie on the full panels. No single dominant influence.';
  } else if (detail === 'unchanged') {
    label = 'THE MIX HOLDS ITS GROUND';
    entries = [{ label:'Interests checked', names:joinNames(domains[0].measured) }];
    qualification = 'Removing any one leaves the rank order unchanged on these panels. Effects elsewhere remain unknown.';
  } else if (detail === 'partial') {
    label = 'PARTIAL INFLUENCE EVIDENCE';
    for (const d of domains) {
      const domain = labels[d.domain] || d.domain;
      if (d.measured.length >= 2) entries.push({ label:`${domain} · ${d.leaders.length ? 'largest among measured' : 'unchanged among measured'}`, names:joinNames(d.leaders.length ? d.leaders : d.measured) });
      if (d.missing.length) entries.push({ label:`${domain} · unavailable`, names:joinNames(d.missing) });
    }
    qualification = 'Only available comparisons are credited. No overall ranking or dominance claim.';
  } else {
    label = 'INSUFFICIENT INFLUENCE EVIDENCE';
    entries = [{ label:'Interests checked', names:joinNames(reveal.strict.rows) }];
    qualification = 'No category supports an influence comparison of at least two interests.';
  }
  return { label, entries, qualification, explanation:influenceCopy(reveal, labels).text };
}

// Canvas layout is measured before drawing, so long typed labels and all their
// qualifications survive export. Normal cards remain 1080 × 1350; long receipts
// can grow vertically instead of clipping evidence or shrinking it beyond use.
export function wrapLines(text, maxWidth, measure) {
  const lines = [];
  let line = '';
  for (const word of text.trim().split(/\s+/)) {
    if (line && measure(line + ' ' + word) <= maxWidth) { line += ' ' + word; continue; }
    if (line) { lines.push(line); line = ''; }
    for (const character of word) {
      if (line && measure(line + character) > maxWidth) { lines.push(line); line = ''; }
      line += character;
    }
  }
  if (line) lines.push(line);
  return lines;
}

export function shareCardLayout(v, sourceLabel, measure) {
  const blocks = [], rules = [];
  let y = 70;
  const add = (text, font, lineHeight, gap = 0) => {
    const lines = wrapLines(text, 940, text => measure(text, font));
    blocks.push({ lines, font, lineHeight, x:70, y });
    y += lines.length * lineHeight + gap;
  };
  const rule = () => { rules.push(y); y += 25; };
  add('YOUR WHOLE PERSONALITY', 'bold 22px Arial', 28, 5);
  add(sourceLabel, 'bold 18px Arial', 24, 24);
  rule();
  add(v.title, '84px Impact, Haettenschweiler, Arial Black, sans-serif', 90, 22);
  add(v.roast, 'italic 30px Georgia', 40, 30);
  rule();
  add('PREDICTABILITY', 'bold 18px Arial', 24, 9);
  const accuracy = v.stats.known ? `${Math.round(v.stats.rate * 100)}%` : '—';
  add(`${accuracy}  ·  ${v.stats.yes}/${v.stats.known} familiar guesses confirmed`, 'bold 28px Arial', 36, 3);
  add(`${v.stats.unknown} not tried · ${v.stats.total} shown`, '22px Arial', 30, 20);
  rule();
  add(v.influence.label, 'bold 18px Arial', 25, 10);
  for (const e of v.influence.entries) add(`${e.label}: ${e.names}`, 'bold 28px Arial', 36, 8);
  add(v.influence.qualification, '22px Arial', 30, 10);
  add('Ranking changes on these fixed shortlists, not shares of personality.', '22px Arial', 30, 24);
  rule();
  if (v.identity) {
    add('IDENTITY REALITY CHECK: ' + v.identity.title, 'bold 28px Arial', 36, 10);
    add('OUR RANKINGS: ' + v.identity.model, '22px Arial', 30, 8);
    add('I SAY: ' + v.identity.self, 'bold 28px Arial', 36, 8);
    add('Self-report, not a psychological measurement.', '22px Arial', 30, 20);
    rule();
  }
  y = Math.max(1160, y);
  add('YOUR FRIENDS ARE NEXT.  ↗', 'bold 28px Arial', 36, 20);
  add('A tiny taste test, not a personality diagnosis. Powered by Qloo.', '20px Arial', 28);
  return { width:1080, height:Math.max(1350, y + 60), blocks, rules };
}

// Use tied rank ranges and the entire fixed panel. Never turn missing entities,
// score-only changes, or arbitrary ordering within a tie into a dramatic swap.
function ranked(rows) {
  const sorted = rows.slice().sort((a, b) => b.score - a.score || a.id.localeCompare(b.id));
  return sorted.map((row, i) => {
    const start = sorted.findIndex(x => x.score === row.score) + 1;
    let end = i + 1;
    while (end < sorted.length && sorted[end].score === row.score) end++;
    return { ...row, start, end, rank: start === end ? `#${start}` : `tied #${start}–${end}` };
  });
}

export function recommendationChanges(base = [], reduced = []) {
  const valid = rows => rows.every(r => r.id && finite(r.score)) && new Set(rows.map(r => r.id)).size === rows.length;
  const ids = new Set(base.map(r => r.id));
  const panel = reduced.filter(r => ids.has(r.id));
  if (base.length < 4 || !valid(base) || !valid(panel) || panel.length !== base.length ||
      new Set(base.map(r => r.score)).size < 2 || new Set(panel.map(r => r.score)).size < 2) return { available: false };
  const before = ranked(base), after = ranked(panel);
  const beforeMap = new Map(before.map(r => [r.id, r]));
  const changes = after.map(row => ({ id: row.id, name: row.name, before: beforeMap.get(row.id), after: row }));
  const entrants = changes.filter(x => x.before.start > 3 && x.after.start <= 3);
  const exits = changes.filter(x => x.before.start <= 3 && x.after.start > 3);
  const moves = changes.filter(x => x.after.end < x.before.start || x.after.start > x.before.end)
    .sort((a, b) => Math.abs(b.before.start - b.after.start) - Math.abs(a.before.start - a.after.start));
  const changed = changes.some(x => x.before.start !== x.after.start || x.before.end !== x.after.end);
  return { available: true, before: before.filter(x => x.start <= 3), after: after.filter(x => x.start <= 3), entrants, exits, moves, changed };
}
