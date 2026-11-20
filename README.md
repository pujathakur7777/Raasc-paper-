# RAASC: An Adaptive Edge-Cloud Semantic-Cache Management Policy with a Calibrated Risk Budget for Voice-Assistant Pipelines

**Authors:** Puja Thakur, Arvind Kumar, Jagpreet Sidhu  
**Repository:** [https://github.com/pujathakur7777/Raasc-paper-](https://github.com/pujathakur7777/Raasc-paper-)  
**DOI Status:** Pending (archived release / persistent DOI to be added upon publication)

---

## Overview

Semantic caching at the network edge helps voice-assistant pipelines answer repeated questions locally without always round-tripping to the cloud. However, fixed per-class Time-To-Live (TTL) windows and a single global cosine-similarity threshold struggle when:
- Different intents update at different, uncertain rates.
- The cost of an incorrect answer depends on the query/intent class and embedding geometry.
- The gateway observes cloud responses and version tags on misses/audits that static rules ignore.
- Network links degrade or fail.

**RAASC** replaces separate static TTLs and global similarity thresholds with a single **operator-defined risk budget ($\rho$)** (default $\rho = 0.05$). A cached candidate is served only when its estimated, severity-weighted risk fits within $\rho$, combining:
1. **Staleness probability ($p_{\text{stale}}$):** Estimated online via a Gamma-Poisson update-rate estimator using cloud version tags, accounting for push-based invalidations ($\kappa_c$).
2. **Wrong-intent probability ($p_{\text{wrong}}$):** Estimated via an online bin-wise cosine-similarity calibrator updated from miss labels and asynchronous shadow audits ($\epsilon = 2\%$).
3. **Class severity weight ($\sigma_c$):** Applied across volatility classes (`static`, `semi-static`, `volatile`).

The policy also includes **risk-based admission and eviction**, a **pre-lookup deny-list** for sensitive/restricted categories, and a **flagged degraded mode** when the cloud link is down.

> **Scope & Safety Note:** Healthcare question answering is used as an illustrative application context for severity classes and update dynamics. All reported results are from simulation and analytical models—**no clinical-safety, end-to-end voice-pipeline, or hardware-deployment claims are made**.

---

## Key Highlights & Results

- **Synthetic Workload (20 test seeds; baselines tuned on 10 validation seeds):**
  - Default class-aware TTL with invalidation (`7 d / 6 h`, $\tau = 0.80$): **60.9%** hit rate, **6.72%** incorrect rate, **114.6** error cost per 1,000 queries.
  - **RAASC + inv ($\rho = 0.05$):** **44.8%** hit rate, **2.60%** incorrect rate, **22.3** error cost per 1,000 queries.
  - Achieves a hit-rate–error-cost trade-off comparable to validation-tuned baselines without requiring labelled tuning traffic (e.g., **+7.5** hit-rate points over the cap-15 tuned TTL baseline at $\rho = 0.05$, without statistically significant superiority after multiple-comparison adjustment).
- **Real Encoder Embeddings (`all-MiniLM-L6-v2`):**
  - **MedQuAD:** Default $\tau = 0.80$ yields **23.7%** incorrect answers; RAASC + inv ($\rho = 0.05$) lowers incorrect answers to **3.94%** (error cost **23.0**) at **40.1%** hits.
  - **MQP (human-labelled pairs):** Calibration reduces error cost from **41.1** (no calibrator) to **9.2** per 1,000 queries (53.1% hits at $\rho = 0.05$).
  - **PAWS (adversarial high-overlap pairs):** High lexical/embedding overlap causes poor separability; RAASC largely abstains at tight budgets and can exceed its budget at $\rho = 0.05$ (10.1% incorrect).
- **Calibration & Robustness Findings:**
  - Risk estimators are **anti-conservative** in high-similarity bins and at small/default budgets (realised cost up to ~2.1× mean estimated risk in tested settings), so $\rho$ acts as an **operating control knob** rather than a strict safety guarantee.
  - Intent-identifier errors of even a few percent noticeably reduce hit rates.

---

## Reproducibility & Artifacts

- **Core Simulator:** `raasc_sim2.py` (Python / NumPy / Numba)
- **Reference Environment:** Python `3.13.18`, NumPy `2.5.3`
- **Frozen Simulator SHA-256 Digest:** `f23a6f4b27f4496e6b008d65ef009941785baf05a22ff5cf9248bf247037f871`
- **Seeds:** Test seeds `0–19`, validation seeds `100–109`
- **Experiment Runner & Scripts:** `run_all.py` and per-workload scripts for **MedQuAD**, **MQP**, and **PAWS** (saving per-seed JSON metrics).
- **Third-Party Models & Datasets:**
  - `all-MiniLM-L6-v2` (ONNX export of `@maycombhq/embed-model 2.0.0-beta.1`, SHA-256: `759c3cd2b7fe7e93933ad23c4c9181b7396442a2ed746ec7c1d46192c469c46e`)
  - MedQuAD, MQP, and PAWS-Wiki (subject to their respective licenses and terms).

*(Add your exact directory tree, installation steps, CLI commands for `run_all.py` and dataset scripts, and output file paths here once pushed to the repo.)*

---

## Limitations & Open Items

- **Simulation only:** No live voice ASR/TTS pipeline, no real patient/clinical records, no real update revision histories, and no physical edge-gateway power/latency measurements (latency and energy figures use analytical estimates from published prototype constants).
- **Future work:** Non-repeat and paraphrase-stratified workloads, real revision histories, direct comparison with `vCache`, per-intent/per-pair calibration with randomised candidate-level auditing, conformal risk bounds, hardware profiling, and a persistent DOI release.
