#!/usr/bin/env python3
"""RAASC simulator v2 (single frozen version used for every table of the v5 paper).

Python + NumPy + Numba.  Everything is synthetic.  Embeddings contain explicit
hard-negative "twin" intents (cosine 0.85 / 0.95 / 0.995 to a sibling) so that
high-similarity wrong-intent pairs exist.  No real encoder or clinical data.
"""
import numpy as np
from numba import njit

D = 64
K = 400
NTOP = 40
CLS_MIX = (0.60, 0.25, 0.15)
IC = np.array([30 * 86400.0, 86400.0, 300.0])      # class prior update intervals (s)
SEV = np.array([1.0, 2.0, 5.0])
WEEK = 7 * 86400.0
QRATE = 2.0 / 60.0
PWR, TC, TI, TO = 3.15, 0.25, 4.77, 2.0
NBIN = 10
SMIN = 0.50
CPN = 600


# ----------------------------------------------------------------- workload
def make_workload(seed, shift="matched", deny="none", rate_scale=1.0):
    rng = np.random.default_rng(10_000 + seed)
    cls = rng.choice(3, size=K, p=CLS_MIX)
    topic = np.repeat(np.arange(NTOP), K // NTOP)
    tv = rng.normal(size=(NTOP, D)); tv /= np.linalg.norm(tv, axis=1, keepdims=True)
    nz = rng.normal(size=(K, D)); nz /= np.linalg.norm(nz, axis=1, keepdims=True)
    rho_t = 0.6
    cv = np.sqrt(rho_t) * tv[topic] + np.sqrt(1 - rho_t) * nz
    cv /= np.linalg.norm(cv, axis=1, keepdims=True)
    # hard-negative twins: later intent copies an earlier one with a small perturbation
    order = rng.permutation(K)
    levels = [(0.85, 0.04), (0.93, 0.025), (0.97, 0.015)]
    pos = 0
    twin_of = -np.ones(K, dtype=int)
    for cosv, frac in levels:
        m = int(frac * K)
        for _ in range(m):
            a, b = order[pos], order[pos + 1]
            pos += 2
            if pos + 2 >= K:
                break
            n2 = rng.normal(size=D); n2 -= n2.dot(cv[a]) * cv[a]; n2 /= np.linalg.norm(n2)
            cv[b] = cosv * cv[a] + np.sqrt(1 - cosv ** 2) * n2
            twin_of[b] = a
    cv /= np.linalg.norm(cv, axis=1, keepdims=True)
    # popularity (Zipf 1.1) on a random permutation
    ranks = rng.permutation(K)
    pop = 1.0 / (ranks + 1.0) ** 1.1
    pop /= pop.sum()
    N = int(WEEK * QRATE)
    qt = np.cumsum(rng.exponential(1.0 / QRATE, size=N))
    qt = qt[qt < WEEK]
    N = len(qt)
    qint = rng.choice(K, size=N, p=pop)
    cth = rng.beta(20.0, 1.1, size=N)
    g = rng.normal(size=(N, D))
    g -= (g * cv[qint]).sum(1, keepdims=True) * cv[qint]
    g /= np.linalg.norm(g, axis=1, keepdims=True)
    qv = cth[:, None] * cv[qint] + np.sqrt(1 - cth ** 2)[:, None] * g
    qv /= np.linalg.norm(qv, axis=1, keepdims=True)
    # update processes
    lam = 1.0 / IC[cls] * rate_scale
    mult = np.ones(K)
    if shift == "wrongprior":
        u = rng.random(K)
        mult[u < 0.3] = 10.0
        mult[(u >= 0.3) & (u < 0.6)] = 0.1
    upd_list = []
    for k in range(K):
        r = lam[k] * mult[k]
        if shift in ("sudden", "drift"):
            rmax = r * 10.0
            n = rng.poisson(rmax * WEEK)
            t = np.sort(rng.random(n) * WEEK)
            if shift == "sudden":
                keep = np.where(t < WEEK / 2, rng.random(n) < 0.1, True)
            else:
                f = 1.0 + 9.0 * t / WEEK
                keep = rng.random(n) < f / 10.0
            t = t[keep]
        else:
            n = rng.poisson(r * WEEK)
            t = np.sort(rng.random(n) * WEEK)
        upd_list.append(t)
    off = np.zeros(K + 1, dtype=np.int64)
    off[1:] = np.cumsum([len(x) for x in upd_list])
    upd = np.concatenate(upd_list) if off[-1] > 0 else np.zeros(0)
    upush = rng.random(len(upd))
    # deny category
    isdeny = np.zeros(K, dtype=bool)
    if deny == "uniform":
        isdeny[rng.choice(K, size=40, replace=False)] = True
    elif deny == "rare":
        low = np.argsort(-ranks)[: K // 2]          # least popular half
        isdeny[rng.choice(low, size=10, replace=False)] = True
    # max-severity neighbourhood (plausible target intents, centre cosine >= 0.8)
    S = cv @ cv.T
    sev_max = np.array([SEV[cls[S[i] >= 0.8]].max() for i in range(K)])
    return dict(seed=seed, cls=cls, cv=cv, qt=qt, qint=qint, qv=qv, upd=upd, off=off, upush=upush,
                isdeny=isdeny, sev_max=sev_max, N=N, rng_seed=seed, twin_of=twin_of)


def make_aux(wl, p_out=0.0, eta=0.0, deny_cfg=None):
    rng = np.random.default_rng(777_000 + wl["seed"])
    N = wl["N"]
    ok = rng.random(N) >= p_out          # cloud request for the query
    ok2 = rng.random(N) >= p_out         # cloud request for an audit
    aud_u = rng.random(N)
    lab_u = rng.random(N)
    denied = np.zeros(N, dtype=bool)
    if deny_cfg is not None:
        r, fpr, corr = deny_cfg
        qi = wl["qint"]
        isd = wl["isdeny"][qi]
        if corr:
            blind = rng.random(K) < (1 - r)
            det = ~blind[qi]
        else:
            det = rng.random(N) < r
        fp = rng.random(N) < fpr
        denied = np.where(isd, det, fp)
    return dict(ok=ok, ok2=ok2, aud_u=aud_u, lab_u=lab_u, denied=denied, eta=eta)


def prior_p0(kind="default"):
    sb = SMIN + 0.05 * (np.arange(NBIN) + 0.5)
    p = np.clip(1.0 / (1.0 + np.exp((sb - 0.75) / 0.04)), 0.005, 0.99)
    if kind == "opt":
        p = np.clip(p / 4.0, 0.001, 0.99)
    elif kind == "pess":
        p = np.clip(p * 4.0, 0.0, 0.99)
    elif kind == "flat":
        p = np.full(NBIN, 0.5)
    return p


_cp = None


def cp_table():
    global _cp
    if _cp is None:
        from scipy.stats import beta
        t = np.ones((CPN + 1, CPN + 1))
        for n in range(1, CPN + 1):
            w = np.arange(0, n + 1)
            ub = np.where(w < n, beta.ppf(0.95, w + 1, np.maximum(n - w, 1)), 1.0)
            t[n, : n + 1] = ub
        _cp = t
    return _cp


# ----------------------------------------------------------------- kernels
@njit(cache=True)
def nver(upd, off, k, t):
    return np.searchsorted(upd[off[k]:off[k + 1]], t, side="right")


@njit(cache=True)
def next_push(upd, off, upush, kap, k, tj):
    a = off[k] + np.searchsorted(upd[off[k]:off[k + 1]], tj, side="right")
    b = off[k + 1]
    for i in range(a, b):
        if upush[i] < kap[k]:
            return upd[i]
    return 1e18


@njit(cache=True)
def pwrong_est(bi, mode, cw, cn, cs2, p0, n0, cp, use_cal, s, tau0):
    if use_cal == 0:
        return 0.0 if s >= tau0 else 1.0
    n = cn[bi]
    if n <= 0.0:
        if mode == 0:
            m = p0[bi]
            return min(1.0, m + np.sqrt(m * (1 - m) / (n0 + 1.0)))
        return 1.0
    neff = n * n / cs2[bi]
    rate = cw[bi] / n
    if mode == 0:
        m = (n0 * p0[bi] + rate * neff) / (n0 + neff)
        return min(1.0, m + np.sqrt(m * (1 - m) / (neff + n0 + 1.0)))
    if mode == 1:
        if neff < 1.0:
            return 1.0
        return min(1.0, rate + np.sqrt(np.log(20.0) / (2.0 * neff)))
    # exact Clopper-Pearson (table up to CPN, normal approximation beyond)
    ni = int(round(neff))
    if ni <= 0:
        return 1.0
    wi = int(round(rate * ni))
    if ni <= 600:
        return cp[ni, min(wi, ni)]
    pr = wi / ni
    return min(1.0, pr + 1.645 * np.sqrt(max(pr * (1 - pr), 1e-4) / ni))


@njit(cache=True)
def run_raasc(qt, qint, qv, cls, upd, off, upush, ok, ok2, aud_u, lab_u, denied, isdeny,
              kap, sig, ic, p0, cp,
              rho, lmin, alpha0, n0, eps, degf, est_mode, ipw, use_cal, tau0, adaptive,
              deg_mode, eta, C, label_on_audit):
    N = qt.shape[0]
    Kn = cls.shape[0]
    cemb = np.zeros((C, qv.shape[1]))
    cint = -np.ones(C, dtype=np.int64)
    ct = np.zeros(C)
    cnp = np.full(C, 1e18)
    clast = np.zeros(C)
    valid = np.zeros(C, dtype=np.bool_)
    ni = np.zeros(Kn)
    Ti = np.zeros(Kn)
    lf_t = -np.ones(Kn)
    lf_v = np.zeros(Kn)
    cw = np.zeros(NBIN); cn = np.zeros(NBIN); cs2 = np.zeros(NBIN)
    out = np.zeros(N, dtype=np.int8)
    sint = -np.ones(N, dtype=np.int64)
    ust = np.zeros(N, dtype=np.bool_)
    uwr = np.zeros(N, dtype=np.bool_)
    rsrv = np.zeros(N)
    binlog = -np.ones(N, dtype=np.int8)
    decw = np.zeros(N, dtype=np.bool_)
    lsrc = np.zeros(N, dtype=np.int8)
    naud = 0
    sims = np.zeros(C)
    for n in range(N):
        t = qt[n]
        q = qv[n]
        ki = qint[n]
        # pushed invalidations
        for j in range(C):
            if valid[j] and cnp[j] <= t:
                valid[j] = False
        if denied[n]:
            # bypass cache; purge entries of deny-category intents
            for j in range(C):
                if valid[j] and isdeny[cint[j]]:
                    valid[j] = False
            if ok[n]:
                out[n] = 4
            else:
                out[n] = 3
            continue
        best = -1
        bestR = 1e18
        bests = 0.0
        bestb = -1
        bestp = 0.0
        for j in range(C):
            if not valid[j]:
                continue
            s = 0.0
            for d in range(qv.shape[1]):
                s += cemb[j, d] * q[d]
            if s < SMIN:
                continue
            ij = cint[j]
            c = cls[ij]
            if adaptive:
                lh = (ni[ij] + alpha0) / (Ti[ij] + alpha0 * ic[c])
            else:
                lh = 1.0 / ic[c]
            ps = 1.0 - np.exp(-(1.0 - kap[ij]) * lh * (t - ct[j]))
            bi = int((s - SMIN) / 0.05)
            if bi > NBIN - 1:
                bi = NBIN - 1
            pw = pwrong_est(bi, est_mode, cw, cn, cs2, p0, n0, cp, use_cal, s, tau0)
            pu = ps + pw - ps * pw
            R = pu * sig[ij]
            if R < bestR:
                bestR = R; best = j; bests = s; bestb = bi; bestp = pw
        if best >= 0:
            binlog[n] = bestb
            decw[n] = cint[best] != ki
        if best >= 0 and bestR <= rho:
            ij = cint[best]
            out[n] = 1
            sint[n] = ij
            uwr[n] = ij != ki
            ust[n] = nver(upd, off, ij, t) > nver(upd, off, ij, ct[best])
            rsrv[n] = bestR
            clast[best] = t
            if aud_u[n] < eps and ok2[n]:
                naud += 1
                wr = 1.0 if cint[best] != ki else 0.0
                if lab_u[n] < eta:
                    wr = 1.0 - wr
                wgt = 1.0 / eps if ipw else 1.0
                cw[bestb] += wr * wgt; cn[bestb] += wgt; cs2[bestb] += wgt * wgt
                lsrc[n] = 2
            continue
        if ok[n]:
            out[n] = 0
            # label the candidate for free
            if best >= 0:
                wr = 1.0 if cint[best] != ki else 0.0
                if lab_u[n] < eta:
                    wr = 1.0 - wr
                cw[bestb] += wr; cn[bestb] += 1.0; cs2[bestb] += 1.0
                lsrc[n] = 1
            # rate update
            v = nver(upd, off, ki, t)
            if lf_t[ki] >= 0:
                ni[ki] += v - lf_v[ki]
                Ti[ki] += t - lf_t[ki]
            lf_t[ki] = t; lf_v[ki] = v
            c = cls[ki]
            if adaptive:
                lh = (ni[ki] + alpha0) / (Ti[ki] + alpha0 * ic[c])
            else:
                lh = 1.0 / ic[c]
            life = np.log(1.0 / (1.0 - min(rho / sig[ki], 0.999))) / ((1.0 - kap[ki]) * lh)
            if life >= lmin:
                slot = -1
                for j in range(C):
                    if valid[j] and cint[j] == ki:
                        slot = j; break
                if slot < 0:
                    for j in range(C):
                        if not valid[j]:
                            slot = j; break
                if slot < 0:
                    oldest = 1e18
                    for j in range(C):
                        ij = cint[j]
                        cc = cls[ij]
                        if adaptive:
                            lj = (ni[ij] + alpha0) / (Ti[ij] + alpha0 * ic[cc])
                        else:
                            lj = 1.0 / ic[cc]
                        rs = (1.0 - np.exp(-(1.0 - kap[ij]) * lj * (t - ct[j]))) * sig[ij]
                        if rs > rho and ct[j] < oldest:
                            oldest = ct[j]; slot = j
                    if slot < 0:
                        lru = 1e18
                        for j in range(C):
                            if clast[j] < lru:
                                lru = clast[j]; slot = j
                for d in range(qv.shape[1]):
                    cemb[slot, d] = q[d]
                cint[slot] = ki; ct[slot] = t; clast[slot] = t; valid[slot] = True
                cnp[slot] = next_push(upd, off, upush, kap, ki, t)
        else:
            # link down: degraded mode
            if deg_mode > 0 and best >= 0 and cls[cint[best]] != 2 and bestR <= degf * rho:
                okd = True
                if deg_mode == 2:
                    okd = bestp * sig[cint[best]] <= rho
                if okd:
                    ij = cint[best]
                    out[n] = 2
                    sint[n] = ij
                    uwr[n] = ij != ki
                    ust[n] = nver(upd, off, ij, t) > nver(upd, off, ij, ct[best])
                    rsrv[n] = bestR
                    clast[best] = t
                    continue
            out[n] = 3
    return out, sint, ust, uwr, rsrv, binlog, decw, lsrc, cw, cn, cs2, naud


@njit(cache=True)
def run_ttl(qt, qint, qv, cls, upd, off, upush, ok, denied, isdeny, kap, ttl, tau, degm, C):
    N = qt.shape[0]
    Kn = cls.shape[0]
    cemb = np.zeros((C, qv.shape[1]))
    cint = -np.ones(C, dtype=np.int64)
    ct = np.zeros(C)
    cnp = np.full(C, 1e18)
    clast = np.zeros(C)
    valid = np.zeros(C, dtype=np.bool_)
    out = np.zeros(N, dtype=np.int8)
    sint = -np.ones(N, dtype=np.int64)
    ust = np.zeros(N, dtype=np.bool_)
    uwr = np.zeros(N, dtype=np.bool_)
    for n in range(N):
        t = qt[n]
        q = qv[n]
        ki = qint[n]
        for j in range(C):
            if valid[j] and cnp[j] <= t:
                valid[j] = False
        if denied[n]:
            for j in range(C):
                if valid[j] and isdeny[cint[j]]:
                    valid[j] = False
            out[n] = 4 if ok[n] else 3
            continue
        best = -1; bests = -1.0
        bestd = -1; bestds = -1.0
        for j in range(C):
            if not valid[j]:
                continue
            s = 0.0
            for d in range(qv.shape[1]):
                s += cemb[j, d] * q[d]
            if s < tau:
                continue
            c = cls[cint[j]]
            age = t - ct[j]
            if age <= ttl[c] and s > bests:
                bests = s; best = j
            if degm > 0.0 and c != 2 and age <= degm * ttl[c] and s > bestds:
                bestds = s; bestd = j
        if best >= 0:
            ij = cint[best]
            out[n] = 1; sint[n] = ij; uwr[n] = ij != ki
            ust[n] = nver(upd, off, ij, t) > nver(upd, off, ij, ct[best])
            clast[best] = t
            continue
        if ok[n]:
            out[n] = 0
            c = cls[ki]
            if ttl[c] > 0.0:
                slot = -1
                for j in range(C):
                    if valid[j] and cint[j] == ki:
                        slot = j; break
                if slot < 0:
                    for j in range(C):
                        if not valid[j]:
                            slot = j; break
                if slot < 0:
                    oldest = 1e18
                    for j in range(C):
                        cc = cls[cint[j]]
                        if (t - ct[j]) > ttl[cc] and ct[j] < oldest:
                            oldest = ct[j]; slot = j
                    if slot < 0:
                        lru = 1e18
                        for j in range(C):
                            if clast[j] < lru:
                                lru = clast[j]; slot = j
                for d in range(qv.shape[1]):
                    cemb[slot, d] = q[d]
                cint[slot] = ki; ct[slot] = t; clast[slot] = t; valid[slot] = True
                cnp[slot] = next_push(upd, off, upush, kap, ki, t)
        else:
            if bestd >= 0:
                ij = cint[bestd]
                out[n] = 2; sint[n] = ij; uwr[n] = ij != ki
                ust[n] = nver(upd, off, ij, t) > nver(upd, off, ij, ct[bestd])
                clast[bestd] = t
            else:
                out[n] = 3
    return out, sint, ust, uwr


# ----------------------------------------------------------------- drivers
INF = 1e18
KAP_INV = np.array([0.5, 0.5, 0.0])


def kap_vec(wl, inv, kmult=1.0):
    k = KAP_INV[wl["cls"]] * kmult if inv else np.zeros(K)
    return np.ascontiguousarray(k, dtype=np.float64)


def sim_raasc(wl, aux, inv=True, rho=0.05, est="eq6", ipw=0, use_cal=1, tau0=0.8, adaptive=1,
              deg=0, degf=4.0, eps=0.02, prior="default", maxsev=False, lmin=30.0, C=100,
              kmult=1.0):
    kap = kap_vec(wl, inv, kmult)
    sig = wl["sev_max"] if maxsev else SEV[wl["cls"]]
    mode = {"eq6": 0, "hoeff": 1, "cp": 2}[est]
    res = run_raasc(wl["qt"], wl["qint"], wl["qv"], wl["cls"], wl["upd"], wl["off"], wl["upush"],
                    aux["ok"], aux["ok2"], aux["aud_u"], aux["lab_u"], aux["denied"], wl["isdeny"],
                    kap, np.ascontiguousarray(sig, dtype=np.float64), IC, prior_p0(prior), cp_table(),
                    rho, lmin, 2.0, 8.0, eps, degf, mode, ipw, use_cal, tau0, adaptive, deg,
                    aux["eta"], C, 1)
    return dict(zip(["out", "sint", "ust", "uwr", "rsrv", "binlog", "decw", "lsrc", "cw", "cn", "cs2", "naud"], res))


def sim_ttl(wl, aux, inv=False, ttl=(7 * 86400.0, 6 * 3600.0, 0.0), tau=0.8, degm=0.0, C=100):
    kap = kap_vec(wl, inv)
    res = run_ttl(wl["qt"], wl["qint"], wl["qv"], wl["cls"], wl["upd"], wl["off"], wl["upush"],
                  aux["ok"], aux["denied"], wl["isdeny"], kap, np.array(ttl, dtype=np.float64),
                  tau, degm, C)
    r = dict(zip(["out", "sint", "ust", "uwr"], res))
    r["naud"] = 0
    return r


def metrics(wl, aux, r, eps_extra=0):
    out = r["out"]; N = len(out)
    cls = wl["cls"]; qi = wl["qint"]
    hit = out == 1; fl = out == 2; un = out == 3; byp = out == 4
    unsafe = (r["ust"] | r["uwr"])
    nh = max(hit.sum(), 1)
    sev_true = SEV[cls[qi]]
    sev_srv = np.where(r["sint"] >= 0, SEV[cls[np.maximum(r["sint"], 0)]], 0.0)
    harm = 1000.0 * (sev_true * (unsafe & hit)).sum() / N
    harm_s = 1000.0 * (sev_srv * (unsafe & hit)).sum() / N
    cost = (sev_srv * (unsafe & hit)).sum() / nh
    m = dict(hit=100.0 * hit.mean(), unsafe=100.0 * (unsafe & hit).sum() / nh,
             stale=100.0 * (r["ust"] & hit).sum() / nh, wrong=100.0 * (r["uwr"] & hit).sum() / nh,
             harm=harm, harm_s=harm_s, cost=cost, flagged=100.0 * fl.mean(), unans=100.0 * un.mean(),
             bypass=100.0 * byp.mean())
    nf = fl.sum()
    m["fl_n"] = nf
    m["fl_stale"] = (r["ust"] & fl).sum(); m["fl_wrong"] = (r["uwr"] & fl).sum()
    m["fl_unsafe"] = (unsafe & fl).sum()
    if "rsrv" in r and hit.any():
        m["rbar"] = r["rsrv"][hit].mean()
    else:
        m["rbar"] = np.nan
    # time and energy
    tm = np.where(out == 1, TC, np.where(out == 0, TC + TI, np.where(out == 4, TC + TI, TC + TO)))
    # bypass of a denied/false-positive query still pays the lookup-free cloud path
    tm = np.where(out == 4, TI, tm)
    answered = out != 3
    m["lat"] = tm[answered].mean()
    energy = PWR * (tm.sum() + r["naud"] * TI) / N
    m["energy"] = energy
    # deny category metrics
    isd = wl["isdeny"][qi]
    if isd.any():
        ds = isd & hit
        m["deny_share"] = 100.0 * isd.sum() / N
        m["deny_served"] = 100.0 * ds.sum() / isd.sum()
        m["deny_unsafe_n"] = (unsafe & ds).sum()
        m["deny_harm"] = 1000.0 * 10.0 * (unsafe & ds).sum() / N
        den = aux["denied"]
        m["tp"] = (den & isd).sum(); m["fp"] = (den & ~isd).sum()
        m["fn"] = (~den & isd).sum(); m["tn"] = (~den & ~isd).sum()
    # shares of served classes
    if hit.any():
        sc = cls[r["sint"][hit]]
        m["share_static"] = 100.0 * (sc == 0).mean()
        m["unsafe_static"] = 100.0 * (unsafe[hit][sc == 0]).mean() if (sc == 0).any() else np.nan
        m["unsafe_semi"] = 100.0 * (unsafe[hit][sc == 1]).mean() if (sc == 1).any() else np.nan
    return m


def cloud_only(wl, aux):
    ok = aux["ok"]
    tm = np.where(ok, TI, TO)
    N = len(tm)
    return dict(hit=np.nan, unsafe=np.nan, harm=np.nan, lat=TI, energy=PWR * tm.mean(),
                unans=100.0 * (~ok).mean())


if __name__ == "__main__":
    import time, sys
    wl = make_workload(0)
    aux = make_aux(wl)
    t0 = time.time()
    r = sim_raasc(wl, aux)
    print("raasc", metrics(wl, aux, r)["hit"], time.time() - t0)
    t0 = time.time(); r = sim_raasc(wl, aux); print("2nd", time.time() - t0)
    r = sim_ttl(wl, aux)
    m = metrics(wl, aux, r); print("ttl", m["hit"], m["unsafe"], m["harm"])
