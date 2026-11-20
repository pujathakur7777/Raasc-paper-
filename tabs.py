"""Builds every table body and number of the v5 paper from results.json (no hand-typed results)."""
import json
import numpy as np

D = json.load(open("/tmp/claude-0/-home-claude/3d193717-eb3f-5d25-a3fd-e765519136bb/scratchpad/sim/results.json"))
R, L, PT, META = D["R"], D["LOG"], D["PT"], D["meta"]
COV = json.load(open("/tmp/claude-0/-home-claude/3d193717-eb3f-5d25-a3fd-e765519136bb/scratchpad/sim/coverage.json"))
TQ = 2.093


def a(n, k):
    return np.array([r[k] for r in R[n]], dtype=float)


def mean(n, k):
    return float(np.nanmean(a(n, k)))


def ci(n, k):
    x = a(n, k)
    x = x[~np.isnan(x)]
    return float(TQ * x.std(ddof=1) / np.sqrt(len(x)))


def M(n, k, d=1):
    return f"{mean(n, k):.{d}f}"


def PM(n, k, d=1):
    return f"{mean(n, k):.{d}f}$\\pm${ci(n, k):.{d}f}"


def pf(p):
    return "$<$0.001" if p < 0.001 else f"{p:.3f}" if p < 0.1 else f"{p:.2f}"


def sgn(x, d=2):
    s = f"{x:+.{d}f}"
    return s.replace("-", "$-$")


def pooled(n, num, den):
    return 100.0 * a(n, num).sum() / max(a(n, den).sum(), 1)


def rows_table(rows, cols, fmts, label_w="l"):
    out = []
    for lab, n in rows:
        if n is None:
            out.append(f"\\multicolumn{{{len(cols)+1}}}{{@{{}}l}}{{\\textit{{{lab}}}}}\\\\")
            continue
        cells = [PM(n, c, f) for c, f in zip(cols, fmts)]
        out.append(lab + " & " + " & ".join(cells) + "\\\\")
    return "\n".join(out)


def T_main():
    cloud = f"Cloud-only & n/a & n/a & n/a & n/a & n/a & {PM('cloud_only','energy',2)}\\\\\n"
    rows = [("Class TTL (7\\,d/6\\,h, $\\tau$=0.80)", "ttl_default"), ("\\quad + inv", "ttl_default_inv"),
            ("Fixed-$\\tau$ semantic (0.80)", "tau_default"), ("\\quad + inv", "tau_default_inv"),
            ("TTL (V-D limits)", "ttl_vd"), ("\\quad + inv", "ttl_vd_inv"),
            ("TTL tuned, harm cap 5 + inv", "ttl_tuned_cap5_inv"), ("TTL tuned, harm cap 15 + inv", "ttl_tuned_cap15_inv"),
            ("Fixed-$\\tau$ tuned, cap 5 + inv", "tau_tuned_cap5_inv"),
            ("RAASC", "raasc"), ("RAASC + inv", "raasc_inv")]
    return cloud + rows_table(rows, ["hit", "unsafe", "stale", "wrong", "harm", "energy"], [1, 2, 2, 2, 1, 2])


def T_tuned():
    out = []
    for inv in (0, 1):
        for fam, name in (("ttl", "TTL"), ("tau", "Fixed-$\\tau$")):
            for cap in (5.0, 15.0):
                v = L["tuned"][f"{fam}_inv{inv}_cap{cap}"]
                p = v[0]
                if fam == "ttl":
                    cfg = f"$\\tau$={p[0]:.2f}, static {p[1]/86400:.0f}\\,d, semi {p[2]/3600:.0f}\\,h"
                else:
                    cfg = f"$\\tau$={p[0]:.2f}, no TTL"
                out.append(f"{name}{' + inv' if inv else ''}, cap {cap:.0f} & {cfg} & {v[1]:.1f} & {v[2]:.1f}\\\\")
    return "\n".join(out)


def T_budget():
    out = []
    for rho in (0.02, 0.05, 0.1, 0.2, 0.4):
        n = f"budget_{rho}"; m = f"budget_maxsev_{rho}"
        ratio = mean(n, "cost") / mean(n, "rbar")
        out.append(f"{rho:g} & {PM(n,'hit',1)} & {PM(n,'harm',1)} & {PM(n,'harm_s',1)} & {mean(n,'cost'):.4f} & {mean(n,'rbar'):.4f} & {ratio:.2f} & {M(m,'hit',1)} & {M(m,'harm',1)}\\\\")
    return "\n".join(out)


