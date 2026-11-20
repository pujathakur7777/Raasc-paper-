#!/usr/bin/env python3
"""Runs every experiment of the v5 paper with raasc_sim2.py (frozen) and writes results.json."""
import json, sys, time, hashlib, itertools, platform
import numpy as np
import raasc_sim2 as S

TEST = list(range(0, 20))
VAL = list(range(100, 110))
DAY = 86400.0
_wl = {}


def WL(seed, shift="matched", deny="none"):
    key = (seed, shift, deny)
    if key not in _wl:
        _wl[key] = S.make_workload(seed, shift, deny)
    return _wl[key]


def collect(fn, seeds, shift="matched", deny="none", p_out=0.0, eta=0.0, deny_cfg=None, keep=False):
    rows = []; raw = []
    for s in seeds:
        wl = WL(s, shift, deny)
        aux = S.make_aux(wl, p_out=p_out, eta=eta, deny_cfg=deny_cfg)
        r = fn(wl, aux)
        m = S.metrics(wl, aux, r)
        rows.append(m)
        if keep:
            raw.append((wl, aux, r))
    return (rows, raw) if keep else rows


def arr(rows, k):
    return np.array([r[k] for r in rows], dtype=float)


R = {}          # name -> list of per-seed metric dicts
LOG = {}


def run(name, fn, seeds=TEST, **kw):
    t0 = time.time()
    R[name] = collect(fn, seeds, **kw)
    print(f"{name:55s} hit={arr(R[name],'hit').mean():6.2f} unsafe={np.nanmean(arr(R[name],'unsafe')):6.2f} "
          f"harm={arr(R[name],'harm').mean():7.2f} [{time.time()-t0:.1f}s]", flush=True)


# ------------------------------------------------------------ baseline tuning (validation seeds only)
GRID_TAU = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]
GRID_S = [1 * DAY, 3 * DAY, 7 * DAY, 14 * DAY]
GRID_M = [1 * 3600.0, 3 * 3600.0, 6 * 3600.0, 12 * 3600.0]
CAPS = [5.0, 15.0]


def tune_ttl(inv):
    res = []
    for tau, ts, tm in itertools.product(GRID_TAU, GRID_S, GRID_M):
        rows = collect(lambda wl, aux: S.sim_ttl(wl, aux, inv=inv, ttl=(ts, tm, 0.0), tau=tau), VAL)
        res.append(((tau, ts, tm), arr(rows, "hit").mean(), arr(rows, "harm").mean()))
    return res


def tune_tau_only(inv):
    res = []
    for tau in GRID_TAU:
        rows = collect(lambda wl, aux: S.sim_ttl(wl, aux, inv=inv, ttl=(S.INF, S.INF, S.INF), tau=tau), VAL)
        res.append(((tau,), arr(rows, "hit").mean(), arr(rows, "harm").mean()))
    return res


def pick(res, cap):
    ok = [x for x in res if x[2] <= cap]
    if ok:
        return max(ok, key=lambda x: x[1])
    return min(res, key=lambda x: x[2])


TUNED = {}
t0 = time.time()
for inv in (False, True):
    g = tune_ttl(inv)
    g2 = tune_tau_only(inv)
    LOG[f"grid_ttl_inv{int(inv)}"] = [(list(map(float, a)), float(b), float(c)) for a, b, c in g]
    LOG[f"grid_tau_inv{int(inv)}"] = [(list(map(float, a)), float(b), float(c)) for a, b, c in g2]
    for cap in CAPS:
        TUNED[("ttl", inv, cap)] = pick(g, cap)
        TUNED[("tau", inv, cap)] = pick(g2, cap)
print("tuning done", time.time() - t0, flush=True)
LOG["tuned"] = {f"{k[0]}_inv{int(k[1])}_cap{k[2]}": [list(map(float, v[0])), float(v[1]), float(v[2])] for k, v in TUNED.items()}
for k, v in TUNED.items():
    print("tuned", k, v, flush=True)


