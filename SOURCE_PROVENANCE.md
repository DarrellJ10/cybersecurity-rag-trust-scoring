# Source provenance and synthetic fixtures

The frozen `corpus.json` includes passage-level source and family metadata. Original collection records, source snapshots, reviews, corpus fingerprints, and evaluation manifests are preserved inside the final checkpoint. This repository does not claim authorship of third-party guidance.

Evidence families are NIST (`nist.gov`), the UK National Cyber Security Centre (`ncsc.gov.uk`), and the jointly authored StopRansomware guide. A jointly published guide or a repost is not counted as an additional independent source. Only claim-09 has complete reference support from two families; the other claims have full support from one family.

Do not interpret a domain preference as authenticated provenance or guaranteed truth. The detector assigns fixed priors to domains and can misclassify legitimate text. Some comparison passages can be unrelated or poisoned.

Passages with synthetic poison identifiers, including `synthetic-poison-*`, `study-added-*`, and `heldout-added-*`, deliberately contain false claims. Copies are controlled repetition fixtures, not independent sources. Evaluation-only labels and reference answers are not intended as generator or detector inputs.

Source text, models, and other third-party materials remain subject to their respective terms. No blanket license for third-party source snapshots is asserted. No open-source license has been selected for the authors' code in this repository snapshot.