def T_abl():
    rows = [("Full RAASC + inv (default)", "raasc_inv"), ("No calibration (threshold 0.80)", "abl_nocal"),
            ("No adaptive rate (class prior)", "abl_noadapt"), ("Estimator: Hoeffding bound", "est_hoeff"),
            ("Estimator: Clopper--Pearson bound", "est_cp"), ("Eq.~\\eqref{eq:wrong} + IPW (Horvitz--Thompson)", "est_eq6_ipw"),
            ("Audit $\\varepsilon$=0 (miss labels only)", "eps_0.00"), ("Audit $\\varepsilon$=0.10", "eps_0.10"),
            ("Audit $\\varepsilon$=0.10 + IPW", "eps_0.10_ipw"),
            ("Prior optimistic ($p_0/4$)", "prior_opt"), ("Prior pessimistic ($4p_0$)", "prior_pess"), ("Prior flat (0.5)", "prior_flat"),
            ("Label noise 2\\,\\%", "labelnoise_0.02"), ("Label noise 5\\,\\%", "labelnoise_0.05"),
            ("Push coverage $\\times$0 (no events)", "kappa_x0.0"), ("Push coverage $\\times$0.25", "kappa_x0.25"),
            ("Push coverage $\\times$0.75", "kappa_x0.75"),
            ("$L_{\\min}$ = 3\\,s", "lmin_3"), ("$L_{\\min}$ = 300\\,s", "lmin_300"), ("$L_{\\min}$ = 3600\\,s", "lmin_3600"),
            ("RAASC cache 50 entries", "repl_raasc_default_cache50"), ("RAASC cache 200 entries", "repl_raasc_default_cache200"),
            ("TTL + inv cache 50 entries", "repl_ttl_cache50"), ("TTL + inv cache 200 entries", "repl_ttl_cache200")]
    return rows_table(rows, ["hit", "unsafe", "wrong", "harm", "energy"], [1, 2, 2, 1, 2])


def fl_pooled(n):
    f = a(n, "fl_n").sum()
    if f == 0:
        return "--", "--", "--"
    return (f"{100*a(n,'fl_stale').sum()/f:.1f}", f"{100*a(n,'fl_wrong').sum()/f:.1f}", f"{100*a(n,'fl_unsafe').sum()/f:.1f}")


def T_outage():
    out = [f"Cloud-only & {PM('out_cloud_only','unans',2)} & 0 & n/a & -- & -- & -- & {PM('out_cloud_only','energy',2)}\\\\"]
    rows = [("Class TTL (default)", "out_ttl_default"), ("Class TTL + matched degraded mode (4$\\times$TTL)", "out_ttl_default_deg4"),
            ("TTL tuned cap 15 + inv", "out_ttl_tuned_cap15_inv"), ("TTL tuned cap 15 + inv + degraded", "out_ttl_tuned_cap15_inv_deg4"),
            ("RAASC + inv, no degraded mode", "out_raasc_nodeg")]
    for f in (2, 4, 6, 8):
        rows.append((f"RAASC + inv, combined rule, factor {f}", f"out_raasc_deg{f}"))
    for f in (2, 4, 6, 8):
        rows.append((f"RAASC + inv, strict wrong-intent rule, factor {f}", f"out_raasc_strict{f}"))
    for lab, n in rows:
        st, wr, un = fl_pooled(n)
        out.append(f"{lab} & {PM(n,'unans',2)} & {M(n,'flagged',2)} & {M(n,'unsafe',2)} & {st} & {wr} & {un} & {M(n,'energy',2)}\\\\")
    return "\n".join(out)


def T_shift():
    out = []
    for sh, lab in (("wrongprior", "Wrong prior"), ("sudden", "Sudden change"), ("drift", "Drift")):
        for suf, nm in (("adaptive", "Adaptive rate"), ("prior", "Class prior"), ("ttl_inv", "TTL + inv (default)"), ("ttl_tuned5_inv", "TTL tuned cap 5 + inv")):
            n = f"shift_{sh}_{suf}"
            first = f"\\multirow{{4}}{{*}}{{{lab}}}" if suf == "adaptive" else ""
            out.append(f"{first} & {nm} & {PM(n,'hit',1)} & {PM(n,'unsafe',2)} & {PM(n,'harm',1)} & {M(n,'energy',2)}\\\\")
        out.append("\\midrule")
    return "\n".join(out[:-1])