def ttl_tuned(inv, cap, degm=0.0):
    (tau, ts, tm), _, _ = TUNED[("ttl", inv, cap)]
    return lambda wl, aux: S.sim_ttl(wl, aux, inv=inv, ttl=(ts, tm, 0.0), tau=tau, degm=degm)


def tau_tuned(inv, cap):
    (tau,), _, _ = TUNED[("tau", inv, cap)]
    return lambda wl, aux: S.sim_ttl(wl, aux, inv=inv, ttl=(S.INF, S.INF, S.INF), tau=tau)


# ------------------------------------------------------------ E1 main comparison (0% outage)
R["cloud"] = collect(lambda wl, aux: None, TEST) if False else None
rows = []
for s in TEST:
    wl = WL(s); aux = S.make_aux(wl); rows.append(S.cloud_only(wl, aux))
R["cloud_only"] = rows
VD_NI = (1.5 * DAY, 36 * 60.0, 0.0)
VD_I = (3.1 * DAY, 73 * 60.0, 0.0)
run("ttl_default", lambda wl, aux: S.sim_ttl(wl, aux, inv=False))
run("ttl_default_inv", lambda wl, aux: S.sim_ttl(wl, aux, inv=True))
run("tau_default", lambda wl, aux: S.sim_ttl(wl, aux, inv=False, ttl=(S.INF,) * 3))
run("tau_default_inv", lambda wl, aux: S.sim_ttl(wl, aux, inv=True, ttl=(S.INF,) * 3))
run("ttl_vd", lambda wl, aux: S.sim_ttl(wl, aux, inv=False, ttl=VD_NI))
run("ttl_vd_inv", lambda wl, aux: S.sim_ttl(wl, aux, inv=True, ttl=VD_I))
for cap in CAPS:
    for inv in (False, True):
        run(f"ttl_tuned_cap{int(cap)}{'_inv' if inv else ''}", ttl_tuned(inv, cap))
        run(f"tau_tuned_cap{int(cap)}{'_inv' if inv else ''}", tau_tuned(inv, cap))
run("raasc", lambda wl, aux: S.sim_raasc(wl, aux, inv=False))
run("raasc_inv", lambda wl, aux: S.sim_raasc(wl, aux, inv=True))

# ------------------------------------------------------------ E2 budget sweep
for rho in (0.02, 0.05, 0.10, 0.20, 0.40):
    run(f"budget_{rho}", lambda wl, aux, rho=rho: S.sim_raasc(wl, aux, inv=True, rho=rho))
    run(f"budget_maxsev_{rho}", lambda wl, aux, rho=rho: S.sim_raasc(wl, aux, inv=True, rho=rho, maxsev=True))

# ------------------------------------------------------------ E3 ablations and robustness
run("abl_nocal", lambda wl, aux: S.sim_raasc(wl, aux, use_cal=0, tau0=0.80))
run("abl_noadapt", lambda wl, aux: S.sim_raasc(wl, aux, adaptive=0))
run("est_hoeff", lambda wl, aux: S.sim_raasc(wl, aux, est="hoeff"))
run("est_cp", lambda wl, aux: S.sim_raasc(wl, aux, est="cp"))
run("est_eq6_ipw", lambda wl, aux: S.sim_raasc(wl, aux, ipw=1))
run("eps_0.10", lambda wl, aux: S.sim_raasc(wl, aux, eps=0.10))
run("eps_0.10_ipw", lambda wl, aux: S.sim_raasc(wl, aux, eps=0.10, ipw=1))
run("eps_0.00", lambda wl, aux: S.sim_raasc(wl, aux, eps=0.0))
for pr in ("opt", "pess", "flat"):
    run(f"prior_{pr}", lambda wl, aux, pr=pr: S.sim_raasc(wl, aux, prior=pr))
for eta in (0.02, 0.05):
    run(f"labelnoise_{eta}", lambda wl, aux: S.sim_raasc(wl, aux), eta=eta)
