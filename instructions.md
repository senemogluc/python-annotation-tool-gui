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

- `The Volkswagen Group consists of two divisions.`
  -> `Two divisions comprise the Volkswagen Group.`

- `The company reported EUR 3 million.`
  -> `The company reported 3,000,000 euros.`

- `Sales revenue was on a level with the prior year.`
  -> `Sales revenue was comparable to the previous year.`

### Alter

Choose Alter if the perturbed text changes the factual meaning of the original.

This includes changes in numbers, dates, entities, comparison, direction, calculation, or polarity.

Examples:

- `The Volkswagen Group consists of two divisions.`
  -> `The Volkswagen Group consists of three divisions.`

- `The models were successfully launched.`
  -> `The models failed to launch.`

- `Deliveries increased by 40.8%.`
  -> `Deliveries declined by 40.8%.`

### Malformed

Choose Malformed if the perturbed text itself is not a valid, well-formed sentence — it's truncated, garbled, or grammatically broken — regardless of whether you could otherwise judge its meaning.

Examples:

- `revenue increas by the the mill lion`
- `Deliveries were up 40 the vehicles.`

Not Sure remains for well-formed sentences where you simply can't tell whether meaning was preserved or altered.

### Not Sure

Choose Not Sure only if you cannot confidently decide.

Use it when the text is unclear, incomplete, ambiguous, or too garbled to interpret. Do not use it only because the sentence is awkward or technical.

## Decision Rule

Ask yourself:

Is the perturbed text itself well-formed? If not: Malformed.

If it is well-formed, did the perturbation only change the wording, or did it change the meaning?

- Same meaning: Preserve.
- Different meaning: Alter.
- Cannot determine: Not Sure.
