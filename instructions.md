# Annotation Guidelines - Contrast Set Review

Thank you for helping annotate this data. These guidelines explain what you will see and how to label each original-perturbed pair.

## 1. What Is This Data?

This dataset contains contrast sets for question answering over Volkswagen annual reports. A contrast set starts from a canonical QA item and creates a modified version of either the question or the supporting text.

The generator creates two kinds of variants:

- Preserve variants: the semantics are unchanged.
- Alter variants: the semantics are flipped or meaningfully changed.

This follows the same general idea used in contrast-set evaluation: controlled perturbations are applied to an original statement/text, and each perturbation is judged by its semantic effect, namely whether it preserves or alters the original meaning.

The goal is to evaluate whether QA models are robust to small but important changes. Preserving variants test whether a model gives consistent answers when the wording changes but the meaning stays the same. Altering variants test whether a model changes its answer when the meaning actually changes.

These annotations will support two robustness metrics:

- Consistency: whether the model behaves the same for semantically equivalent inputs.
- Faithfulness: whether the model changes its prediction when the meaning-relevant facts change.

## 2. What You Will See

For each item, you will see:

- Question type: the category of the original QA item, such as `insight`, `lookup_text`.
- Perturbation type: an internal label describing how the text was modified.
- Original text: the text before modification.
- Perturbed text: the modified version.

Question type and perturbation type are shown only for context. You should make your decision by comparing the original text and the perturbed text.

Your task is not to judge grammar, fluency, or writing quality. Your task is to judge whether the perturbed text preserves or alters the meaning of the original text.

## 3. Annotation Labels

Choose one of three labels:

- Preserve
- Alter
- Not Sure

## 4. Preserve

Choose Preserve when the perturbed text keeps the same factual meaning as the original text.

In a Preserve case, the wording may change, but the core semantic content remains the same. The important entities, numbers, dates, comparisons, directions, calculations, and polarity should remain unchanged.

Preserve means:

- The same fact is expressed in different words.
- The same quantity is written in a different format.
- The sentence structure changes, but the claim is unchanged.
- Extra neutral wording is added, but it does not change the original claim.
- A model should give the same answer from the original and perturbed text.

Examples:

- `The Volkswagen Group consists of two divisions.`
  -> `Two divisions comprise the Volkswagen Group.`

- `The company reported EUR 3 million.`
  -> `The company reported 3,000,000 euros.`

- `Sales revenue was on a level with the prior year.`
  -> `Sales revenue was comparable to the previous year.`

- `The new Passat, the new Tiguan and the ID.7 Tourer were successfully launched on the market.`
  -> `The marketplace saw the successful introduction of the new Passat, the new Tiguan, and the ID.7 Tourer.`

These are Preserve cases because the meaning is unchanged.

## 5. Alter

Choose Alter when the perturbed text changes the factual meaning of the original text.

In an Alter case, an answer-relevant or meaning-relevant fact is changed. The perturbed text no longer says the same thing as the original text. It may contradict the original, flip the direction of the claim, or replace a key fact with a different one.

Alter means:

- A number, amount, percentage, or unit changes.
- A date, year, period, or quarter changes.
- An entity, market, model, division, or region changes.
- A comparison changes, such as highest to lowest.
- The direction changes, such as increased to decreased.
- The polarity changes, such as success to failure or profit to loss.
- A calculation changes, such as addition to subtraction.
- A model should give a different answer from the perturbed text than from the original text.

Examples:

- `The Volkswagen Group consists of two divisions.`
  -> `The Volkswagen Group consists of three divisions.`

- `The models were successfully launched on the market.`
  -> `The models failed to launch on the market.`

- `Deliveries increased by 40.8%.`
  -> `Deliveries declined by 40.8%.`

- `The ratio is calculated by adding the R&D ratio and the capex to sales revenue ratio.`
  -> `The ratio is calculated by subtracting the capex to sales revenue ratio from the R&D ratio.`

These are Alter cases because the meaning is changed.

## 6. Not Sure

Choose Not Sure only when you cannot confidently decide between Preserve and Alter.

Use Not Sure when:

- The original text is unclear.
- The perturbed text is incomplete or too garbled to interpret.
- The change is genuinely ambiguous.
- You can reasonably argue for both Preserve and Alter.
- There is not enough information in the shown text to decide whether the meaning changed.

Do not choose Not Sure only because the sentence is awkward, technical, or unfamiliar. If the meaning is still recoverable, choose Preserve or Alter.

## 7. Decision Rule

Use this question as your main test:

Did the perturbation only change the wording, or did it change the meaning?

- If only the wording changed, choose Preserve.
- If the factual meaning changed, choose Alter.
- If you genuinely cannot tell, choose Not Sure.

Another useful test:

Would a QA model be expected to give the same answer for the original and perturbed text?

- Same answer expected: Preserve.
- Different answer expected: Alter.
- Cannot determine: Not Sure.

## 8. Practical Tips

1. Read the original text first.
2. Identify the main factual claim.
3. Read the perturbed text.
4. Check whether the same factual claim is still true.
5. Ignore grammar, fluency, and style.
6. Pay special attention to numbers, dates, entities, comparisons, direction words, and negation.
7. If one important meaning-relevant fact changes, choose Alter.
8. If the same meaning is expressed differently, choose Preserve.
9. Use Not Sure only when the meaning cannot be confidently determined.

## 9. Summary

Preserve means semantics unchanged.

Alter means semantics flipped or meaningfully changed.

Not Sure means the semantic effect cannot be confidently judged.