def T_paired():
    out = []
    comps = [("raasc|ttl_default", "RAASC vs class TTL"), ("raasc_inv|ttl_default_inv", "RAASC + inv vs TTL + inv"),
             ("raasc_inv|ttl_tuned_cap15_inv", "RAASC + inv vs tuned TTL (cap 15) + inv"),
             ("raasc_inv|ttl_tuned_cap5_inv", "RAASC + inv vs tuned TTL (cap 5) + inv"),
             ("raasc_inv|ttl_vd_inv", "RAASC + inv vs TTL (V-D limits) + inv"),
             ("raasc_inv|tau_tuned_cap5_inv", "RAASC + inv vs tuned fixed-$\\tau$ (cap 5) + inv"),
             ("raasc_inv|abl_nocal", "RAASC + inv vs no calibration"), ("raasc_inv|abl_noadapt", "RAASC + inv vs class-prior rate"),
             ("est_hoeff|raasc", "Hoeffding vs Eq.~\\eqref{eq:wrong} (RAASC, no inv)"), ("est_cp|raasc", "Clopper--Pearson vs Eq.~\\eqref{eq:wrong} (no inv)")]
    names = {"hit": "Hit (pts)", "unsafe": "Unsafe (pts)", "harm": "Harm/1k", "energy": "Energy (J)"}
    for key, lab in comps:
        out.append(f"\\multicolumn{{8}}{{@{{}}l}}{{\\textit{{{lab}}}}}\\\\")
        for m in ("hit", "unsafe", "harm", "energy"):
            t = PT[f"{key}|{m}"]
            d = 2 if m != "harm" else 1
            out.append(f"{names[m]} & {sgn(t['delta'],d)} [{sgn(t['lo'],d)}, {sgn(t['hi'],d)}] & {t['dz']:.2f} & {pf(t['p_t'])} & {pf(t['p_w'])} & {pf(t['p_perm'])} & {pf(t['p_holm'])} & {t['wins']}/20\\\\")
    return "\n".join(out)


def T_bins(key="bins_plain", ipw=False):
    out = []
    for r in L[key][4:]:
        def f(x, d=3):
            return "--" if x is None else f"{x:.{d}f}"
        out.append(f"{r['lo']:.2f}--{r['lo']+0.05:.2f} & {r['miss_per_seed']:.0f} & {r['aud_per_seed']:.1f} & {r['dec_per_seed']:.0f} & "
                   f"{f(r['rate_miss'])} & {f(r['rate_aud'])} & {f(r['rate_orc'])} & "
                   f"{r['cov_eq6']:.0f} / {r['cov_H']:.0f} / {r['cov_CP']:.0f} & {r['mean_eq6']:.3f} / {r['mean_H']:.3f} / {r['mean_CP']:.3f}\\\\")
    return "\n".join(out)


def T_deny(tag):
    rows = [("RAASC + inv, no deny-list", f"deny_{tag}_raasc_nolist", None), ("TTL + inv, no deny-list", f"deny_{tag}_ttl_nolist", None)]
    for r in (0.7, 0.9, 1.0):
        for fpr in (0.0, 0.05):
            rows.append((f"RAASC + inv, router $r$={r}, FPR={fpr}", f"deny_{tag}_raasc_r{r}_fp{fpr}", (r, fpr)))
        if r < 1.0:
            rows.append((f"RAASC + inv, $r$={r}, FPR=0, correlated misses", f"deny_{tag}_raasc_r{r}_fp0.0_corr", (r, 0)))
    rows.append(("TTL + inv, router $r$=1, FPR=0", f"deny_{tag}_ttl_r1.0_fp0.0", (1.0, 0.0)))
    out = []
    for lab, n, cfg in rows:
        if cfg is None:
            prec = rec = fpr = "--"
        else:
            tp, fp, fn, tn = (a(n, k).sum() for k in ("tp", "fp", "fn", "tn"))
            prec = f"{100*tp/max(tp+fp,1):.1f}"; rec = f"{100*tp/max(tp+fn,1):.1f}"; fpr = f"{100*fp/max(fp+tn,1):.1f}"
        out.append(f"{lab} & {prec} / {rec} / {fpr} & {M(n,'hit',1)} & {M(n,'bypass',1)} & {M(n,'deny_served',1)} & {M(n,'deny_harm',2)} & {M(n,'harm',1)} & {M(n,'energy',2)}\\\\")
    return "\n".join(out)


def T_cov():
    out = []
    for r in COV:
        def c(k):
            return f"{r[k][0]:.0f} / {r[k][1]:.3f}"
        out.append(f"{r['q']:g} & {r['n']} & {c('eq6')} & {c('eq6_opt')} & {c('hoeff')} & {c('cp')}\\\\")
    return "\n".join(out)


