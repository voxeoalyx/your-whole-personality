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
  return `YOUR WHOLE PERSONALITY\n${v.title}\n${v.roast}\n${accuracy}; ${v.stats.unknown} not tried.\n${v.winner ? 'Strongest ranking influence: ' + v.winner.name : v.sensitivityStatus === 'complete' ? 'No clear single influence.' : 'Ranking influence: insufficient evidence.'}\n${source === 'recorded' ? 'Recorded Qloo demo round — not predictions from my own interests.\n' : ''}A tiny taste test, not a personality diagnosis.\nYour turn. Try Your Whole Personality.`;
}
