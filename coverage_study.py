#!/usr/bin/env python3
"""Isolated coverage study of the wrong-intent estimators (seed 0, 200,000 draws per setting)."""
import json, numpy as np
from scipy.stats import beta
rng = np.random.default_rng(0)
out = []
for q in (0.02, 0.1, 0.3):
    for n in (20, 60, 185, 600):
        w = rng.binomial(n, q, size=200000)
        row = dict(q=q, n=n)
        for tag, p0 in (("eq6", q), ("eq6_opt", q / 4)):
            m = (8 * p0 + w) / (8 + n)
            est = np.minimum(1, m + np.sqrt(m * (1 - m) / (n + 9)))
            row[tag] = (float((est >= q).mean() * 100), float(est.mean()))
        est = np.minimum(1, w / n + np.sqrt(np.log(20) / (2 * n)))
        row["hoeff"] = (float((est >= q).mean() * 100), float(est.mean()))
        ub = np.where(w < n, beta.ppf(0.95, w + 1, np.maximum(n - w, 1)), 1.0)
        row["cp"] = (float((ub >= q).mean() * 100), float(ub.mean()))
        out.append(row)
json.dump(out, open("coverage.json", "w"))
for r in out: print(r)