def T_energy():
    h = mean("raasc_inv", "hit") / 100.0
    out = []
    for tc in (0.1, 0.25, 0.5, 1.0, 2.0):
        cells = []
        for ti in (2.0, 4.77, 8.0):
            s = h - tc / ti - 0.02 * h
            cells.append(f"{100*s:.0f}")
        be = [100 * (tc / ti) / (1 - 0.02) for ti in (2.0, 4.77, 8.0)]
        out.append(f"{tc:g} & " + " & ".join(cells) + " & " + " / ".join(f"{b:.1f}" for b in be) + "\\\\")
    return "\n".join(out)


def sav(h, tc=0.25, ti=4.77, eps=0.02):
    return 100 * (h - tc / ti - eps * h)


def covrange(key):
    lo = min(r[key][0] for r in COV); hi = max(r[key][0] for r in COV)
    return f"{lo:.0f}", f"{hi:.0f}"


def share_text():
    d = L["label_share_hi"]
    return f"{100*d['labelled_frac']:.1f}", f"{100*d['miss_share']:.0f}"


from scipy import stats as _st


def below(n, rho):
    return int((a(n, "cost") <= rho).sum())


def pair_desc(x, y, k, lower=True):
    d = a(x, k) - a(y, k)
    t = _st.ttest_1samp(d, 0.0).pvalue
    try:
        w = _st.wilcoxon(d).pvalue
    except Exception:
        w = 1.0
    return d.mean(), t, w, int((d < 0).sum() if lower else (d > 0).sum())


def agreement():
    keys = list(PT.keys())
    allsig = sum(1 for k in keys if PT[k]["p_t"] < .05 and PT[k]["p_w"] < .05 and PT[k]["p_perm"] < .05)
    nonsig = sum(1 for k in keys if PT[k]["p_t"] >= .05 and PT[k]["p_w"] >= .05 and PT[k]["p_perm"] >= .05)
    nonnorm = sum(1 for k in keys if PT[k]["shapiro"] < .05)
    mixed = len(keys) - allsig - nonsig
    return allsig, nonsig, mixed, nonnorm, len(keys)


def fig_budget():
    def co(names, kx="hit", ky="harm"):
        return " ".join(f"({mean(n,kx):.2f},{mean(n,ky):.2f})" for n in names)
    b = [f"budget_{r}" for r in (0.02, 0.05, 0.1, 0.2, 0.4)]
    m = [f"budget_maxsev_{r}" for r in (0.02, 0.05, 0.1, 0.2, 0.4)]
    s = r"""\begin{tikzpicture}
\begin{axis}[width=\columnwidth,height=6.0cm,xlabel={Cache hit rate (\% of queries)},ylabel={Harm per 1,000 queries},
 xmin=10,xmax=75,ymin=0,ymax=185,grid=major,grid style={gray!25},
 legend style={font=\tiny,at={(0.02,0.98)},anchor=north west,draw=none,fill=white,fill opacity=0.85,row sep=-2pt},
 tick label style={font=\scriptsize},label style={font=\footnotesize}]
"""
    s += r"\addplot[blue!70!black,mark=*,thick] coordinates {" + co(b) + "};\n\\addlegendentry{RAASC+inv, five budgets}\n"
    s += r"\addplot[blue!70!black,mark=o,dashed,thick] coordinates {" + co(m) + "};\n\\addlegendentry{RAASC+inv, max-severity weights}\n"
    for n, lab, mk, col in (("ttl_default_inv", "Class TTL + inv (default)", "square*", "gray!70!black"),
                            ("ttl_tuned_cap5_inv", "Tuned TTL, cap 5 + inv", "triangle*", "red!70!black"),
                            ("ttl_tuned_cap15_inv", "Tuned TTL, cap 15 + inv", "diamond*", "orange!80!black"),
                            ("ttl_vd_inv", "TTL (V-D limits) + inv", "pentagon*", "green!50!black")):
        s += r"\addplot[only marks,mark=%s,%s,mark size=2.6pt] coordinates {(%.2f,%.2f)};\n\\addlegendentry{%s}\n" % (mk, col, mean(n, "hit"), mean(n, "harm"), lab) if False else \
            "\\addplot[only marks,mark=%s,%s,mark size=2.6pt] coordinates {(%.2f,%.2f)};\n\\addlegendentry{%s}\n" % (mk, col, mean(n, "hit"), mean(n, "harm"), lab)
    for r, n in zip(("0.02", "0.05", "0.10", "0.20", "0.40"), b):
        s += "\\node[font=\\tiny,anchor=north west] at (axis cs:%.2f,%.2f) {$\\rho{=}%s$};\n" % (mean(n, "hit") + 0.6, mean(n, "harm") - 1.5, r)
    s += "\\end{axis}\n\\end{tikzpicture}"
    return s
