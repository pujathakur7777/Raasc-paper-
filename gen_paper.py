import re, sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/3d193717-eb3f-5d25-a3fd-e765519136bb/scratchpad/sim")
import tabs as T

BASE = "/tmp/claude-0/-home-claude/3d193717-eb3f-5d25-a3fd-e765519136bb/scratchpad/"
v4 = open(BASE + "paper/raasc_v4.tex").read()

i_setup = v4.index("%==================================================================\n\\section{Experimental Setup}")
i_bib = v4.index("%==================================================================\n\\begin{thebibliography}")
head = v4[:i_setup]
bib = v4[i_bib:]


def rep(s, old, new):
    assert old in s, "missing: " + old[:70]
    return s.replace(old, new, 1)


# ---------------------------------------------------------------- abstract
a0 = head.index("\\textit{\\textbf{Abstract}---}%")
a1 = head.index("\\par\\smallskip")
abstract = r"""\textit{\textbf{Abstract}---}%
A semantic cache at the network edge lets a voice-assistant pipeline answer repeated questions locally, saving modelled energy and time and surviving link outages. For health information the cache also affects safety: a reused answer may be outdated, and a loosely matched question may be a different question. Existing designs use a fixed per-class time-to-live (TTL) and one global similarity threshold; neither adapts. We introduce RAASC, an edge-side semantic-cache policy that serves an entry only if an \emph{estimated} severity-weighted risk score fits an operator-set budget. The score combines the probability of an outdated answer, from an update rate learned online from cloud version tags, and of a wrong-intent match, from online calibration of cosine similarity. A clinical deny-list, event-driven invalidation and a flagged degraded mode complete the design. We show that the rule induces an adaptive per-intent reuse limit and state the assumptions under which the budget bounds the \emph{expected} estimated risk. All results come from one frozen, reproducible synthetic simulator with explicit hard-negative (near-duplicate) intents, 20 test seeds and baselines tuned on 10 separate validation seeds. At the default budget RAASC + inv serves @@T.M('raasc_inv','hit')@@\,\% of queries from the cache with @@T.M('raasc_inv','unsafe',2)@@\,\% unsafe cached answers (harm @@T.M('raasc_inv','harm')@@ per 1,000 queries); the default class-aware TTL cache reaches @@T.M('ttl_default','hit')@@\,\% hits but @@T.M('ttl_default','unsafe',2)@@\,\% unsafe answers (harm @@T.M('ttl_default','harm')@@). Against a TTL cache tuned to a harm cap of 15, RAASC gives @@T.sgn(T.PT['raasc_inv|ttl_tuned_cap15_inv|hit']['delta'],1)@@ points of hit rate at statistically indistinguishable harm, and it dominates TTL tuned to a cap of 5 at a looser budget only in the hit--harm frontier sense. The analysis is also sobering: near-duplicate intents make wrong-intent hits the main failure (@@T.M('raasc_inv','wrong',2)@@ of @@T.M('raasc_inv','unsafe',2)@@ points of unsafe share), the realised served-class cost is @@'%.2f' % (T.mean('budget_0.05','cost')/T.mean('budget_0.05','rbar'))@@ times the mean estimated risk at the default budget (so the conservativeness assumption fails), and a 5\,\% label-noise rate in the cloud's intent identifiers collapses the hit rate to @@T.M('labelnoise_0.05','hit')@@\,\%. With a 10\,\% link outage a strict degraded mode that checks wrong-intent risk separately keeps flagged answers at @@T.fl_pooled('out_raasc_strict4')[2]@@\,\% unsafe, against @@T.fl_pooled('out_raasc_deg4')[2]@@\,\% for the combined rule. The workload is synthetic, the work is a simulation-and-methodology study of a cache layer rather than an end-to-end voice assistant, it has not been clinically validated, and no calibration with real labelled sentence pairs is reported (Section~\ref{sec:status}).
"""
head = head[:a0] + abstract + head[a1:]

# ---------------------------------------------------------------- contributions / intro
head = rep(head, r"""\item an extended evaluation that relates the realised cost of served answers to the budget, stress-tests the calibration prior, measures the selection bias of the calibration labels, audits flagged answers, evaluates the deny-list with imperfect router recall, and adds an unlabelled probe on real medical questions (Sections~\ref{sec:cost}--\ref{sec:probe}).""",
r"""\item an evaluation on one frozen simulator that includes hard-negative intents and compares against baselines tuned on separate validation seeds; it relates the realised cost to the budget, runs Hoeffding and exact-binomial calibrators and a propensity-weighted calibrator inside the cache, tests label noise, measures the selection bias of the calibration labels, evaluates a strict degraded mode and a deny-list with false positives, correlated misses and rare intents, and adds an unlabelled probe on real medical questions (Sections~\ref{sec:budget}--\ref{sec:probe}).""")
head = rep(head, "a seeded evaluation against a class-aware TTL baseline and further baselines, with paired statistical tests, an ablation, a stress test of the rate estimator and an outage test (Sections~\\ref{sec:setup} and~\\ref{sec:results});",
           "a seeded evaluation against class-aware, matched-limit and validation-tuned TTL and threshold baselines, with paired statistical tests (t, Wilcoxon, permutation, Holm), an ablation, a stress test of the rate estimator and an outage test (Sections~\\ref{sec:setup} and~\\ref{sec:results});")

# ---------------------------------------------------------------- design edits
head = rep(head, "the evaluation follows this assumption and does not simulate label noise.", "the main evaluation follows this assumption, and \\sref{sec:ablation} then injects identifier errors as label noise.")
head = rep(head, "\\sref{sec:baselines} compares this with plain LRU, LFU and ARC~\\cite{megiddo2003}.", "Alternative replacement rules such as LFU or ARC~\\cite{megiddo2003} were not compared in this version; \\sref{sec:ablation} varies the cache size instead.")
head = rep(head, "its effect on individual intents was not evaluated.", "\\sref{sec:ablation} sweeps it.")
head = rep(head, "A variant in which the wrong-intent estimate must pass its own strict threshold, independently of the staleness relaxation, is a natural safeguard but was not evaluated here.",
           "A strict variant, in which the wrong-intent estimate must pass its own threshold $\\pwrong\\sigma_c\\le\\rho$ independently of the staleness relaxation, is evaluated in \\sref{sec:flagged}.")
head = rep(head, "so those tables report the risk rule alone; \\sref{sec:denyeval} evaluates the deny-list separately, with router recall as the only imperfection modelled (precision, false positives and correlated misses are not modelled).",
           "so the main tables report the risk rule alone; \\sref{sec:denyeval} evaluates the deny-list separately on workloads with a deny category (uniformly chosen and rare), with router recall, false positives and correlated misses.")
head = rep(head, "The workload used for the main tables does not exercise it, so", "The workload used for the main tables does not exercise it, so")
head = rep(head, "The cache-level experiments use \\eqref{eq:wrong}, not this bound, so they measure the realised unsafe rate and do not verify (A4).",
           "The main cache-level experiments use \\eqref{eq:wrong}; \\sref{sec:ablation} also runs the Hoeffding and the exact bound inside the cache. Cache-level experiments measure the realised unsafe rate and do not by themselves verify (A4).")
head = rep(head, "\\sref{sec:coverage} compares \\eqref{eq:wrong}, the Hoeffding bound and the exact binomial bound as estimators in isolation, and \\sref{sec:bias} repeats the comparison on the labels that the cache itself produces.",
           "\\sref{sec:coverage} compares \\eqref{eq:wrong}, the Hoeffding bound and the exact binomial bound as estimators in isolation, and \\sref{sec:bias} repeats the comparison on the labels that the cache itself produces, with and without propensity weighting.")
head = rep(head, "For the static and semi-static classes the limits are shorter than the 7\\,d and 6\\,h of the TTL baseline, which is consistent with the lower unsafe rate of \\sref{sec:results}; since the simulated update rates equal the class priors (\\sref{sec:ablation}), the shorter limits account for most of that reduction, as a TTL cache with exactly these limits shows (\\sref{sec:baselines}).",
           "For the static and semi-static classes the limits are shorter than the 7\\,d and 6\\,h of the default TTL baseline; \\sref{sec:baselines} compares RAASC with a TTL cache that uses exactly these limits and with TTL caches tuned on validation seeds.")
head = rep(head, "so the audit rate should be lowered only once the high-similarity bins hold enough labels. At $h=0.456$ (RAASC + inv hit rate of \\tref{tab:main}), $\\varepsilon=0.02$ and $t_i=4.77$\\,s the modelled saving is 39\\,\\% for a lookup time of 0.25\\,s, 34\\,\\% for 0.5\\,s and 24\\,\\% for 1\\,s, and vanishes only at about 2.1\\,s.",
           "so the audit rate should be lowered only once the high-similarity bins hold enough labels. At $h=@@'%.3f' % (T.mean('raasc_inv','hit')/100)@@$ (RAASC + inv hit rate of \\tref{tab:main}), $\\varepsilon=0.02$ and $t_i=4.77$\\,s the modelled saving is @@'%.0f' % T.sav(T.mean('raasc_inv','hit')/100,0.25)@@\\,\\% for a lookup time of 0.25\\,s, @@'%.0f' % T.sav(T.mean('raasc_inv','hit')/100,0.5)@@\\,\\% for 0.5\\,s and @@'%.0f' % T.sav(T.mean('raasc_inv','hit')/100,1.0)@@\\,\\% for 1\\,s, and vanishes at about @@'%.1f' % (4.77*T.mean('raasc_inv','hit')/100*0.98)@@\\,s (\\tref{tab:energy}).")
head = rep(head, "at $h=0.46$, $\\varepsilon=0.02$, misses supply at most about 98\\,\\% of all labels (only misses with a candidate above the floor are labelled, mostly in the lower-similarity bins)",
           "in the simulation misses supply @@T.share_text()[1]@@\\,\\% of the labels above cosine 0.80, where only @@T.share_text()[0]@@\\,\\% of the decisions are labelled (only misses with a candidate above the floor are labelled, mostly in the lower-similarity bins)")