for km in (0.0, 0.25, 0.75):
    run(f"kappa_x{km}", lambda wl, aux, km=km: S.sim_raasc(wl, aux, kmult=km))
for lm in (3.0, 300.0, 3600.0):
    run(f"lmin_{int(lm)}", lambda wl, aux, lm=lm: S.sim_raasc(wl, aux, lmin=lm))
run("repl_raasc_default_cache50", lambda wl, aux: S.sim_raasc(wl, aux, C=50))
run("repl_raasc_default_cache200", lambda wl, aux: S.sim_raasc(wl, aux, C=200))
run("repl_ttl_cache50", lambda wl, aux: S.sim_ttl(wl, aux, inv=True, C=50))
run("repl_ttl_cache200", lambda wl, aux: S.sim_ttl(wl, aux, inv=True, C=200))

# ------------------------------------------------------------ E4 outage 10%
OUT = dict(p_out=0.10)
rows = []
for s in TEST:
    wl = WL(s); aux = S.make_aux(wl, p_out=0.10); rows.append(S.cloud_only(wl, aux))
R["out_cloud_only"] = rows
run("out_ttl_default", lambda wl, aux: S.sim_ttl(wl, aux, inv=False), **OUT)
run("out_ttl_default_deg4", lambda wl, aux: S.sim_ttl(wl, aux, inv=False, degm=4.0), **OUT)
for cap in CAPS:
    run(f"out_ttl_tuned_cap{int(cap)}_inv", ttl_tuned(True, cap), **OUT)
    run(f"out_ttl_tuned_cap{int(cap)}_inv_deg4", ttl_tuned(True, cap, degm=4.0), **OUT)
run("out_raasc_nodeg", lambda wl, aux: S.sim_raasc(wl, aux, deg=0), **OUT)
for f in (2.0, 4.0, 6.0, 8.0):
    run(f"out_raasc_deg{int(f)}", lambda wl, aux, f=f: S.sim_raasc(wl, aux, deg=1, degf=f), **OUT)
    run(f"out_raasc_strict{int(f)}", lambda wl, aux, f=f: S.sim_raasc(wl, aux, deg=2, degf=f), **OUT)

# ------------------------------------------------------------ E5 shifted update rates
for shift in ("wrongprior", "sudden", "drift"):
    run(f"shift_{shift}_adaptive", lambda wl, aux: S.sim_raasc(wl, aux, adaptive=1), shift=shift)
    run(f"shift_{shift}_prior", lambda wl, aux: S.sim_raasc(wl, aux, adaptive=0), shift=shift)
    run(f"shift_{shift}_ttl_inv", lambda wl, aux: S.sim_ttl(wl, aux, inv=True), shift=shift)
    run(f"shift_{shift}_ttl_tuned5_inv", ttl_tuned(True, 5.0), shift=shift)

# ------------------------------------------------------------ E6 selection bias (labels, oracle, coverage)
def bin_report(variants):
    out = {}
    for name, kw in variants.items():
        miss = np.zeros((len(TEST), 10)); aud = np.zeros_like(miss); dec = np.zeros_like(miss)
        wm = np.zeros_like(miss); wa = np.zeros_like(miss); wo = np.zeros_like(miss)
        est = {"eq6": np.zeros_like(miss), "H": np.zeros_like(miss), "CP": np.zeros_like(miss), "ipw": np.zeros_like(miss)}
        cp = S.cp_table(); p0 = S.prior_p0()
        for i, s in enumerate(TEST):
            wl = WL(s); aux = S.make_aux(wl)
            r = S.sim_raasc(wl, aux, **kw)
            b = r["binlog"]; dw = r["decw"]; ls = r["lsrc"]
            for k in range(10):
                m = b == k
                dec[i, k] = m.sum(); wo[i, k] = (dw & m).sum()
                mm = m & (ls == 1); aa = m & (ls == 2)
                miss[i, k] = mm.sum(); aud[i, k] = aa.sum()
                wm[i, k] = (dw & mm).sum(); wa[i, k] = (dw & aa).sum()
                cw, cn, cs2 = r["cw"], r["cn"], r["cs2"]
                dummy = np.ones(10)
                for key, mode in (("eq6", 0), ("H", 1), ("CP", 2)):
                    est[key][i, k] = S.pwrong_est(k, mode, cw, cn, cs2, p0, 8.0, cp, 1, 0.9, 0.8)
        out[name] = dict(miss=miss, aud=aud, dec=dec, wm=wm, wa=wa, wo=wo, est=est)
    return out


