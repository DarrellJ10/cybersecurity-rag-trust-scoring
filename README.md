# Source-Diversity Trust Scoring for Retrieval Poisoning Detection in Cybersecurity RAG Systems

**Darrell Jarrett and John Nguyen**

Graduate research implementation and saved experiments for a cybersecurity retrieval-augmented generation (RAG) system. We test whether provenance and source-family aggregation can identify injected false passages while preserving useful evidence and answer quality.

## Start here

[![Open saved-results verification in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DarrellJ10/cybersecurity-rag-trust-scoring/blob/main/06_Verify_Saved_Results.ipynb)

**Recommended first step:** open `06_Verify_Saved_Results.ipynb` and run its cells. It verifies the saved archive and displays the final context and answer summaries. It does not download model weights, run inference, or change grades. Locally, Python 3.10+ is sufficient:

```bash
git clone https://github.com/DarrellJ10/cybersecurity-rag-trust-scoring.git
cd cybersecurity-rag-trust-scoring
python3 verify_results.py
```

The executed verification notebook includes actual verification output from the supplied files. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the difference between checking saved results and rerunning the historical experiments.

## Included files

| File | Purpose |
|---|---|
| `01_Clean_Baseline_Cybersecurity_RAG.ipynb` | Original clean baseline notebook and saved outputs |
| `02_Retrieval_Poisoning_Experiments.ipynb` | Original targeted poisoning pilot |
| `03_Source_Diversity_Trust_Scoring.ipynb` | Initial defense comparisons |
| `04_Expanded_Research_Evaluation.ipynb` | Expanded corpus, question design, and detector development |
| `05_Trust_Scoring_Detector.ipynb` | Integration, source-repetition experiments, and held-out setup |
| `06_Verify_Saved_Results.ipynb` | Executed, no-model verification entry point |
| `07_Historical_Heldout_Recovery.ipynb` | Recovery workflow used after the original runtime reset |
| `trust_detector_backup_20261027T030637Z.zip` | Final checkpoint: 430 fingerprinted files, corpora, indexes, caches, and all 56 held-out generations |
| `trust_detector_backup_20261026T180455Z.zip` | Earlier development checkpoint required by the historical recovery notebook |
| `heldout_review_results.zip` | Separately packaged final AI-assisted answer review |
| `heldout_ai_review_results_v1.json` | Inspectable final answer review and method summaries |
| `heldout_results_summary.md` | Detailed saved-results summary |
| `corpus.json`, `claims.json`, question and rule JSON files | Exact copies from the frozen evaluation package |
| `method_settings_v1.json`, `test_run_plan_v1.json` | Frozen held-out settings and condition plan |
| `artifact_manifest.json` | File hashes and notebook provenance for this repository snapshot |

Original notebooks are **historical Colab session records**, not a fully automated run-all pipeline. Earlier cells can depend on uploaded checkpoints or globals from that session. Two notebooks retain an interrupted-cell error output; those outputs are not removed to make the record appear cleaner. The final checkpoint and verifier establish what was actually completed. The recovery notebook is included as historical code and has no saved execution outputs in the downloaded copy.

## Design

- Clean corpus: 39 reviewed passages from eight source documents, grouped into NIST, UK NCSC, and joint StopRansomware evidence families.
- Questions: 16 development and 32 held-out; the held-out split contains 24 answerable questions and eight unanswerable questions.
- Retrieval: sparse TF-IDF vectors in SQLite, cosine ranking, top three positive-scoring passages. IDF is refitted per corpus condition.
- Answer model: `Qwen/Qwen2.5-1.5B-Instruct`, revision `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, CPU float32, greedy generation, 160 new tokens maximum.
- Relation classifier: `cross-encoder/nli-MiniLM2-L6-H768`, revision `b95119ce93d3e065de6214e38cd4a97b0f2f2c6d`.
- Experimental trust score: `T = P * (1 - C) + (1 - P) * S`, flagged strictly below 0.45. Source preferences are not calibrated truth probabilities.
- Held-out scope: 27 conditions, eight context-selection methods, 864 condition/question pairs. The predefined generation subset uses 16 questions, two conditions, and four methods: 128 answer uses served by 56 unique generations and five empty-context policy abstention uses.

## Main findings

In the combined condition with two copies of each of eight false fixtures, 16 of 55 passages were poisoned (29.1%). Deduplication plus family grouping removed all 33 retrieved poison occurrences, but also removed 15 of 63 benign occurrences. Deduplication plus passage averaging removed all 33 and removed 14 of 63 benign occurrences. Reference coverage fell to 18/24 answerable questions under both combined methods.

On the eight answerable generation questions in that poisoned condition, exact deduplication produced seven correct answers and one incorrect answer. Both combined detectors produced six correct answers and two abstentions. **Source-family grouping did not outperform passage averaging in the tested configurations.** Detecting retrieved poison did not establish better final answers.

## Review status and limits

Answer grading is **AI-assisted and not independently human-validated**. Two factual judgments remain uncertain. The JSON records preserve this status and grading provenance. Correctness ranges are unresolved-grade bounds, not confidence intervals. Counts reuse a small set of synthetic fixtures, exact copies, and correlated question wordings; they are not independent attack trials. Most claims have full supporting evidence from only one family. No general security improvement or statistical significance is claimed.

Synthetic false passages are experimental fixtures, **not cybersecurity advice**. Consult the attributed official source guidance rather than model outputs or attack text. See [SOURCE_PROVENANCE.md](SOURCE_PROVENANCE.md).

## Submission status

This repository supplies code and experimental artifacts for instructor review. The final IEEE paper, shared Overleaf project, and a PDF printout of the executed research notebook remain separate submission items. Publishing this repository does not email the instructor or invite collaborators. Read-only access is public; write access is not granted to other users.