head = rep(head, "Third, estimators \\eqref{eq:rate} and \\eqref{eq:wrong} are not conservative by construction: \\eqref{eq:rate} is a posterior mean, and \\sref{sec:coverage} shows that the coverage of \\eqref{eq:wrong} stays below 90\\,\\% in all tested settings.",
           "Third, estimators \\eqref{eq:rate} and \\eqref{eq:wrong} are not conservative by construction: \\eqref{eq:rate} is a posterior mean, \\sref{sec:coverage} shows that the coverage of \\eqref{eq:wrong} stays below 90\\,\\% in all isolated settings, and \\sref{sec:budget} and \\sref{sec:bias} show that in the cache the realised cost exceeds the mean estimated risk at several budgets.")
head = rep(head, "In the experiments the realised unsafe rate is measured (\\tref{tab:main}), not guaranteed; \\sref{sec:cost} compares the realised served-class cost per answer with the budget, and \\sref{sec:bias} measures the selection bias named above.",
           "In the experiments the realised unsafe rate is measured (\\tref{tab:main}), not guaranteed; \\sref{sec:budget} compares the realised served-class cost per answer with the budget and with the mean estimated risk, and \\sref{sec:bias} measures the selection bias named above.")

# ---------------------------------------------------------------- middle part
mid = r"""%==================================================================
\section{Experimental Setup}\label{sec:setup}
\textbf{Implementation.} The simulator \texttt{raasc\_sim2.py} (Python, NumPy and Numba; one file) implements the gateway logic and a seeded workload generator, and \texttt{run\_all.py} runs every experiment of this paper; \texttt{coverage\_study.py} produces \tref{tab:cov}. It runs the policies of \sref{sec:policies} on identical traffic and reports hit, flagged, unanswered, stale, wrong-intent, unsafe, severity-weighted harm, latency and modelled energy per seed. Everything is synthetic: no patient data, clinical records or human subjects were used.

\textbf{Workload.} The generator is trace-free. One simulated week has 400 intents in 40 topics of 64-dimensional synthetic vectors (cosine between intents of one topic about 0.6, between topics about 0), Zipf popularity ($s=1.1$) and a class mix of 60/25/15\,\% (static/semi-static/volatile) assigned independently of topic. \emph{Hard negatives:} 32 intents are near-copies of a sibling intent (cosine 0.85, 0.93 or 0.97 to it; 16, 10 and 6 intents), chosen independently of volatility class, so that pairs of different intents with high cosine exist, including pairs that cross classes. A query is the intent vector rotated by an angle whose cosine is Beta(20, 1.1)-distributed (mean 0.948); two queries of one intent then have a mean cosine of 0.90 (5th percentile 0.78 in seed 0), which matches the paraphrase similarity reported in~\cite{montoya2025}. Queries arrive at 2 per minute (about 20,100 per seed) and the cache holds 100 entries. Updates are Poisson with mean intervals of 30\,d, 1\,d and 5\,min. Lookup time (0.25\,s), cloud time (4.77\,s) and power (3.15\,W) are the measurements of~\cite{montoya2025}; failed cloud requests time out after 2\,s. Severity weights are 1, 2, 5; $\smin=0.50$; $\varepsilon=0.02$; $\Lmin=30$\,s; $\alpha_0=2$; $n_0=8$; push coverage is 0.5 for static and semi-static and 0 for volatile intents; degraded mode accepts risks up to $4\rho$. The calibration prior is \eqref{eq:prior} (\tref{tab:prior}). Severity weights, intervals and push coverage are assumptions that clinical governance would replace. The twin construction is a stand-in for the high-lexical-overlap pairs that real sentence encoders produce; it is not calibrated to any real encoder (\sref{sec:probe}).

\textbf{Estimator stress workloads.} For \sref{sec:shift} only the update process is changed, and all policies see the same updates within a variant: (i) mis-specified priors, in which 30\,\% of the intents change 10 times faster and 30\,\% 10 times more slowly than the class prior; (ii) a sudden change, in which all update rates are multiplied by 10 at the middle of the week; and (iii) a drift, in which all rates grow linearly from 1 to 10 times the prior over the week.

\textbf{Deny-category workloads.} For \sref{sec:denyeval}, either 40 intents drawn uniformly (@@'%.1f' % T.mean('deny_uniform_raasc_nolist','deny_share')@@\,\% of the queries, since popularity is unequal) or 10 intents drawn from the less popular half (@@'%.1f' % T.mean('deny_rare_raasc_nolist','deny_share')@@\,\% of the queries) form a deny category. Their harm is weighted with a severity of 10, a \emph{synthetic stress parameter} and not a clinical weight. The router flags a deny query with probability $r$ (recall) and an ordinary query with probability FPR; in the correlated variant each deny intent is missed entirely with probability $1-r$ (a terminology change that hides a whole intent), which keeps the same average recall.

\subsection{Policies compared}\label{sec:policies}
\emph{Cloud-only} sends every query to the cloud. The \emph{class-aware TTL cache} keeps static, semi-static and volatile answers for 7\,d, 6\,h and 0\,s (volatile answers are never cached) with a global cosine threshold of 0.80 (the assumed defaults of the earlier versions of this work); \emph{+ inv} adds event-driven invalidation with the push coverage of RAASC. The \emph{fixed-$\tau$ semantic cache} has no TTL. The \emph{V-D TTL} cache uses the reuse limits of \sref{sec:reuse} (1.5\,d and 36\,min without invalidation, 3.1\,d and 73\,min with invalidation) and $\tau=0.80$. \textbf{Tuned baselines:} on 10 validation seeds (100--109), disjoint from the 20 test seeds (0--19), we searched a grid of $\tau\in\{0.60,\dots,0.95\}$ (step 0.05), static TTL $\in\{1,3,7,14\}$\,d and semi-static TTL $\in\{1,3,6,12\}$\,h (128 settings) for the TTL cache, and $\tau$ alone for the fixed-$\tau$ cache, each with and without invalidation. The selection rule was fixed in advance: the setting with the highest validation hit rate whose mean validation harm does not exceed a cap of 5 or of 15 per 1,000 queries (the setting with the lowest harm if none qualifies). The selected settings are in \tref{tab:tuned}. \textbf{RAASC} is the proposed rule without invalidation (push coverage zero in \eqref{eq:stale}, \eqref{eq:admit}, \eqref{eq:amax}); \emph{RAASC + inv} uses the push coverage above. RAASC itself was \emph{not} tuned: $\rho=0.05$ was fixed in advance and other budgets are reported in \sref{sec:budget}. All policies see the same queries, update events and link states for each seed.

\subsection{Metrics and statistics}\label{sec:metrics}
\emph{Hit} is the share of all queries answered from the cache without a flag. \emph{Unsafe} is the share of cache-served answers that are stale or belong to a different intent (\emph{Stale} and \emph{Wrong} are its two parts, which can overlap). \emph{Harm} is the severity-weighted unsafe count per 1,000 queries using the severity of the \emph{true intent}; Eq.~\eqref{eq:cost} and Proposition~\ref{prop:cond} instead use the severity of the \emph{served entry's class} (Harm$_s$ and the realised cost of \sref{sec:budget}). Denominators differ (served answers vs.\ all queries) and are stated in every caption. Modelled energy is the mean over all queries of $P\cdot t$, including audits and timeouts; latency and energy are model outputs of the constant-power model, not hardware measurements, and are coupled by construction.

Intervals are mean $\pm$ Student-$t$ 95\,\% half-widths over the 20 test seeds (quantile 2.093). Because all policies share each seed's traffic, comparisons use per-seed paired differences with: the mean difference and its Student-$t$ interval, $d_z$, the paired $t$-test, the Wilcoxon signed-rank test, a sign-flip permutation test (20,000 flips), and the number of seeds in which the first policy is better. Normality of the paired differences is rejected (Shapiro--Wilk $p<0.05$) in @@T.agreement()[3]@@ of @@T.agreement()[4]@@ tests, which is why the non-parametric tests are shown. Holm's correction is applied to the \emph{family of the @@T.agreement()[4]@@ tests of \tref{tab:paired}} (ten comparisons, four metrics each) using the $t$-test $p$-values. A non-significant difference is not evidence of equivalence: no equivalence margin was specified.

\subsection{Reproducibility}\label{sec:repro}
All tables of this paper come from \emph{one frozen version} of the simulator, identified by the SHA-256 digest \texttt{@@T.META['sha256_raasc_sim2'][:32]@@\-@@T.META['sha256_raasc_sim2'][32:]@@} of \texttt{raasc\_sim2.py} (Python @@T.META['python']@@, NumPy @@T.META['numpy']@@). \tref{tab:repro} maps every table to its experiment, seeds and configuration; raw per-seed metrics of every configuration are stored in \texttt{results.json}. The estimator-coverage study (\tref{tab:cov}) uses seed 0. The probe on real questions (\tref{tab:probe}) was run in an earlier stage of this work with a separate script and the WordLlama encoder; its weights could not be downloaded in the final environment, so it was not re-run and is the only result not produced by the frozen code.

\begin{table}[t]
\centering
\caption{Table-to-run map (all runs: raasc\_sim2.py, digest above; test seeds 0--19, validation seeds 100--109)}\label{tab:repro}
\scriptsize
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{}p{0.2\columnwidth}p{0.74\columnwidth}@{}}
\toprule
Table / figure & Experiment (run\_all.py configuration prefix)\\
\midrule
\tref{tab:tuned} & validation-seed grid search (\texttt{grid\_*}, \texttt{tuned})\\
\tref{tab:main} & \texttt{ttl\_*, tau\_*, raasc, raasc\_inv}, 0\,\% outage\\
\tref{tab:budget}, \fref{fig:budget} & \texttt{budget\_*, budget\_maxsev\_*}\\
\tref{tab:abl} & \texttt{abl\_*, est\_*, eps\_*, prior\_*, labelnoise\_*, kappa\_*, lmin\_*, repl\_*}\\
\tref{tab:outage} & \texttt{out\_*}, 10\,\% outage, independent request failures\\
\tref{tab:paired} & paired statistics over the above (\texttt{PT} in results.json)\\
\tref{tab:shift} & \texttt{shift\_*}\\
\tref{tab:bins} & label-source bookkeeping of \texttt{raasc\_inv} runs (\texttt{bins\_*})\\
\tref{tab:deny}, \tref{tab:deny2} & \texttt{deny\_uniform\_*, deny\_rare\_*}\\
\tref{tab:cov} & \texttt{coverage\_study.py}, seed 0\\
\tref{tab:limits}, \tref{tab:wrongeff}, \tref{tab:energy} & closed-form (Eq.~\eqref{eq:amax}, \eqref{eq:energy})\\
\bottomrule
\end{tabular}
\end{table}

%==================================================================
\section{Experimental Results}\label{sec:results}
All figures hold for the synthetic workload of \sref{sec:setup} only. Energy values are modelled estimates. Seed-to-seed variation is large (the standard deviation of the RAASC + inv hit rate over seeds is @@'%.1f' % T.a('raasc_inv','hit').std(ddof=1)@@ points), because the placement of the near-duplicate intents among the popular intents differs between seeds; intervals therefore reflect workload variance and should not be read as model error.

\subsection{Main comparison}\label{sec:main}
\tref{tab:main} compares the policies at the defaults. The default class-aware TTL cache has the highest hit rate of the safe-looking policies (@@T.M('ttl_default','hit')@@\,\%) but serves @@T.M('ttl_default','unsafe',2)@@\,\% unsafe answers (harm @@T.M('ttl_default','harm')@@). RAASC (without invalidation) lowers the unsafe share to @@T.M('raasc','unsafe',2)@@\,\% and harm to @@T.M('raasc','harm')@@ ($-$@@'%.0f' % (100*(1-T.mean('raasc','harm')/T.mean('ttl_default','harm')))@@\,\%; paired tests of \sref{sec:paired}), but it does so with @@T.sgn(T.PT['raasc|ttl_default|hit']['delta'],1)@@ points of hit rate and with higher modelled energy (@@T.M('raasc','energy',2)@@ vs @@T.M('ttl_default','energy',2)@@\,J). The fixed-threshold semantic caches serve about a fifth of their cached answers wrongly, because nothing retires outdated answers and near-duplicate intents are served at the threshold, and tuning the threshold alone cannot bring them near the harm cap (best validation harm @@'%.0f' % T.L['tuned']['tau_inv0_cap5.0'][2]@@).

The fair comparison is with TTL caches tuned on separate validation seeds. A TTL cache tuned to a harm cap of 5 is safe (harm @@T.M('ttl_tuned_cap5_inv','harm')@@) but answers only @@T.M('ttl_tuned_cap5_inv','hit')@@\,\% of the queries; tuned to a cap of 15 it reaches @@T.M('ttl_tuned_cap15_inv','hit')@@\,\% hits at harm @@T.M('ttl_tuned_cap15_inv','harm')@@. RAASC + inv at the default budget has @@T.M('raasc_inv','hit')@@\,\% hits at harm @@T.M('raasc_inv','harm')@@: @@T.sgn(T.PT['raasc_inv|ttl_tuned_cap15_inv|hit']['delta'],1)@@ points of hit rate against the cap-15 baseline (paired $p=@@'%.3f' % T.PT['raasc_inv|ttl_tuned_cap15_inv|hit']['p_t']@@$, not significant after Holm's correction, $p_{\mathrm{Holm}}=@@'%.2f' % T.PT['raasc_inv|ttl_tuned_cap15_inv|hit']['p_holm']@@$) and a harm difference of @@T.sgn(T.PT['raasc_inv|ttl_tuned_cap15_inv|harm']['delta'],1)@@ that is not significant. Against the cap-5 baseline it has @@T.sgn(T.PT['raasc_inv|ttl_tuned_cap5_inv|hit']['delta'],1)@@ points of hit rate but also @@T.sgn(T.PT['raasc_inv|ttl_tuned_cap5_inv|harm']['delta'],1)@@ more harm (significant), so the two are not safety-matched. The honest summary is that RAASC's advantage over a validation-tuned class TTL cache is a modest, non-significant gain in the hit--harm trade-off at the default budget, visible mainly in the frontier of \fref{fig:budget}, together with the operational benefit that one budget replaces a grid of TTLs and a threshold. The V-D TTL cache, which uses RAASC's own reuse limits but a global threshold of 0.80, is not safer than RAASC + inv here (harm @@T.M('ttl_vd_inv','harm')@@, difference not significant after Holm) and has @@'%.1f' % abs(T.PT['raasc_inv|ttl_vd_inv|hit']['delta'])@@ points more hits, because it also serves near-duplicate intents above 0.80.

The composition of the unsafe answers differs from a workload without hard negatives: of the @@T.M('raasc_inv','unsafe',2)@@\,\% unsafe answers of RAASC + inv, @@T.M('raasc_inv','wrong',2)@@ points are wrong-intent hits and only @@T.M('raasc_inv','stale',2)@@ points are stale hits (the two overlap slightly). Unsafe rates are @@T.M('raasc_inv','unsafe_static',1)@@\,\% of the static and @@T.M('raasc_inv','unsafe_semi',1)@@\,\% of the semi-static answers served; @@T.M('raasc_inv','share_static',0)@@\,\% of the served answers are static. Invalidation lowers RAASC's stale share (@@T.M('raasc','stale',2)@@ to @@T.M('raasc_inv','stale',2)@@\,\%) but not its wrong-intent share, so invalidation is not by itself a sufficient safety measure once near-duplicates exist.

\begin{table*}[t]
\centering
\caption{Policy comparison at 0\,\% outage (100 entries; mean $\pm$ 95\,\% CI over 20 test seeds; Hit: \% of all queries; Unsafe, Stale, Wrong: \% of cache-served answers; Harm: severity-weighted unsafe answers per 1,000 queries, true-intent severity; Energy: modelled; single frozen simulator)}\label{tab:main}
\footnotesize
\begin{tabular}{@{}lcccccc@{}}
\toprule
Policy & Hit \% & Unsafe \% & Stale \% & Wrong \% & Harm/1k & Energy (J)\\
\midrule
@@T.T_main()@@
\bottomrule
\end{tabular}
\end{table*}

\begin{table}[t]
\centering
\caption{Baseline settings selected on the 10 validation seeds (validation mean hit \% and harm per 1,000 queries); cap: maximum allowed validation harm}\label{tab:tuned}
\scriptsize
\setlength{\tabcolsep}{2pt}
\begin{tabular}{@{}llcc@{}}
\toprule
Baseline & Selected setting & Hit & Harm\\
\midrule
@@T.T_tuned()@@
\bottomrule
\end{tabular}
\end{table}

\subsection{Risk budget and realised cost}\label{sec:budget}
The budget is the main operating knob of RAASC. \fref{fig:budget} and \tref{tab:budget} show the five values that were run (no others were tried), together with a variant that weights each candidate by the \emph{maximum} severity among intents whose centre lies within cosine 0.8 of its own (plausible targets of a wrong-intent match). Hit rate rises from @@T.M('budget_0.02','hit')@@\,\% at $\rho=0.02$ to @@T.M('budget_0.4','hit')@@\,\% at 0.40, while harm rises from @@T.M('budget_0.02','harm')@@ to @@T.M('budget_0.4','harm')@@ per 1,000 queries. At $\rho=0.02$ RAASC + inv has @@T.M('budget_0.02','hit')@@\,\% hits at harm @@T.M('budget_0.02','harm')@@, against @@T.M('ttl_tuned_cap5_inv','hit')@@\,\% at harm @@T.M('ttl_tuned_cap5_inv','harm')@@ for the cap-5 TTL cache: about twice the hits at about 1.8 times the harm. The max-severity variant cuts harm at every budget (at $\rho=0.05$ from @@T.M('budget_0.05','harm')@@ to @@T.M('budget_maxsev_0.05','harm')@@) for about @@'%.0f' % (T.mean('budget_0.05','hit')-T.mean('budget_maxsev_0.05','hit'))@@ points of hit rate, and shifts the whole frontier towards safety; it is a conservative design option that needs the set of plausible target intents, which a deployment would have to estimate.

The table also relates the realised cost to the budget. The realised mean served-class cost per served answer is below $\rho$ on average at every budget, and below it in @@T.below('budget_0.05',0.05)@@ of 20 seeds at $\rho=0.05$ and in @@T.below('budget_0.4',0.4)@@ of 20 at 0.40. It is, however, \emph{not} below the mean estimated risk $\bar R$ of the served answers: at the default budget the ratio of realised cost to $\bar R$ is @@'%.2f' % (T.mean('budget_0.05','cost')/T.mean('budget_0.05','rbar'))@@, at $\rho=0.02$ it is @@'%.2f' % (T.mean('budget_0.02','cost')/T.mean('budget_0.02','rbar'))@@ and at 0.10 @@'%.2f' % (T.mean('budget_0.1','cost')/T.mean('budget_0.1','rbar'))@@, and it falls to @@'%.2f' % (T.mean('budget_0.4','cost')/T.mean('budget_0.4','rbar'))@@ only at the loosest budget. The estimates are therefore \emph{not} conservative on average at the small and default budgets, which violates the premise of assumption (A4) of Proposition~\ref{prop:cond}: the bound $\rho/(1-\rho/2)$ still holds on average in this workload because the realised cost is far from the budget, but it is not implied by the estimators. The cause is visible in \sref{sec:bias}: a bin-wise calibrator pools twin and non-twin intents, so intents with a near-duplicate partner are served with a wrong-intent probability that is too small for them. The two harm conventions diverge as the budget grows (Harm @@T.M('budget_0.4','harm')@@ against Harm$_s$ @@T.M('budget_0.4','harm_s')@@ at $\rho=0.40$), because wrong-intent hits that cross classes weigh by the severity of the true intent in one convention and of the served entry in the other; the budget acts on the served-class quantity, not on the true-intent harm, and both should be reported when a budget is chosen.

\begin{figure}[t]
\centering
@@T.fig_budget()@@
\caption{Hit rate against harm per 1,000 queries (true-intent severity) for five risk budgets (RAASC + inv, solid; with max-severity weights, dashed) and for baselines; mean of 20 test seeds, single frozen simulator. Upper left is worse for harm, right is better for hits.}\label{fig:budget}
\end{figure}

\begin{table*}[t]
\centering
\caption{Realised cost versus budget (RAASC + inv; mean $\pm$ 95\,\% CI over 20 test seeds). Harm: true-intent severity; Harm$_s$: served-entry class severity (both per 1,000 queries); Cost: mean $\sigma_{c(i_j)}U_j$ per served answer; $\bar R$: mean estimated risk of the served answers; right block: max-severity candidate weights}\label{tab:budget}
\footnotesize
\begin{tabular}{@{}cccccccrr@{}}
\toprule
 & & & & & & & \multicolumn{2}{c}{Max-severity}\\
\cmidrule(l){8-9}
$\rho$ & Hit \% & Harm & Harm$_s$ & Cost & $\bar R$ & Cost/$\bar R$ & Hit \% & Harm\\
\midrule
@@T.T_budget()@@
\bottomrule
\end{tabular}
\end{table*}

\subsection{Ablation and robustness}\label{sec:ablation}
\tref{tab:abl} varies one component at a time around RAASC + inv. \emph{Calibration:} replacing the calibrator by the fixed threshold 0.80 raises the hit rate to @@T.M('abl_nocal','hit')@@\,\% but harm to @@T.M('abl_nocal','harm')@@ (paired harm difference @@T.sgn(T.PT['raasc_inv|abl_nocal|harm']['delta'],1)@@, $p_{\mathrm{Holm}}=@@'%.2f' % T.PT['raasc_inv|abl_nocal|harm']['p_holm']@@$, not significant after Holm but significant in the Wilcoxon and permutation tests); with near-duplicate intents the calibrator therefore buys safety with hits, the opposite sign of what a workload without hard negatives suggests. \emph{Adaptive rate:} with update rates equal to the class priors the estimator has nothing to correct and shows no effect (hit @@T.sgn(T.PT['raasc_inv|abl_noadapt|hit']['delta'],2)@@, harm @@T.sgn(T.PT['raasc_inv|abl_noadapt|harm']['delta'],2)@@, both $p>0.6$). \emph{Bounds inside the cache:} the Clopper--Pearson bound costs @@'%.1f' % abs(T.PT['est_cp|raasc|hit']['delta'])@@ points of hit rate against \eqref{eq:wrong} (no invalidation; $p_{\mathrm{Holm}}=@@'%.3f' % T.PT['est_cp|raasc|hit']['p_holm']@@$) for a harm change of @@T.sgn(T.PT['est_cp|raasc|harm']['delta'],1)@@ that is not significant; the Hoeffding bound costs @@'%.1f' % abs(T.PT['est_hoeff|raasc|hit']['delta'])@@ points and lowers harm by @@'%.1f' % abs(T.PT['est_hoeff|raasc|harm']['delta'])@@ (both significant): a guaranteed calibrator is affordable only with the exact bound. \emph{Propensity weighting} (Horvitz--Thompson counts with weight $1/\varepsilon$ for audited hits and 1 for miss labels) gives hit @@T.M('est_eq6_ipw','hit')@@\,\% and harm @@T.M('est_eq6_ipw','harm')@@ i.e.\ it is also a safer, less available operating point; a higher audit rate (0.10) lowers harm at a cost of hits, and without audits ($\varepsilon=0$) harm rises to @@T.M('eps_0.00','harm')@@. \emph{Prior:} the optimistic, pessimistic and flat priors move the hit rate to @@T.M('prior_opt','hit')@@, @@T.M('prior_pess','hit')@@ and @@T.M('prior_flat','hit')@@\,\% and harm to @@T.M('prior_opt','harm')@@, @@T.M('prior_pess','harm')@@ and @@T.M('prior_flat','harm')@@ (no paired test run); the prior mainly trades availability for safety. \emph{Label noise:} flipping the identifier comparison of a label with probability 2\,\% or 5\,\% lowers the hit rate to @@T.M('labelnoise_0.02','hit')@@ and @@T.M('labelnoise_0.05','hit')@@\,\%. This is expected: a noise floor $\eta$ in the wrong-intent estimate removes every entry whose class budget share $\rho/\sigma_c$ is below $\eta$, so the correctness of the cloud's canonical intent identifier is a hard requirement. \emph{Push events:} reducing the push coverage (a proxy for lost or delayed events) lowers the hit rate only slightly (@@T.M('kappa_x0.0','hit')@@\,\% with no events against @@T.M('raasc_inv','hit')@@\,\%) and moves harm from @@T.M('raasc_inv','harm')@@ to @@T.M('kappa_x0.0','harm')@@, because invalidation only addresses staleness. \emph{$L_{\min}$:} 3\,s and 300\,s give the same results (the volatile limit of 3\,s is below both thresholds' relevant range), and 3,600\,s reduces the hit rate to @@T.M('lmin_3600','hit')@@\,\% because semi-static entries with short limits are no longer admitted. \emph{Cache size:} 50 and 200 entries change RAASC + inv to @@T.M('repl_raasc_default_cache50','hit')@@ and @@T.M('repl_raasc_default_cache200','hit')@@\,\% hits, and the default TTL + inv cache to @@T.M('repl_ttl_cache50','hit')@@ and @@T.M('repl_ttl_cache200','hit')@@\,\%.

\begin{table}[t]
\centering
\caption{Ablation and robustness (RAASC + inv unless stated; 0\,\% outage; mean $\pm$ 95\,\% CI over 20 test seeds; units as in \tref{tab:main})}\label{tab:abl}
\scriptsize
\setlength{\tabcolsep}{1.8pt}
\resizebox{\columnwidth}{!}{%
\begin{tabular}{@{}lccccc@{}}
\toprule
Variant & Hit \% & Unsafe \% & Wrong \% & Harm & Energy\\
\midrule
@@T.T_abl()@@
\bottomrule
\end{tabular}}
\end{table}

\subsection{Link outage and availability}\label{sec:outage}
\tref{tab:outage} fails each cloud request independently with probability 0.10. Cloud-only leaves @@T.M('out_cloud_only','unans',2)@@\,\% of the queries unanswered. The default TTL cache leaves @@T.M('out_ttl_default','unans',2)@@\,\% (its high hit rate also comes with the unsafe answers of \tref{tab:main}); the safety-tuned TTL cache (cap 15) leaves @@T.M('out_ttl_tuned_cap15_inv','unans',2)@@\,\%; RAASC + inv without degraded mode leaves @@T.M('out_raasc_nodeg','unans',2)@@\,\% and with the combined degraded rule at factor 4 @@T.M('out_raasc_deg4','unans',2)@@\,\%. RAASC with the degraded mode therefore \emph{does not} beat the default TTL cache on availability in this workload (@@T.M('out_raasc_deg4','unans',2)@@ against @@T.M('out_ttl_default','unans',2)@@\,\%), an advantage reported for an earlier workload does not replicate, and it beats the safety-tuned TTL cache by about @@'%.1f' % (T.mean('out_ttl_tuned_cap15_inv','unans')-T.mean('out_raasc_deg4','unans'))@@ points. A TTL cache given a matched degraded mode (answers up to $4\times$TTL old, flagged) gains almost nothing, because TTL entries older than their limit are rarely still cached and matching (the flagged share is @@T.M('out_ttl_default_deg4','flagged',2)@@\,\%).

\begin{table*}[t]
\centering
\caption{Availability at 10\,\% cloud-link outage (mean $\pm$ 95\,\% CI over 20 test seeds; Unans., Flagged: \% of all queries; Unsafe: \% of unflagged cache-served answers; Fl.\ stale/wrong/unsafe: \% of flagged answers, pooled over seeds)}\label{tab:outage}
\footnotesize
\begin{tabular}{@{}lccccccc@{}}
\toprule
Policy & Unans.\ \% & Flagged \% & Unsafe \% & Fl.\ stale & Fl.\ wrong & Fl.\ unsafe & Energy (J)\\
\midrule
@@T.T_outage()@@
\bottomrule
\end{tabular}
\end{table*}

\subsection{Audit of flagged degraded-mode answers}\label{sec:flagged}
The degraded mode of \sref{sec:degraded} serves a flagged answer when the link is down. Each flagged answer is checked against the truth in \tref{tab:outage}. With the combined rule ($R_{j^*}\le f\rho$) at factor 4, @@T.M('out_raasc_deg4','flagged',2)@@\,\% of the queries are answered flagged, and @@T.fl_pooled('out_raasc_deg4')[2]@@\,\% of these answers are unsafe (@@T.fl_pooled('out_raasc_deg4')[0]@@\,\% stale, @@T.fl_pooled('out_raasc_deg4')[1]@@\,\% wrong-intent), against @@T.M('out_raasc_deg4','unsafe',2)@@\,\% for the unflagged served answers; at factor 8 the flagged unsafe share is @@T.fl_pooled('out_raasc_deg8')[2]@@\,\%. Almost all flagged errors are wrong-intent answers, which the warning ``may be outdated'' does not describe. The strict rule, which additionally requires $\pwrong\sigma_c\le\rho$, serves @@T.M('out_raasc_strict4','flagged',2)@@\,\% flagged answers of which @@T.fl_pooled('out_raasc_strict4')[2]@@\,\% are unsafe, and its results are identical for factors 2 to 8 in the unflagged columns because the wrong-intent condition binds, not the staleness relaxation. It leaves @@T.M('out_raasc_strict4','unans',2)@@\,\% unanswered (against @@T.M('out_raasc_deg4','unans',2)@@\,\% for the combined rule and @@T.M('out_raasc_nodeg','unans',2)@@\,\% without degraded mode), so almost 80\,\% of the availability gain of the combined rule is lost; this is the price of not answering a possibly different question. Factor 4 is a heuristic simulation setting; no clinical threshold was derived. The flagged shares are pooled over seeds and their per-seed distribution is skewed (flagged counts are small).

\subsection{Paired comparisons and statistics}\label{sec:paired}
\tref{tab:paired} gives per-seed paired differences between the first and the second policy of each pair. Of the @@T.agreement()[4]@@ tests, @@T.agreement()[0]@@ are significant at 5\,\% in all three tests (paired $t$, Wilcoxon, sign-flip permutation), @@T.agreement()[1]@@ in none and @@T.agreement()[2]@@ in some; the non-parametric tests are generally the more sensitive here because the differences are skewed. After Holm's correction over the family the following hold: RAASC lowers the unsafe share and harm of the default TTL cache (unsafe $p_{\mathrm{Holm}}=@@'%.3f' % T.PT['raasc|ttl_default|unsafe']['p_holm']@@$, harm $p_{\mathrm{Holm}}=@@'%.3f' % T.PT['raasc|ttl_default|harm']['p_holm']@@$) in all 20 seeds, at the cost of hits and modelled energy; with invalidation the unsafe reduction stays significant ($p_{\mathrm{Holm}}=@@'%.3f' % T.PT['raasc_inv|ttl_default_inv|unsafe']['p_holm']@@$) but the harm reduction does not ($p_{\mathrm{Holm}}=@@'%.3f' % T.PT['raasc_inv|ttl_default_inv|harm']['p_holm']@@$). Against the tuned TTL cache (cap 15) no difference survives. With 20 seeds the $t$-test has 80\,\% power for $d_z=0.66$, so small effects are neither confirmed nor excluded.

\begin{table*}[t]
\centering
\caption{Paired differences over 20 test seeds (first minus second policy; Student-$t$ 95\,\% CI of the mean difference; $d_z$: effect size; $p$: paired $t$, Wilcoxon (W), sign-flip permutation (perm), and Holm-adjusted $t$; Wins: seeds in which the first policy is better; Holm family: all 40 tests listed)}\label{tab:paired}
\scriptsize
\setlength{\tabcolsep}{2.5pt}
\begin{tabular}{@{}lccccccc@{}}
\toprule
Metric & $\Delta$ [95\,\% CI] & $d_z$ & $p_t$ & $p_W$ & $p_{\mathrm{perm}}$ & $p_{\mathrm{Holm}}$ & Wins\\
\midrule
@@T.T_paired()@@
\bottomrule
\end{tabular}
\end{table*}

\subsection{Baselines and tuning}\label{sec:baselines}
\tref{tab:tuned} and \tref{tab:main} contain the tuned baselines of \sref{sec:policies}; the main findings are in \sref{sec:main}. Two points deserve emphasis. First, the fixed-$\tau$ semantic cache cannot be tuned to a safe operating point with a threshold alone: even at $\tau=0.95$ it serves @@T.M('tau_tuned_cap5_inv','unsafe',1)@@\,\% unsafe answers, because without a TTL the stale answers accumulate and because near-duplicate intents sit above any usable threshold. Second, the TTL values and the threshold of the conventional baselines matter more than the choice of algorithm: moving from the assumed defaults to tuned values changes the TTL cache from @@T.M('ttl_default_inv','hit')@@\,\% hits at harm @@T.M('ttl_default_inv','harm')@@ to @@T.M('ttl_tuned_cap15_inv','hit')@@\,\% at @@T.M('ttl_tuned_cap15_inv','harm')@@. Comparisons of RAASC with the untuned defaults of the earlier versions therefore overstate its advantage; the comparison with validation-tuned baselines in \tref{tab:paired} is the relevant one. Tuning used only validation seeds, and the selection rule (a harm cap) was fixed before the runs, but a different rule or cap would select different baselines, and a TTL tuned per intent was not tried.

\subsection{Update-rate estimator under shifted rates}\label{sec:shift}
\tref{tab:shift} compares the adaptive estimator with the class prior on the three update-process variants of \sref{sec:setup}. Per-seed paired differences (adaptive minus prior): with mis-specified priors harm changes by @@T.sgn(T.pair_desc('shift_wrongprior_adaptive','shift_wrongprior_prior','harm')[0],1)@@ (Wilcoxon $p=@@'%.3f' % T.pair_desc('shift_wrongprior_adaptive','shift_wrongprior_prior','harm')[2]@@$, $t$ $p=@@'%.2f' % T.pair_desc('shift_wrongprior_adaptive','shift_wrongprior_prior','harm')[1]@@$), after a sudden change by @@T.sgn(T.pair_desc('shift_sudden_adaptive','shift_sudden_prior','harm')[0],1)@@ ($p_t=@@'%.3f' % T.pair_desc('shift_sudden_adaptive','shift_sudden_prior','harm')[1]@@$) and under drift by @@T.sgn(T.pair_desc('shift_drift_adaptive','shift_drift_prior','harm')[0],1)@@ ($p_t=@@'%.3f' % T.pair_desc('shift_drift_adaptive','shift_drift_prior','harm')[1]@@$), at a cost of about 2.7 points of hit rate under sudden change and drift and about 0.7 points with mis-specified priors. The estimator is therefore helpful when the update process changes, and its benefit is smaller than its cost when only the prior is wrong in the way tested. These tests are descriptive and outside the Holm family. In all variants RAASC stays far below the default TTL + inv cache in harm, and the tuned TTL cache (cap 5) keeps lower harm at a much lower hit rate.

\begin{table}[t]
\centering
\caption{Update-rate estimator under shifted update rates (RAASC + inv, and TTL baselines; 0\,\% outage; mean $\pm$ 95\,\% CI over 20 test seeds; units as in \tref{tab:main})}\label{tab:shift}
\scriptsize
\setlength{\tabcolsep}{1.6pt}
\begin{tabular}{@{}llcccc@{}}
\toprule
Workload & Policy & Hit \% & Unsafe \% & Harm/1k & Energy\\
\midrule
@@T.T_shift()@@
\bottomrule
\end{tabular}
\end{table}

\subsection{Analytical sensitivity of the reuse limit}\label{sec:sens}
The experiments vary only the budget, but Eq.~\eqref{eq:amax} gives the reuse limit in closed form, so its sensitivity can be stated without further simulation. \tref{tab:limits} lists the limit at $\pwrong=0$ for the five budgets of \tref{tab:budget} and the class parameters of \sref{sec:setup}. For small budgets the limit grows almost linearly with $\rho/\sigma_c$, and invalidation with $\kappa=0.5$ doubles it. The volatile limit stays below $\Lmin=30$\,s at all five budgets (25\,s at $\rho=0.40$), so volatile answers are never admitted at any budget that was run. The limits also show where RAASC becomes more permissive than the default TTL baseline (7\,d and 6\,h): with invalidation, the static limit exceeds 7\,d for $\rho$ above about 0.11 and the semi-static limit exceeds 6\,h for $\rho$ above about 0.235. \tref{tab:wrongeff} shows how the calibrated wrong-intent probability uses up the budget. Because the two risks add in Eq.~\eqref{eq:risk}, a bin with a small $\pwrong$ shortens the admissible age by its share of the budget $\rho/\sigma_c$: at $\rho=0.05$, $\pwrong=0.01$ already removes 20\,\% of the static limit and 40\,\% of the semi-static limit, and a semi-static entry is not served at all once $\pwrong\ge\rho/\sigma_c=0.025$. This is why the near-duplicate intents of \sref{sec:setup} matter: they raise $\pwrong$ in the high-similarity bins where entries are served.

\begin{table}[t]
\centering
\caption{Reuse limit (Eq.~\eqref{eq:amax}) at $p_{\mathrm{wrong}}=0$ for the budgets of \tref{tab:budget}; push coverage 0.5 for static and semi-static intents (no invalidation in parentheses)}\label{tab:limits}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}cccc@{}}
\toprule
$\rho$ & Static & Semi-static & Volatile\\
\midrule
0.02 & 29.1\,h (14.5\,h) & 29\,min (14\,min) & 1.2\,s\\
0.05 & 3.1\,d (1.5\,d) & 73\,min (36\,min) & 3.0\,s\\
0.10 & 6.3\,d (3.2\,d) & 2.5\,h (74\,min) & 6.1\,s\\
0.20 & 13.4\,d (6.7\,d) & 5.1\,h (2.5\,h) & 12.2\,s\\
0.40 & 30.6\,d (15.3\,d) & 10.7\,h (5.4\,h) & 25.0\,s\\
\bottomrule
\end{tabular}
\end{table}

\begin{table}[t]
\centering
\caption{Effect of the wrong-intent estimate on the reuse limit (budget 0.05, push coverage 0.5; share of the limit at $p_{\mathrm{wrong}}=0$ in parentheses)}\label{tab:wrongeff}
\scriptsize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}ccc@{}}
\toprule
$p_{\mathrm{wrong}}$ & Static & Semi-static\\
\midrule
0 & 3.1\,d (100\,\%) & 73\,min (100\,\%)\\
0.005 & 2.8\,d (90\,\%) & 58\,min (80\,\%)\\
0.01 & 2.5\,d (80\,\%) & 44\,min (60\,\%)\\
0.02 & 1.9\,d (61\,\%) & 15\,min (20\,\%)\\
0.03 & 30.0\,h (41\,\%) & not served\\
0.04 & 15.1\,h (20\,\%) & not served\\
\bottomrule
\end{tabular}
\end{table}

\subsection{Coverage of the wrong-intent estimators in isolation}\label{sec:coverage}
To test the estimators of the wrong-intent probability apart from the cache, we draw $w\sim\mathrm{Binomial}(n,q)$ labels for one similarity bin with true wrong-intent probability $q$ and compare upper estimates of $q$: \eqref{eq:wrong} with a well-specified prior ($p_0=q$) and with an optimistic prior ($p_0=q/4$), the Hoeffding bound with $\delta=0.05$, and the exact one-sided binomial bound of Clopper and Pearson~\cite{clopper1934} with $\delta=0.05$. \tref{tab:cov} gives the coverage $\Pr[\text{estimate}\ge q]$ and the mean estimate over 200,000 draws per setting. Estimator \eqref{eq:wrong} never reaches the 95\,\% level: its coverage lies between @@T.covrange('eq6')[0]@@\,\% and @@T.covrange('eq6')[1]@@\,\% with the well-specified prior and between @@T.covrange('eq6_opt')[0]@@\,\% and @@T.covrange('eq6_opt')[1]@@\,\% with the optimistic prior, and the shortfall is largest for small $q$ and few labels, the situation of the high-similarity bins that decide which hits are served. The Hoeffding bound covers at least 99.6\,\% in all settings but its mean value is up to several times that of \eqref{eq:wrong}; the exact bound lies in between, with coverage of 95--100\,\%. A margin is paid for out of the budget share $\rho/\sigma_c$ (\tref{tab:wrongeff}): for the Hoeffding margin alone to fit inside the share, $n$ must exceed $\ln(1/\delta)/\big(2(\rho/\sigma_c)^2\big)$, that is 600, 2,397 and 14,979 labels for static, semi-static and volatile intents at $\rho=0.05$, well above the 185 labels that suffice to estimate a bin within 0.1. \sref{sec:ablation} shows the consequence inside the cache: the exact bound is affordable, the Hoeffding bound is not. The draws here are independent by construction, which real miss and audit labels are not; \sref{sec:bias} therefore repeats the comparison on the labels that the cache itself produces.

\begin{table*}[t]
\centering
\caption{Coverage (\%) / mean estimate of four upper estimates of the wrong-intent probability $q$ of one bin ($n$ labels, 200,000 draws; 95\,\% confidence level for the two bounds; \texttt{coverage\_study.py}, seed 0)}\label{tab:cov}
\footnotesize
\begin{tabular}{@{}rrcccc@{}}
\toprule
$q$ & $n$ & Eq.~\eqref{eq:wrong}, $p_0=q$ & Eq.~\eqref{eq:wrong}, $p_0=q/4$ & Hoeffding & Clopper--Pearson\\
\midrule
@@T.T_cov()@@
\bottomrule
\end{tabular}
\end{table*}

\subsection{Calibration prior}\label{sec:prior}
The prior of the wrong-intent calibrator is Eq.~\eqref{eq:prior}; \tref{tab:prior} lists its ten values. It is a weak monotone assumption and is not fitted to data. \tref{tab:abl} gives the effect of three alternatives (descriptive, no paired test): the hit rate changes by @@T.sgn(T.mean('prior_opt','hit')-T.mean('raasc_inv','hit'),1)@@, @@T.sgn(T.mean('prior_pess','hit')-T.mean('raasc_inv','hit'),1)@@ and @@T.sgn(T.mean('prior_flat','hit')-T.mean('raasc_inv','hit'),1)@@ points and harm from @@T.M('raasc_inv','harm')@@ to @@T.M('prior_opt','harm')@@, @@T.M('prior_pess','harm')@@ and @@T.M('prior_flat','harm')@@ for the optimistic, pessimistic and flat prior. A higher prior holds a similarity bin back until enough labels have accumulated to overcome it, so the prior mainly trades availability against safety. With $n_0=8$ pseudo-observations the prior fades after a few tens of labels per bin, and the bins above 0.80 receive hundreds of labels per seed and week (\tref{tab:bins}); a deployment with fewer labels would be more sensitive to the choice.

\begin{table}[t]
\centering
\caption{Prior wrong-intent probability $p_0(b)$ of the ten similarity bins (Eq.~\eqref{eq:prior}; $s_b$ is the bin mid-point)}\label{tab:prior}
\scriptsize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}clcc@{}}
\toprule
Bin $b$ & Range & $s_b$ & $p_0(b)$\\
\midrule
1 & 0.50--0.55 & 0.525 & 0.990\\
2 & 0.55--0.60 & 0.575 & 0.988\\
3 & 0.60--0.65 & 0.625 & 0.958\\
4 & 0.65--0.70 & 0.675 & 0.867\\
5 & 0.70--0.75 & 0.725 & 0.651\\
6 & 0.75--0.80 & 0.775 & 0.349\\
7 & 0.80--0.85 & 0.825 & 0.133\\
8 & 0.85--0.90 & 0.875 & 0.042\\
9 & 0.90--0.95 & 0.925 & 0.012\\
10 & 0.95--1.00 & 0.975 & 0.005\\
\bottomrule
\end{tabular}
\end{table}

\subsection{Selection bias of the calibration labels}\label{sec:bias}
In the cache, labels come from two selected sources: the best-scoring candidate of every query that is not served (a miss), and a random 2\,\% of the served hits (an audit). The simulator also records an oracle label for the best-scoring candidate of every query, served or not, which no deployed gateway could observe. \tref{tab:bins} compares, for the six upper bins and RAASC + inv at the default budget, the wrong-intent rate in the miss labels, in the audit labels and among all decisions, and the coverage across the 20 seeds of the end-of-week estimates (Eq.~\eqref{eq:wrong}, Hoeffding, Clopper--Pearson) with respect to the all-decision rate of the same seed; \tref{tab:binsipw} repeats the estimates for the propensity-weighted calibrator.

Below 0.80 only miss labels exist and almost every decision is a miss. Above 0.80 only @@T.share_text()[0]@@\,\% of the decisions are labelled and @@T.share_text()[1]@@\,\% of these labels come from misses. The two sources disagree where it matters. In the 0.85--0.90 bin the miss labels show a wrong-intent rate of @@'%.3f' % T.L['bins_plain'][7]['rate_miss']@@, the audit labels @@'%.3f' % T.L['bins_plain'][7]['rate_aud']@@ and all decisions (oracle) @@'%.3f' % T.L['bins_plain'][7]['rate_orc']@@: miss labels overstate and audit labels understate the rate, because misses are selected for high estimated risk and served hits for low estimated risk. Estimator \eqref{eq:wrong} covers the oracle rate in only @@'%.0f' % T.L['bins_plain'][7]['cov_eq6']@@\,\% of the seeds in the 0.85--0.90 bin and @@'%.0f' % T.L['bins_plain'][8]['cov_eq6']@@\,\% in the 0.90--0.95 bin, the bins that serve most hits; the Hoeffding bound covers @@'%.0f' % T.L['bins_plain'][7]['cov_H']@@ and @@'%.0f' % T.L['bins_plain'][8]['cov_H']@@\,\% and the exact bound @@'%.0f' % T.L['bins_plain'][7]['cov_CP']@@ and @@'%.0f' % T.L['bins_plain'][8]['cov_CP']@@\,\%, at the price of mean estimates two to four times larger. Propensity weighting raises the coverage of \eqref{eq:wrong} in these bins to @@'%.0f' % T.L['bins_ipw'][7]['cov_eq6']@@ and @@'%.0f' % T.L['bins_ipw'][8]['cov_eq6']@@\,\%. The selection of the labels therefore does make \eqref{eq:wrong} anti-conservative in the served bins, which is consistent with the finding of \sref{sec:budget} that realised cost exceeds the estimated risk. The per-bin estimate cannot separate twin from non-twin intents, a limit of the bin-wise design that a per-intent or per-pair calibrator would address. A candidate-level randomised audit with recorded probabilities beyond the 2\,\% of served hits, and tests against temporal dependence of the labels, were not run.

\begin{table*}[t]
\centering
\caption{Label sources and estimator coverage in the cache (RAASC + inv, $\rho=0.05$; 20 test seeds). Counts are per-seed means; wrong-intent rates are pooled over seeds; the oracle rate is the wrong-intent share of all best-candidate decisions in the bin; coverage is the share of seeds in which the end-of-week estimate is at least that seed's oracle rate; H: Hoeffding, CP: Clopper--Pearson}\label{tab:bins}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}lrrrrrrcc@{}}
\toprule
 & \multicolumn{3}{c}{Per seed (count)} & \multicolumn{3}{c}{Wrong-intent rate (pooled)} & Coverage \% & Mean estimate\\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}
Bin & Miss lab. & Audit lab. & Decisions & Miss & Audit & Oracle & (6) / H / CP & (6) / H / CP\\
\midrule
@@T.T_bins('bins_plain')@@
\bottomrule
\end{tabular}
\end{table*}

\begin{table*}[t]
\centering
\caption{As \tref{tab:bins} for the propensity-weighted calibrator (Horvitz--Thompson counts; audited hits weighted $1/\varepsilon$)}\label{tab:binsipw}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}lrrrrrrcc@{}}
\toprule
 & \multicolumn{3}{c}{Per seed (count)} & \multicolumn{3}{c}{Wrong-intent rate (pooled)} & Coverage \% & Mean estimate\\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}
Bin & Miss lab. & Audit lab. & Decisions & Miss & Audit & Oracle & (6) / H / CP & (6) / H / CP\\
\midrule
@@T.T_bins('bins_ipw')@@
\bottomrule
\end{tabular}
\end{table*}

\subsection{Evaluation of the deny-list}\label{sec:denyeval}
The main workload contains no deny category, so \tref{tab:deny} and \tref{tab:deny2} evaluate the deny-list of \sref{sec:deny} on two workloads (\sref{sec:setup}). Each row gives the router's precision, recall and false-positive rate over all queries, pooled over seeds. Without a deny-list, RAASC + inv serves @@T.M('deny_uniform_raasc_nolist','deny_served',1)@@\,\% of the deny-category queries from the cache in the uniform workload (deny-category harm @@T.M('deny_uniform_raasc_nolist','deny_harm',2)@@ per 1,000 queries); a router of recall 1 removes this exposure entirely at a cost of @@'%.1f' % (T.mean('deny_uniform_raasc_nolist','hit')-T.mean('deny_uniform_raasc_r1.0_fp0.0','hit'))@@ points of hit rate and @@'%.2f' % (T.mean('deny_uniform_raasc_r1.0_fp0.0','energy')-T.mean('deny_uniform_raasc_nolist','energy'))@@\,J. Recall 0.9 and 0.7 let @@T.M('deny_uniform_raasc_r0.9_fp0.0','deny_served',1)@@ and @@T.M('deny_uniform_raasc_r0.7_fp0.0','deny_served',1)@@\,\% of the deny queries through (deny-category harm @@T.M('deny_uniform_raasc_r0.9_fp0.0','deny_harm',2)@@ and @@T.M('deny_uniform_raasc_r0.7_fp0.0','deny_harm',2)@@): the leak is small because each detected query purges the cached entries of its intent, so that a missed query can be served only from an entry admitted by an earlier undetected query since the last purge. \emph{Correlated misses} (whole intents hidden from the router) leak more at the same average recall (deny harm @@T.M('deny_uniform_raasc_r0.7_fp0.0_corr','deny_harm',2)@@ against @@T.M('deny_uniform_raasc_r0.7_fp0.0','deny_harm',2)@@ at nominal recall 0.7; @@T.M('deny_uniform_raasc_r0.9_fp0.0_corr','deny_harm',2)@@ against @@T.M('deny_uniform_raasc_r0.9_fp0.0','deny_harm',2)@@ at 0.9), because the purge protection disappears when an intent is never detected. A false-positive rate of 5\,\% sends ordinary queries to the cloud: the bypass share rises to @@T.M('deny_uniform_raasc_r1.0_fp0.05','bypass',1)@@\,\% and the hit rate falls by a further @@'%.1f' % (T.mean('deny_uniform_raasc_r1.0_fp0.0','hit')-T.mean('deny_uniform_raasc_r1.0_fp0.05','hit'))@@ points. Because deny queries are rare, precision is low at this FPR (@@'%.0f' % (100*T.a('deny_uniform_raasc_r0.9_fp0.05','tp').sum()/(T.a('deny_uniform_raasc_r0.9_fp0.05','tp').sum()+T.a('deny_uniform_raasc_r0.9_fp0.05','fp').sum()))@@\,\% in the uniform and @@'%.0f' % (100*T.a('deny_rare_raasc_r0.9_fp0.05','tp').sum()/(T.a('deny_rare_raasc_r0.9_fp0.05','tp').sum()+T.a('deny_rare_raasc_r0.9_fp0.05','fp').sum()))@@\,\% in the rare workload), so a deployed router needs a far lower FPR than 5\,\%. In the rare workload (@@'%.1f' % T.mean('deny_rare_raasc_nolist','deny_share')@@\,\% of the queries) the deny harm is small in absolute terms (@@T.M('deny_rare_raasc_nolist','deny_harm',2)@@ without a list) but @@T.M('deny_rare_raasc_nolist','deny_served',1)@@\,\% of such queries are still answered from the cache; the deny-list's cost in hit rate is negligible without false positives. The overall unsafe share and harm are nearly unchanged by the deny-list, because the deny-category intents are no riskier than the others in the generator: the deny-list is justified by clinical severity, which the update statistics of the simulation cannot express. The experiment measures the availability cost and the effect of imperfect and correlated recall, not the clinical benefit.

\begin{table*}[t]
\centering
\caption{Deny-list, uniform deny category (mean over 20 test seeds; precision / recall / FPR of the router in \%, pooled; Hit and Bypass: \% of all queries; Deny served: \% of deny-category queries answered from the cache; Deny harm: unsafe deny-category answers weighted 10, per 1,000 queries; Harm: all queries, true-intent severity)}\label{tab:deny}
\footnotesize
\begin{tabular}{@{}lccccccc@{}}
\toprule
Policy / router & P / R / FPR & Hit & Bypass & Deny served & Deny harm & Harm & Energy\\
\midrule
@@T.T_deny('uniform')@@
\bottomrule
\end{tabular}
\end{table*}

\begin{table*}[t]
\centering
\caption{Deny-list, rare deny category (10 less popular intents; columns as \tref{tab:deny})}\label{tab:deny2}
\footnotesize
\begin{tabular}{@{}lccccccc@{}}
\toprule
Policy / router & P / R / FPR & Hit & Bypass & Deny served & Deny harm & Harm & Energy\\
\midrule
@@T.T_deny('rare')@@
\bottomrule
\end{tabular}
\end{table*}

\subsection{Probe with a pretrained encoder on real medical questions}\label{sec:probe}
All simulator experiments use synthetic vectors. As a first, limited step towards the protocol of \sref{sec:protocol} we embedded real consumer medical questions with a pretrained encoder and measured how close the questions of different threads are to each other. The questions are the titles of 4,000 distinct threads drawn at random (seed 0) from the public WebMD, eHealth Forum and iCliniq question collections of~\cite{regin2017} (about 24,000 questions after de-duplication); the encoder is WordLlama (\texttt{l2\_supercat}, 256 dimensions)~\cite{wordllama2025}, the only pretrained sentence encoder whose weights were reachable at that time. It is a static embedder derived from a language-model embedding table, not Sentence-BERT~\cite{reimers2019}, and it ignores word order: ``ibuprofen with warfarin'' and ``warfarin with ibuprofen'' have cosine 1.0. For each question we took the cosine of its nearest neighbour among the other 3,999 questions. This probe was produced by a separate script in an earlier stage and was not re-run for this paper (\sref{sec:repro}).

\tref{tab:probe} shows that a neighbour above the similarity floor of 0.5 is the rule, and that 5.3\,\% of the questions have a neighbour at 0.8 or more, the threshold of the fixed-threshold baseline. Inspection of the closest pairs shows both cases: near-duplicates with the same intent (cosine 0.999, ``what are the symptoms of schizophrenia?'' against the same question without an article; 0.90 for two questions on the treatment of sinusitis) and pairs with a high cosine and a different clinical situation (cosine 0.74 for two questions on unprotected intercourse and contraception, one asking about emergency contraception and the other about pregnancy). The probe has three limits: it has no same-intent labels and cannot give $\pwrong$ per bin; it uses a static encoder whose similarity distribution differs from that of Sentence-BERT; and it does not enter the cache simulation. It is an exploratory, unlabelled similarity probe and \emph{not} a calibration or validation result. It does show that real medical questions contain many close neighbours, which motivated the hard-negative twins of the present workload; their number and similarity are, however, assumptions and not fitted to this probe.

\begin{table}[t]
\centering
\caption{Nearest-neighbour cosine between real medical questions (4,000 questions, WordLlama encoder; exploratory, unlabelled; earlier run)}\label{tab:probe}
\scriptsize
\begin{tabular}{@{}lc@{}}
\toprule
Statistic & Value\\
\midrule
Median / 90th / 99th percentile & 0.573 / 0.737 / 0.900\\
Questions with a neighbour at cos $\ge0.6$ & 40.1\,\%\\
Questions with a neighbour at cos $\ge0.7$ & 15.0\,\%\\
Questions with a neighbour at cos $\ge0.8$ & 5.3\,\%\\
Questions with a neighbour at cos $\ge0.9$ & 1.0\,\%\\
\bottomrule
\end{tabular}
\end{table}

\subsection{Modelled energy sensitivity}\label{sec:energysens}
\tref{tab:energy} gives the modelled saving against cloud-only from Eq.~\eqref{eq:energy} with the measured RAASC + inv hit rate of this simulation (@@T.M('raasc_inv','hit')@@\,\%), $\varepsilon=0.02$, for lookup times $t_c$ and cloud times $t_i$, together with the break-even hit rate. The saving is robust to a cloud time between 4.77 and 8\,s for lookup times up to 0.5\,s, but vanishes or turns negative for lookup times of 1\,s or more at a cloud time of 2\,s: the energy benefit is a property of the measured prototype, not of the policy. These are model calculations; the power, lookup time and cloud time were not measured on the target gateway.

\begin{table}[t]
\centering
\caption{Modelled energy saving against cloud-only (\%) for $\varepsilon=0.02$ at the RAASC + inv hit rate of \tref{tab:main}, and break-even hit rate (\%)}\label{tab:energy}
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}cccccc@{}}
\toprule
$t_c$ (s) & $t_i{=}2$\,s & $t_i{=}4.77$\,s & $t_i{=}8$\,s & \multicolumn{2}{c}{Break-even hit \% ($t_i$=2/4.77/8)}\\
\midrule
@@T.T_energy().replace('\\\\', '\\\\')@@
\bottomrule
\end{tabular}
\end{table}

%==================================================================
\section{Discussion and Limitations}\label{sec:discussion}
\subsection{Interpretation of the results}
The fixed TTL and the fixed threshold are two separate, uncalibrated rules. RAASC replaces both with one quantity, the estimated severity-weighted risk, whose inputs are learned from signals that the gateway already receives (version tags and cloud answers on misses). Proposition~\ref{prop:limit} shows that the rule behaves as an adaptive TTL per intent. On the synthetic workload with near-duplicate intents RAASC removes most of the unsafe answers of the default class-aware TTL cache, but it also removes about a third of its hits, and against TTL and threshold baselines tuned on validation seeds its advantage shrinks to a modest, non-significant gain in the hit--harm trade-off. The operational advantage that remains is that the operator controls the system through one parameter, the risk budget, which a clinical safety officer can audit more easily than a table of TTLs and a similarity threshold, and that RAASC keeps working when update rates change (\tref{tab:shift}).

The extended analyses reverse or qualify several earlier impressions. (i) With near-duplicate intents, wrong-intent hits, not stale hits, dominate the unsafe answers, and invalidation does not reduce them. (ii) The bin-wise calibrator pools twin and non-twin intents and is anti-conservative in the bins that serve most hits; realised served-class cost exceeds the mean estimated risk at the small and default budgets, so assumption (A4) fails in practice, and Hoeffding or propensity-weighted estimators repair the coverage only by giving up hit rate. (iii) A 2--5\,\% error rate in the cloud's canonical intent identifiers sharply reduces the hit rate, so identifier quality is a hard prerequisite. (iv) The combined degraded-mode rule answers wrong questions with a warning that does not describe the error; the strict rule fixes this at the cost of most of the availability gain, and RAASC's availability does not beat the default TTL cache here, only the safety-tuned one. (v) A deny-list needs a low false-positive rate and tolerates imperfect recall less well when misses are correlated. (vi) The budget acts on the served-class estimated risk; the true-intent harm can be several times larger at loose budgets, and a max-severity weighting is a conservative alternative.

\subsection{Deployment considerations}\label{sec:deploy}
The severity weights and the risk budget must be set by clinical governance and reviewed when intents are added or guidelines change; the values 1, 2 and 5 are placeholders. Patient-specific, time-sensitive information such as results, medication changes and appointment slots must never be served from the cache. A high severity makes this unlikely, but RAASC does not depend on it: these categories are excluded by the explicit deny-list of \sref{sec:deny}, whose recall, precision and correlated failures are those of the router in front of it (\sref{sec:denyeval}). The deny-list and router need a governed lifecycle: named clinical owners, review of every change, versioned releases with rollback and an emergency update path. Event-driven invalidation lowers the stale share (\sref{sec:main}), so a clinic should publish protocol and label changes to the gateway whenever it can; delayed or lost events behave like a lower push coverage $\kappa_c$ (\sref{sec:ablation}), and periodic revalidation by version tag is a possible remedy that was not evaluated. Shadow auditing sends de-identified text to the cloud for a small fraction of hits (2\,\% here); its rate trades calibration quality against cloud calls (\sref{sec:ablation}) and can be raised after a change of model or vocabulary~\cite{gama2014}. Further issues remain open: conflicting information from different clinical sources, the periodic review of severity weights, and the risk that an incorrect cloud answer~\cite{singhal2023,ji2023} enters the cache, for which only answers from a curated, versioned knowledge base should be admitted. The voice-biomarker path follows the guided-recording protocol recommended in~\cite{carron2021}, and RAASC does not touch audio. A cache that serves health information may fall under medical-device or health-data regulation depending on the jurisdiction; this paper makes no such assessment.

\subsection{Security, privacy and threat model}\label{sec:security}
The cache sits between users and a clinical knowledge source, so it needs an explicit, if short, threat model. In scope for the design: cached content is treated as untrusted data when read back (the cache stores only answers, version counters and intent identifiers from a curated knowledge base); the deny-list keeps patient-specific content out of the cache; and the privacy filter de-identifies text before embedding and before any shadow audit. Out of scope and not evaluated: tenant isolation and cross-patient leakage (the simulation is single-tenant, and a deployment would need tenant-scoped cache keys and access control, since a deny-list is not an authorisation mechanism); malicious or adversarially crafted queries, including prompt injection through query text and embeddings engineered to hit a chosen entry; cache pollution and poisoning by crafted traffic or by a compromised update channel; and the authenticity of pushed update events. These attacks could in particular distort the calibration labels or the rate estimates, and a hardened design would authenticate events and rate-limit label updates. Upstream errors are also out of scope: the model assumes that the cloud returns a correct and current answer with a valid version tag, and does not handle upstream hallucination, stale sources or conflicting knowledge bases.

\subsection{Threats to validity}
First, the evaluation uses synthetic vectors, not the output of a sentence encoder~\cite{reimers2019}; the hard-negative twins (32 intents, three similarity levels) are an assumption, and the paraphrase similarity was set to match~\cite{montoya2025}, so they are not an independent check. Real encoders may produce more or fewer, and differently distributed, high-similarity wrong-intent pairs. Second, the traffic, update process, severity weights and push coverage are assumed. Third, we assume that the cloud provides correct and current answers with a version tag and an accurate canonical intent identifier; \sref{sec:ablation} shows the sensitivity to identifier errors only for a symmetric flip of labels. Fourth, absolute rates will differ on real traffic and the large seed-to-seed variation (\sref{sec:results}) means that conclusions are about the simulated workload family. Fifth, latency, power and the constant-power model $E=Pt$ come from one prototype~\cite{montoya2025} and ignore radio, compute and idle states, so energy and latency are modelled and coupled. Sixth, only a seven-day, 100-entry, single-gateway scenario was simulated (cache sizes 50 and 200 as a check). Seventh, the intervals reflect variance between seeds, not model error; tests are not corrected beyond the stated Holm family and equivalence was not tested. Eighth, the baselines were tuned on a harm-cap rule and a grid chosen by us; different rules would select different baselines, and a learned-threshold cache~\cite{schroeder2026} was not compared. Ninth, the correlation between stale and wrong-intent events was not measured; Proposition~\ref{prop:cond}(b) bounds its effect but the generator draws updates independently of questions. Tenth, the shadow audit has a single rate (0.02, 0.10 tried); a candidate-level randomised audit with recorded probabilities was not run beyond the propensity-weighted variant. Eleventh, the deny-category workloads use assumed severities (10), uniform or rare selection and independent or whole-intent misses, and only one false-positive rate beyond zero. Finally, the budget is enforced with estimated probabilities, so there is no distribution-free guarantee, unlike conformal methods~\cite{angelopoulos2021}, and estimator \eqref{eq:wrong} is not conservative (\sref{sec:coverage}, \sref{sec:bias}).

\subsection{Protocol for validation on real embeddings and public data}\label{sec:protocol}
The synthetic embeddings are the main limit of the present evaluation, and validating the design does not require clinical traffic. The protocol has five steps. (i) Replace the synthetic vectors by the output of a named sentence encoder~\cite{reimers2019} (model, version, pooling, normalisation and dimension reported) and build the workload from public question collections: MedQuAD, a collection of 47,457 medical question--answer pairs with annotations~\cite{benabacha2019}, supplies medical questions and topics, and PAWS, a set of human-labelled paraphrase and non-paraphrase pairs with high lexical overlap~\cite{zhang2019}, supplies hard same-intent and different-intent pairs, so that the calibrator of \eqref{eq:wrong} is fed with real labels; splits are made at the pair level with a fixed seed so that no pair or near-duplicate leaks between calibration and test. (ii) Report the calibration error of $\pwrong$ per similarity bin on held-out pairs (calibration plot, Brier score, log loss, per-bin counts and intervals) before any cache simulation, because Proposition~\ref{prop:cond} depends on it. (iii) Replace the assumed Poisson rates by rates fitted to public revision histories, for example of drug labels or guidelines. (iv) Add a learned-threshold semantic cache~\cite{schroeder2026} as a baseline on the public benchmarks released with it. (v) Measure energy on the target gateway hardware. Only after these steps should the severity weights and the budget go to a supervised clinical pilot.

\subsection{Status of this revision and open items}\label{sec:status}
Relative to the earlier versions, this revision runs every experiment on one frozen simulator, adds hard-negative intents, validation-tuned baselines, a matched degraded-mode baseline, Hoeffding, exact-binomial and propensity-weighted calibrators inside the cache, label noise, a strict degraded mode, a max-severity weighting, a deny-list with false positives, correlated misses and rare intents, non-parametric and permutation tests with a defined Holm family, an analytic energy sensitivity, and a threat model. The following remain \emph{open} and are not claimed: (1) steps (i) and (ii) of \sref{sec:protocol}: Sentence-BERT weights, PAWS and MedQuAD were not reachable in our environment, so no calibration or cache result with real labelled pairs is reported, and the hard negatives are synthetic; (2) the real-question probe of \sref{sec:probe} was not re-run with the frozen code; (3) a per-intent or per-pair calibrator that separates twin from non-twin intents, and a candidate-level randomised audit across all similarity ranges; (4) comparison with a learned-threshold cache~\cite{schroeder2026}; (5) fitting update rates to public revision logs; (6) hardware power measurement; (7) clinical determination of severity weights, budget and deny-list; (8) an implemented tenant-isolation and adversarial-robustness evaluation; and (9) distribution-free guarantees by conformal calibration. Until then the results are a simulation-and-methodology study of a semantic-cache layer, and no clinical safety claim is made.

%==================================================================
\section{Conclusion and Future Work}\label{sec:conclusion}
We presented RAASC, a risk-aware adaptive semantic-cache layer for edge healthcare voice-assistant pipelines, with an analysis of its estimators and reuse limit, a frozen reference simulator and a seeded evaluation. RAASC estimates the staleness and wrong-intent probabilities of each entry online and serves only entries whose estimated severity-weighted risk fits an operator-defined budget. On a synthetic workload with near-duplicate intents it removes most of the unsafe answers of the default class-aware TTL cache (unsafe @@T.M('ttl_default','unsafe',1)@@\,\% to @@T.M('raasc','unsafe',1)@@\,\% without invalidation) at lower hit rate, and against validation-tuned TTL baselines it offers a modest, non-significant gain in the hit--harm trade-off together with a single operator-facing control. The same experiments show where the design is weak: wrong-intent hits dominate, the bin-wise calibrator is anti-conservative in the served bins so the conditional bound of Proposition~\ref{prop:cond} does not hold in practice, the hit rate is very sensitive to errors in the cloud's intent identifiers, and a degraded mode that checks only the combined risk answers wrong questions. The risk control is conditional on stated assumptions and is not a clinical safety guarantee.

As future work we plan to (1) validate the calibrator on real labelled sentence pairs with a named sentence encoder (\sref{sec:protocol}) and rerun the simulator with the resulting distributions; (2) develop a per-intent or per-pair calibrator and a randomised candidate-level audit with propensity correction, and add distribution-free guarantees by conformal calibration~\cite{angelopoulos2021} and tail-risk budgets by conditional value at risk~\cite{rockafellar2000}; (3) measure power on target hardware; (4) fit update rates to measured revision logs and compare with a learned-threshold cache~\cite{schroeder2026}; (5) evaluate a deny-list router with a measured confusion matrix and its lifecycle, and the tenant-isolation and adversarial threats of \sref{sec:security}; and (6) run a supervised clinical pilot, with clinicians setting the severity weights, to validate the safety margins on real traffic.

"""

full = head + mid + bib
# placeholder evaluation
pat = re.compile(r"@@(.+?)@@", re.S)


def ev(m):
    expr = m.group(1)
    try:
        return str(eval(expr, {"T": T}))
    except Exception as e:
        print("ERR", expr[:80], e)
        return "??"


out = pat.sub(ev, full)
# fix escaped \@@ artefacts
out = out.replace("\\@", "\\")
open(BASE + "paper/raasc_v5.tex", "w").write(out)
print("written", len(out))