BR = bin_report({"plain": dict(), "ipw": dict(ipw=1)})


def bin_summary(b):
    res = []
    for k in range(10):
        dec = b["dec"][:, k]; wo = b["wo"][:, k]
        orc_seed = np.where(dec > 0, wo / np.maximum(dec, 1), np.nan)
        row = dict(bin=k, lo=0.5 + 0.05 * k, miss_per_seed=float(b["miss"][:, k].mean()), aud_per_seed=float(b["aud"][:, k].mean()),
                   dec_per_seed=float(dec.mean()),
                   rate_miss=float(b["wm"][:, k].sum() / max(b["miss"][:, k].sum(), 1)) if b["miss"][:, k].sum() > 0 else None,
                   rate_aud=float(b["wa"][:, k].sum() / max(b["aud"][:, k].sum(), 1)) if b["aud"][:, k].sum() > 0 else None,
                   rate_orc=float(wo.sum() / max(dec.sum(), 1)) if dec.sum() > 0 else None)
        for key in ("eq6", "H", "CP"):
            e = b["est"][key][:, k]
            ok = ~np.isnan(orc_seed)
            row["cov_" + key] = float(100 * np.mean(e[ok] >= orc_seed[ok])) if ok.any() else None
            row["mean_" + key] = float(e[ok].mean()) if ok.any() else None
        res.append(row)
    return res


LOG["bins_plain"] = bin_summary(BR["plain"])
LOG["bins_ipw"] = bin_summary(BR["ipw"])
# pooled labelled share above 0.80
d = BR["plain"]
hi = slice(6, 10)
LOG["label_share_hi"] = dict(
    labelled_frac=float((d["miss"][:, hi].sum() + d["aud"][:, hi].sum()) / max(d["dec"][:, hi].sum(), 1)),
    miss_share=float(d["miss"][:, hi].sum() / max(d["miss"][:, hi].sum() + d["aud"][:, hi].sum(), 1)))
# estimator coverage (6) at end of week for IPW variant
print("bins done", flush=True)

# ------------------------------------------------------------ E7 deny-list
def denyrun(name, rate_cfg, deny, fn):
    run(name, fn, deny=deny, deny_cfg=rate_cfg)


for deny in ("uniform", "rare"):
    tag = deny
    denyrun(f"deny_{tag}_raasc_nolist", None, deny, lambda wl, aux: S.sim_raasc(wl, aux))
    denyrun(f"deny_{tag}_ttl_nolist", None, deny, lambda wl, aux: S.sim_ttl(wl, aux, inv=True))
    for r in (0.7, 0.9, 1.0):
        for fpr in (0.0, 0.05):
            denyrun(f"deny_{tag}_raasc_r{r}_fp{fpr}", (r, fpr, False), deny, lambda wl, aux: S.sim_raasc(wl, aux))
        if r < 1.0:
            denyrun(f"deny_{tag}_raasc_r{r}_fp0.0_corr", (r, 0.0, True), deny, lambda wl, aux: S.sim_raasc(wl, aux))
    denyrun(f"deny_{tag}_ttl_r1.0_fp0.0", (1.0, 0.0, False), deny, lambda wl, aux: S.sim_ttl(wl, aux, inv=True))

# ------------------------------------------------------------ statistics
from scipy import stats

