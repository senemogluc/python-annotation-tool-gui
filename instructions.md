# Annotation Guidelines - Contrast Set Review

You will compare an original text with a perturbed text and decide whether the perturbation preserves or changes the meaning.

This data contains contrast sets for Volkswagen annual-report QA. The generator creates two types of variants:

- Preserve: semantics unchanged.
- Alter: semantics flipped or meaningfully changed.

Your annotation will help evaluate model robustness through Consistency and Faithfulness.

## What You See

- Question type: shown only for context.
- Perturbation type: shown only for context.
- Original text: text before modification.
- Perturbed text: modified text.

Do not judge grammar or fluency for its own sake — judge meaning, except for the Malformed label below, which exists specifically for text that is too broken to read as a sentence.

## Labels

### Preserve

Choose Preserve if the perturbed text has the same factual meaning as the original.

The wording may change, but the key facts stay the same: entities, numbers, dates, comparisons, direction, calculation, and polarity.

Examples:

- `The Volkswagen Group consists of two divisions.` -> `Two divisions comprise the Volkswagen Group.`

- `The company reported EUR 3 million.` -> `The company reported 3,000,000 euros.`

- `Sales revenue was on a level with the prior year.` -> `Sales revenue was comparable to the previous year.`

### Alter

Choose Alter if the perturbed text changes the factual meaning of the original.

This includes changes in numbers, dates, entities, comparison, direction, calculation, or polarity.

Examples:

- `The Volkswagen Group consists of two divisions.` -> `The Volkswagen Group consists of three divisions.`

- `The models were successfully launched.` -> `The models failed to launch.`

- `Deliveries increased by 40.8%.`
  -> `Deliveries declined by 40.8%.`

### Malformed

Choose Malformed when the perturbed text should not be evaluated as a normal perturbation because there is an output-generation problem.

Use Malformed if:

- the perturbed text is identical to the original text,
- the perturbed text contains model reasoning or generation artifacts, such as `<think>`, chain-of-thought content, prompt fragments, or meta-comments,
- the perturbed text is truncated, garbled, or grammatically broken to the point that it cannot be treated as a valid sentence.

Examples:

- `revenue increas by the the mill lion`
- `Deliveries were up 40 the vehicles.`
- `<think> I need to change the number but preserve the meaning... </think>`
- the original and perturbed texts are exactly the same

### Not Sure

Choose Not Sure only when the perturbed text is well-formed enough to evaluate, but you cannot confidently decide whether the meaning is Preserved or Altered.

Use Not Sure when the sentence is understandable, but the semantic relation between the original and perturbed text is unclear, ambiguous, or difficult to judge.

Do not choose Not Sure only because the sentence is awkward, technical, or hard to read. If the problem is caused by a generation error, such as identical output, chain-of-thought content, truncation, or severe grammatical corruption, choose Malformed instead.

## Decision Rule

Ask yourself:

Is the perturbed text itself well-formed? If not: Malformed.

If it is well-formed, did the perturbation only change the wording, or did it change the meaning?

- Same meaning: Preserve.
- Different meaning: Alter.
- Cannot determine: Not Sure.
