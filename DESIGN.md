\# Design Document: <project name>



> Draft for Omar to adapt. Items marked \*\*\[VERIFY]\*\* are claims or

> resources I have not confirmed in detail. Replace my reasoning with

> your own wherever you disagree, and cut anything you cannot defend.



\## 1. Problem and scope



A spaced repetition language trainer that schedules reviews using a

learned model of recall, designed to work for languages with little

available data, with Mauritian Creole as the first target. See the README

for the personal motivation.



\*\*In scope:\*\*

\- Card model and local SQLite storage

\- SM-2 scheduler as the baseline

\- Command-line review loop

\- Full logging of every review

\- One learned recall model, evaluated against the baseline

\- A small, hand-verified Mauritian Creole card set (a few hundred cards)



\*\*Deliberately out of scope (for now), and why:\*\*

\- Web or mobile interface: postponed until the scheduler is validated

\- Multiple user accounts: unnecessary for a personal tool

\- Speech recognition or pronunciation scoring: needs data and tooling

&#x20; well beyond the core claim

\- Language-model-generated card content: reliability on a low-resource

&#x20; language is unproven, so generated content would need checking anyway



\## 2. Prior art



| Source | What it does | What I took from it | Reservations |

|---|---|---|---|

| SM-2 (SuperMemo, the Anki baseline) | Multiplies the review interval by an ease factor adjusted by a self-rated recall score | Simple, deterministic, well understood baseline | One fixed rule for every learner and card; does not output a recall probability |

| FSRS | Models memory with stability, difficulty and retrievability, with trainable parameters, and schedules to a target retention | Framing scheduling as predicting recall probability | Fitting parameters needs enough review data \*\*\[VERIFY]\*\* |

| Half-life regression (Settles and Meeder, Duolingo, 2016) | Models recall probability as exponential decay with a per-card half-life estimated by regression on features | Simple, interpretable, and not tied to any particular language | Trained on very large logs; a single learner's data is far smaller |

| Existing apps for less common languages | General tools were combined to cover the gap | The motivating problem | \*\*\[Add your own findings from using them]\*\* |



\## 3. Core design decisions



\### 3.1 Card data model

\- \*\*Choice:\*\* a `dataclass` holding content only (id, language, prompt,

&#x20; answer, accepted spelling variants, tags). Scheduling state lives in a

&#x20; separate table.

\- \*\*Alternative considered:\*\* scheduling fields on the card itself.

\- \*\*Reasoning:\*\* separating content from state lets different schedulers

&#x20; run over the same cards, which the comparison in Section 5 needs.



\### 3.2 Storage and database schema

\- \*\*Choice:\*\* SQLite through the standard library, with tables for

&#x20; cards, scheduling state and reviews.

\- \*\*Alternative considered:\*\* JSON files, or a server database.

\- \*\*Reasoning:\*\* no setup, a single file, and the review history is

&#x20; directly queryable for training and evaluation.



\### 3.3 Review log schema

\- \*\*Fields:\*\* review id, card id, timestamp (UTC), rating, whether the

&#x20; answer was correct, response time, days since the previous review,

&#x20; interval that was scheduled, scheduler name and version, and the typed

&#x20; answer if applicable.

\- \*\*Reasoning:\*\* recall models depend on counts of past successes and

&#x20; failures and on elapsed time since the last review. Logging the

&#x20; scheduler version means reviews produced by different schedulers can

&#x20; be told apart later. Anything not logged now cannot be recovered.



\### 3.4 Scheduler interface

\- \*\*Choice:\*\* one common interface, with a method to update a card's

&#x20; state after a review and a method returning predicted recall at a

&#x20; given time.

\- \*\*Reasoning:\*\* SM-2 and the learned model must be interchangeable so

&#x20; an evaluation harness can replay the same logs through either.



\### 3.5 Answer matching

\- \*\*Choice:\*\* normalise Unicode (NFC) and case, then compare against

&#x20; the stored answer and its accepted variants.

\- \*\*Reasoning:\*\* Mauritian Creole spelling has varied historically

&#x20; between orthographies, so a single canonical spelling would mark

&#x20; correct answers wrong.



\## 4. Content sourcing



\- \*\*Sources to investigate:\*\* the standardised orthography

&#x20; (\*Lortograf Kreol Morisien\*, Ministry of Education, 2011, building on

&#x20; the harmonised writing system known as \*Grafi Larmoni\*) as the spelling

&#x20; reference; \*Diksyoner Morisien\* (Carpooran), a monolingual dictionary;

&#x20; online dictionaries including Lalit's and Rajki's Morisyen dictionary

&#x20; with etymologies (2008); and the KreoLex lexical database (Fabiola

&#x20; Henri, University at Buffalo), which includes word frequency data

&#x20; \*\*\[VERIFY availability and contents]\*\*.

\- \*\*Verification method:\*\* every card is checked against at least two

&#x20; independent sources before it is marked verified. Unverified cards are

&#x20; flagged and kept separate.

\- \*\*Known risks:\*\* orthographic variation across sources; data licences

&#x20; (check the terms before committing any dataset to a public repository);

&#x20; a small card set limiting how much data the model can ever learn from.



\## 5. Machine learning plan and evaluation



\- \*\*Baseline:\*\* SM-2, plus a trivial predictor (the learner's overall

&#x20; average recall rate) so the model is compared against something

&#x20; meaningful even before SM-2 is involved.

\- \*\*Candidate models:\*\* half-life regression first; FSRS-style fitting

&#x20; afterwards if the data allows.

\- \*\*Features:\*\* past successes and failures, time since last review,

&#x20; number of reviews, and word-level features such as frequency and length.

\- \*\*Metric:\*\* log loss on predicted recall probability, plus a

&#x20; calibration check (when the model says 80%, is the learner right

&#x20; about 80% of the time?).

\- \*\*Data split:\*\* chronological. Train on earlier reviews and test on

&#x20; later ones, because a random split leaks future information into

&#x20; training and flatters the model.

\- \*\*Data volume:\*\* a single learner will produce few reviews. Consider

&#x20; first validating the method on a public dataset released with the

&#x20; half-life regression paper \*\*\[VERIFY it is still available]\*\*, then

&#x20; applying it to your own logs.

\- \*\*Success criterion:\*\* the model achieves lower held-out log loss than

&#x20; the baselines. If there are too few reviews to tell, report the result

&#x20; as inconclusive rather than claiming an improvement.



\## 6. Roadmap



| Stage | Deliverable | Status |

|---|---|---|

| 1 | Card model, SQLite schema, review log | Not started |

| 2 | SM-2 scheduler with unit tests | Not started |

| 3 | Command-line review loop | Not started |

| 4 | Verified Mauritian Creole card set | Not started |

| 5 | Evaluation harness replaying logs | Not started |

| 6 | Learned recall model and comparison | Not started |



\## 7. Open questions



\- SM-2 outputs intervals, not probabilities. What is the fairest way to

&#x20; compare it with a model that outputs recall probability, for example

&#x20; by fitting a simple probability function to SM-2's scheduled

&#x20; intervals, or by simulating reviews?

\- How many reviews are enough for the model to be worth trusting?

\- Which orthography is the canonical form for stored answers?

\- What are the licence terms of each content source?

\- Typed answers or self-rated ones? Typed answers give cleaner data but

&#x20; need tolerant matching.

