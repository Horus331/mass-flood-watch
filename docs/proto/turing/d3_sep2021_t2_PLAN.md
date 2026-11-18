# District 3 run of the September 2021 storm (Ida remnants) on the T2 terrain: plan (fixed before the run, 18 Nov 2026)

**Why.** Paper 1 §4.5 / §5.4 report consequences (closures, delay, residents losing timely access to emergency services, the share of them
on dry roads) for the September 2023 storm only, which is the calibration storm (`paper/REVIEW_SELF.md` M4). This run repeats the same
analysis on a held-out storm. It is a **reporting run**: no setting changes, no decision depends on it, nothing goes to the live site.

**Storm.** `sep2021` (1–2 Sept 2021, Ida remnants; held-out in PROTOCOL v2, not locked). Rain window from `sim/colab/w9_lisflood.py`
STORMS (t0 2021-09-01T18:00Z), 48 h as for the September 2023 District run.

**Settings.** Identical to `d3_sep2023_t2` (`docs/proto/turing/d3_sep2023_t2/`): District box 128000,856000,206000,946000 (EPSG:26986), 20 m,
`LF_CN_SCALE=0.88`, `LF_PARITY=1`, `LF_NOTCH_FIX=1`, `LF_CHAN_ENFORCE=1`, `PROTO_CASCADE=1`, `LF_SAVEINT=1800`,
`PROTO_RES_CONSISTENT=1`, `PROTO_RC_START_H=rain`. GPU solve and CPU post-processing as separate requests (queue rules).

**What will be reported** (same definitions and code as §4.5; `proto/paper_figs.py`-style extraction from `cascade.json`):
1. segments closed at some time and at the peak, and when the peak happens;
2. added vehicle-hours per hour at the peak and over 48 h;
3. residents losing timely access to a hospital (30 min), fire station (8 min) or police station (10 min) at the peak, and the share of
   them, and of the person-hours, on roads that stay dry;
4. segments closed before the rain starts (should be ≈ 0 after the start-up fix);
5. site recall of the storm's reports for the District run (secondary; reports are approximate).

**How it will be read (fixed now).** The paper's claim "consequences fall mostly on dry roads" is supported on a second storm if the
dry-road share of residents losing access is ≥ 80 %. If it is lower, §5.4 is rewritten to report both storms and the range. Whatever
the result, both storms are reported. No model setting is changed because of this run.
