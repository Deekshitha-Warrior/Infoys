# Dashboard scores and PDF traceability

Rechecked against the full supplied project specification on 17 November 2026.
The dashboard displays real computed quantities, not demonstration percentages.
The mentor request is interpreted as match scores plus visible mathematics.

| Dashboard measure | Formula and source |
|---|---|
| Career match index (0-100) | 0.8 times mean classifier probability percentage plus 0.2 times unrounded skill alignment percentage. This is the existing ranking heuristic, not a probability of getting hired. |
| Model confidence | 100 times the arithmetic mean of Logistic Regression, Random Forest and XGBoost class probabilities. Uncalibrated. |
| Skill match | Listed canonical required skills divided by required checklist skills times 100. |
| Skill gap | Missing checklist skills divided by required skills times 100. Lower means fewer missing skills. |
| Learning tasks complete | Self-marked completed missing-skill tasks divided by missing-skill tasks times 100. Existing skills are excluded from this numerator. |
| Roadmap coverage | Existing listed skills plus self-marked completed missing-skill tasks, divided by all required skills, times 100. This is not assessed mastery. |
| Profile completeness | Filled degree, institution, graduation year, experience field and technical-skill section divided by five, times 100. |
| Resume completeness | Passed structural checks divided by eight, times 100. Not ATS or grammar accuracy. |
| Recognized skill coverage | Supplied canonical skills having at least one token in the trained vocabulary divided by supplied skills, times 100. A vocabulary check, not semantic/proficiency assessment. |

Each score card displays its formula, the relevant counts where available, and
an explanation. Missing analyses and resume uploads show a dash instead of zero.
Career cards show composite match indices, skill match and model confidence.
Career Intelligence also shows the ranking index and skill-match fraction.

Separate validation results on the dashboard show accuracy, macro precision,
macro recall, macro F1 and Top-5 recall on the held-out survey sample. Expand
its formula section for definitions. These are global model metrics, never
presented as an individual user's score. The macro F1 gate and missing real
pilot feedback are explicitly displayed.

## Limits from the PDF

The specification also mentions confidence intervals, market-demand signals,
experience recency/seniority weighting, independently evaluated parsing,
SemEval/LinkedIn benchmarks, and pilot/user acceptance percentages. The current
data does not establish those scores. The dashboard explicitly marks these
limitations rather than inventing percentages. Binary listed/missing skill
status is not a measured competency level. See MILESTONES.md and MILESTONE3.md
for acceptance evidence and the still-unmet model quality targets.

Display values are rounded. The composite uses unrounded probability and skill
fractions internally, so arithmetic on rounded display values can differ slightly.
