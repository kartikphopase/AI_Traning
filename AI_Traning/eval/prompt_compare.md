
# JalSanchay Prompt Comparison - Day 6

## Objective
Compare two prompt versions using the same 10 JalSanchay user questions.

## Prompt A - Basic
You are a helpful assistant. Answer the user's question about
rainwater harvesting and groundwater recharge.

## Prompt B - JalSanchay Grounded Prompt
You are JalSanchay, an AI assistant.

Answer using only the supplied CGWB knowledge records.
Do not invent rules, measurements, formulas or values.
If the records do not contain the answer, clearly say that
the available data is insufficient.

Use simple language. Return JSON containing:
- answer
- confidence
- follow_up

## Test Questions

1. How much rainwater can a rooftop collect?
2. What is the purpose of a first-flush system?
3. How do I estimate rainwater storage capacity?
4. Which roofing materials are suitable for rainwater harvesting?
5. What is the recommended downpipe size?
6. What is the current groundwater level at my exact plot in Kopargaon?
7. What type of filter can be used for rooftop rainwater harvesting?
8. How much water should be stored per person during the scarcity period?
9. What is the purpose of gutters in rooftop rainwater harvesting?
10. Which artificial groundwater recharge method is suitable for my area?

## Evaluation Criteria

Score each response from 0 to 2:

- Factual correctness: 0-2
- Grounding in CGWB records: 0-2
- Correct JSON format: 0-2
- Appropriate handling of missing information: 0-2

Maximum score per question: 8

## Comparison Results

| Question | Prompt A Score / 8 | Prompt B Score / 8 | Notes |
|---|---:|---:|---|
| Q1 | Pending | Pending | |
| Q2 | Pending | Pending | |
| Q3 | Pending | Pending | |
| Q4 | Pending | Pending | |
| Q5 | Pending | Pending | |
| Q6 | Pending | Pending | Must identify missing plot-level data |
| Q7 | Pending | Pending | |
| Q8 | Pending | Pending | |
| Q9 | Pending | Pending | |
| Q10 | Pending | Pending | |

## Expected Outcome

Prompt B should provide more reliable answers because it uses
the available CGWB records and instructs the model not to
invent missing information.

Actual scores and observations must be filled after running
both prompts against all 10 questions.
