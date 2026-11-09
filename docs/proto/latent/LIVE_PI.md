# Live calibrated flooding probability: results of checks 1-3 (9 Nov 2026)

Pre-registration: `PREREG_LIVE_PI.md` (8 Nov). Code: `proto/latent_live.py check`. Run on Turing (`proto/turing/pitest.slurm`, job 2487106,
CPU only) over the 9 terrain-fix (T2) replay runs `results/site_*_t2`. Raw output: `live_pi_check_t2.json`.

**Read this first:** the frozen fit (`fit_all.json`, 28 Oct) was fitted on the same 25 storms, on the runs before T2. So these checks show
that π carries over to the live physics (T2 terrain, depth from rain onset) without refitting. They do not show how it does on new storms;
the held-out evidence is the earlier leave-one-storm-out result in `LATENT.md` (recall 0.204 -> 0.327). The forward test (new storms) decides
that.

| check | threshold | result | |
|---|---|---|---|
| 1 calibration in the large (reported segments / expected) | pooled 0.67-1.5, each storm 1/3-3 | pooled **0.79**; storms 0.56-2.69 | pass |
| 2 ranking: report sites in the top 3 % | π not lower than p_close by more than 0.03 | p_close **0.224** -> π **0.381** (98 sites) | pass |
| 3 Leominster sep2023, DPW complete inventory | Brier skill > 0; top fifth within ±0.10 | Brier skill **+0.16**; top fifth 0.30 predicted vs 0.24 observed | pass |
| 4 no-rain forced cycle (test_pi, 8 Nov 12Z, forced water map): mean π of the top 10 roads | < 0.20 | **0.005** (max 0.006, none above 10 %) | pass |

Per storm (reported segments vs expected; sites hit in the top 3 %, p_close -> π; segments with π >= 0.5):

| storm | obs / exp | sites hit | π >= 0.5 |
|---|---|---|---|
| sep2023 | 119 / 193.8 (0.61) | 28 -> 48 of 84 | 77 |
| aug2023 | 32 / 25.4 (1.26) | 1 -> 3 of 18 | 2 |
| aug2026 | 25 / 15.6 (1.61) | 0 -> 0 of 12 | 0 |
| sep2021 | 17 / 13.5 (1.26) | 3 -> 4 of 8 | 0 |
| jun2020 | 14 / 17.8 (0.79) | 0 -> 0 of 6 | 0 |
| jul2023 | 9 / 10.3 (0.88) | 0 -> 0 of 6 | 0 |
| sep2018 | 9 / 3.3 (2.69) | 1 -> 0 of 5 | 0 |
| sep2018m | 8 / 14.2 (0.56) | 0 -> 0 of 4 | 0 |
| sep2022 | 8 / 11.4 (0.70) | 0 -> 1 of 4 | 3 |

What it means: π gives probabilities that roughly add up to what is reported (within a factor of about 1.3 pooled), it ranks report sites
much higher than the depth rule, and in Leominster, where the city logged every flooded street, roads it gives about 30 % flooded about 24 %
of the time. Most roads in most storms stay below 50 %; only the big storm (Sept 2023) gives many roads above 50 %.

All four checks passed (check 4 on forecast run 42592456041, 9 Nov). As pre-registered, the forecast now shows "Chance of flooding X %" on the
road rows and in the road details; the headline stays the k-of-8 count. Every forecast member computes π (forecast.yml, proto/latent_live.py);
the mean over members is in kofn.json (pi, pi_seg) and on the roads (pi). The forward test will show how it does on new storms.