rng = np.random.default_rng(2026)


def paired(a, b, metric, lower_is_better=True):
    x = arr(R[a], metric) - arr(R[b], metric)
    n = len(x)
    mean = x.mean(); sd = x.std(ddof=1)
    tq = stats.t.ppf(0.975, n - 1)
    ci = (mean - tq * sd / np.sqrt(n), mean + tq * sd / np.sqrt(n))
    dz = mean / sd if sd > 0 else 0.0
    p_t = stats.ttest_1samp(x, 0.0).pvalue if sd > 0 else 1.0
    try:
        p_w = stats.wilcoxon(x).pvalue
    except Exception:
        p_w = 1.0
    flips = rng.choice([-1.0, 1.0], size=(20000, n))
    pm = np.mean(np.abs((flips * x).mean(1)) >= abs(mean) - 1e-12)
    wins = int((x < 0).sum() if lower_is_better else (x > 0).sum())
    sh = stats.shapiro(x).pvalue if sd > 0 else 1.0
    return dict(delta=float(mean), lo=float(ci[0]), hi=float(ci[1]), dz=float(dz), p_t=float(p_t), p_w=float(p_w),
                p_perm=float(pm), wins=wins, shapiro=float(sh))


PAIRS = [("raasc", "ttl_default"), ("raasc_inv", "ttl_default_inv"), ("raasc_inv", "ttl_tuned_cap5_inv"),
         ("raasc_inv", "ttl_tuned_cap15_inv"), ("raasc_inv", "ttl_vd_inv"), ("raasc_inv", "tau_tuned_cap5_inv")]
METS = [("hit", False), ("unsafe", True), ("harm", True), ("energy", True)]
PT = {}
fam = []
for a, b in PAIRS:
    for m, lib in METS:
        key = f"{a}|{b}|{m}"
        PT[key] = paired(a, b, m, lib)
        fam.append(key)
# calibration ablation, estimator pairs (second family)
for a, b in (("raasc_inv", "abl_nocal"), ("raasc_inv", "abl_noadapt"), ("est_hoeff", "raasc"), ("est_cp", "raasc")):
    for m, lib in METS:
        key = f"{a}|{b}|{m}"
        PT[key] = paired(a, b, m, lib)
        fam.append(key)
# Holm over whole family
ps = np.array([PT[k]["p_t"] for k in fam])
order = np.argsort(ps)
m = len(ps)
adj = np.empty(m)
run_max = 0.0
for rank, idx in enumerate(order):
    val = (m - rank) * ps[idx]
    run_max = max(run_max, val)
    adj[idx] = min(1.0, run_max)
for k, a in zip(fam, adj):
    PT[k]["p_holm"] = float(a)
LOG["holm_family_size"] = m

# ------------------------------------------------------------ energy sensitivity (analytic, uses measured RAASC hit)
h = float(arr(R["raasc_inv"], "hit").mean()) / 100.0
LOG["energy_sens"] = []
for tc in (0.1, 0.25, 0.5, 1.0, 2.0):
    for ti in (2.0, 4.77, 8.0):
        for eps in (0.0, 0.02, 0.10):
            sav = 1 - (tc + (1 - h + eps * h) * ti) / ti
            be = (tc / ti) / (1 - eps)
            LOG["energy_sens"].append(dict(tc=tc, ti=ti, eps=eps, saving=sav, breakeven=be))

# ------------------------------------------------------------ dump
def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(x) for x in o]
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return o


sha = hashlib.sha256(open("raasc_sim2.py", "rb").read()).hexdigest()
meta = dict(sha256_raasc_sim2=sha, python=platform.python_version(), numpy=np.__version__, test_seeds=TEST, val_seeds=VAL,
            n_queries_seed0=int(WL(0)["N"]))
json.dump(clean(dict(meta=meta, R={k: v for k, v in R.items() if v is not None}, LOG=LOG, PT=PT)), open("results.json", "w"))
print("saved; sha256", sha)
