# Roster: agents, compute, schedule, queue issues

Snapshot: **Mon 19 Oct 2026, 07:50 ET**. Queue file audited at commit `55479216` (pending South River jobs pinned to `4dc291ea`).
Maintained by the secretary agent (owns `docs/ops/` only). Nothing here changes the queue: every fix below is a suggestion for the lead.

Times are ET. Assumed durations: South River 10 m about 4.0 h on an L4 and 4.75 h on a T4 (range 3.5 to 5 h); statewide 30 m about 8.5 h on an L4, including w5 tiles and w6 scoring; smoke test about 0.5 h. The worker polls every 2 min when idle.

---

## (a) Agents

| Agent | Role | Status | Owns (may edit) | Reports to |
|---|---|---|---|---|
| **Mo** (human) | PhD student and project owner. Approves decisions, holds the accounts (Colab x2, Kaggle, Hugging Face token, GitHub, WPI Turing request, NAACC account) and starts or restarts the GPU sessions | active | everything; the only one who handles tokens and account actions | advisors |
| **Lead** (Claude) | Coordinator of everything: engine and worker code, the queue, the work log, validation write-ups, merging agent output | active | `sim/colab/*.py`, `sim/solver.py`, `sim/validate.py`, `docs/queue/jobs.json`, `docs/progress.json` (work log), `docs/reviews/`, and by default any path no one else owns (site HTML, `refresh/`, `tools/`, `.github/workflows/`) | Mo |
| **Bug-review agent** (Claude) | Read-only review of the engine, worker, validate and crossings code | **finished**. 4 confirmed findings were fixed in `031998ce` | none (read-only) | Lead |
| **Research scout** (Claude) | State of the art, competitors, data sources, ideas | **running** (`docs/research/` is still empty at 07:50) | `docs/research/` only | Lead |
| **Secretary** (Claude, this file) | Queue audit, schedule projection, roster, coordination rules | active | `docs/ops/` only | Lead |

## (b) Compute

| Machine | Worker name | GPU / memory | Limits | Current job (snapshot) | Expected finish | Next job (current queue, simulated) |
|---|---|---|---|---|---|---|
| **BOT1**, Colab | `colab1` | L4, 24 GB (GPU_GB 22) | Colab can drop the runtime at any time; it was idle-disconnected at 00:15 and VM-reset at about 04:20 last night. Worker started before 07:18, so it runs the **pre-fix worker.py** | `sep2023_v3b_30m`, w4, 132 min (claimed about 05:38, heartbeat 2 min ago) | **13:40 to 14:40** (central 14:10) | `tiles_jul2023_whetstone_v3_10m` (only if its status is queued and `runs/jul2023_whetstone_v3_10m/meta.json` exists), then **idle**. Every other runnable job has `only: [colab2, kaggle]` |
| **BOT2**, Colab | `colab2` | L4, 24 GB (GPU_GB 22) | same as BOT1; pre-fix worker.py | `jul2023_southriver_v3n07b_10m`, w4, 127 min (claimed about 05:43) | **09:15 to 10:45** (central 09:45) | `smoke_4c03ab91`, then `jul2023_southriver_v3brch_10m` |
| **BOT3**, Kaggle | `kaggle` | 2x T4, uses one 15 GB card (launcher default GPU_GB 14) | **12 h session cap**, so this session ends about **19:00**. **30 h/week quota**: the previous session (about 18:50 to 06:50) used about 12 h, and this one will use about 12 h more, which leaves 6 h or less until the weekly reset. Pre-fix worker.py | `jul2023_southriver_v3dryA_10m`, w4, 46 min (claimed about 07:04) | **10:35 to 12:05** (central 11:50) | `jul2023_southriver_v3dryK_10m`, then `jul2023_southriver_v3snapb_10m`, **which the 19:00 cap will kill** (see issue 1) |
| GitHub Actions | none | CPU | about 6 h per job; data workflows run by hand; `refresh.yml` runs every 6 h (00:17, 06:17, 12:17, 18:17 UTC) | data refresh only (not part of the GPU queue) | n/a | next refresh at 08:17 ET (12:17 UTC) |
| WPI Turing | none | n/a | **pending**: Mo has to request an account | none | n/a | none |

## (c) Projected schedule, next 24 h (to Tue 07:50)

### As the queue stands now (no changes)

| Time (central) | colab1 (L4) | colab2 (L4) | kaggle (T4) |
|---|---|---|---|
| 07:50 | sep2023_v3b_30m (since 05:38) | n07b (since 05:43) | dryA (since 07:04) |
| 09:45 | | n07b done, then **smoke_4c03ab91** (claimed before `kaggle` frees) | |
| 10:15 | | smoke done, then **brch** (prio 10) | |
| 11:50 | | | dryA done, then **dryK** (prio 9; gated only by the *old* smoke) |
| 14:10 | sep done, then whetstone tiles (if eligible, about 15 min), then **idle** for the rest of the day and night | | |
| 14:15 | | brch done, then **dryAK** (prio 8) | |
| 16:35 | | | dryK done, then **snapb** (prio 7, attempt 2 of 2) |
| 18:15 | | dryAK done, then **n13** (prio 6) | |
| about 19:00 | | | **Kaggle 12 h cap kills snapb** after about 2.4 h of its about 4.75 h run. Attempts reach 2, so snapb is **locked out** for good (the worker never retries at 2 attempts) |
| 22:15 | | n13 done, then coast_northshore_jan2018_10m (w8, unpinned) | (no session) |
| overnight | idle | coast_southshore_jan2018_10m | (no session; quota nearly used) |

Outcome by Tue morning: n07b, dryA, smoke, brch, dryK, dryAK and n13 are done, with the coast 10 m runs probably done too. **snapb is lost and locked.** colab1 sits idle for about 17 h. The dryK, dryAK and n13 runs all happen on the un-breached bed, which the 07:44 diagnosis says is mis-specified.

### With the suggested fixes (issues 1 to 5 below applied before 09:45)

| Time (central) | colab1 (L4) | colab2 (L4) | kaggle (T4) |
|---|---|---|---|
| 09:45 | | smoke_4c03ab91 plus the new validate check (score job, a few minutes; can run on any worker) | |
| 10:15 | | **brch** | |
| 11:50 | | | **snapb** (same-commit control for brch; finishes about 16:35, well before the 19:00 cap) |
| 14:10 | sep done, then whetstone tiles, then **re-score jobs** for n07b, dryA and sep (minutes each) | | |
| 14:15 | brch is done, so (about one poll later) **dryK** (or a BREACH=1 variant, the lead's call after reading brch) | | |
| 14:15 | | **dryAK** (or a BREACH=1 variant) | |
| 16:35 | | | snapb done. Claim nothing over 2 h; stop the session to save quota |
| 18:15 to 18:30 | **n13** | coast_northshore | |
| overnight | | coast_southshore | |

Gain: snapb survives, brch is compared against a same-commit control the same afternoon, the drier-ground and roughness tests can be re-decided on the brch result, colab1 does about 10 h of extra work, and Kaggle stops before it burns its last quota.

---

## (d) Issues found, most important first, each with a suggested fix

**1. snapb will be killed by the Kaggle 12 h cap and then locked out.** Its dead claim (heartbeat 59 min old, attempts 1, from the session that hit the cap at about 06:50) is already re-claimable. In the simulation `kaggle` claims it at about 16:35 and the cap kills it at about 19:00. That makes attempts 2, and `pick()` then refuses it permanently. The same thing happened to the previous session: dec2023 took 8.7 h, then snapb started and died at the cap.
*Fix:* (a) raise snapb to prio 10 so it starts before the long tail (or pin it with `only: ["colab1","colab2"]`). (b) Add a session deadline to the worker. For example, the Kaggle launcher passes `SESSION_END=<epoch>` and jobs carry `est_h`, and `runnable()` skips a job when `now + est_h > SESSION_END`. (c) Until (b) exists, keep jobs over 2 h off Kaggle after about 14:00 ET.

**2. colab1 is excluded from every pending South River and coast job.** All of them have `only: ["colab2","kaggle"]`, left over from "keep BOT 1 free for the Sept rerun" (`75a7018a`), which no longer applies. After sep ends (about 14:10), colab1 idles for about 17 h, burning Colab compute units and inviting another idle disconnect.
*Fix:* remove `only` from smoke_4c03ab91, brch, snapb, dryK, dryAK, n13 and both coast jobs, or add `colab1` to each list.

**3. Wrong gating: jobs pinned to 4dc291ea are gated by a smoke test at a different commit, or by none.** dryK and dryAK have `after: ["smoke_e31e82b5"]`, a smoke test of `e31e82b5`, which predates the upload/meta changes (`031998ce`) and validate changes now in their path. snapb and n13 have no `after` at all. If smoke_4c03ab91 fails, all four still run for about 4 h each.
*Fix:* set `after: ["smoke_4c03ab91"]` on snapb, n13, dryK and dryAK (and on the coast jobs once they are pinned, issue 7).

**4. The 4dc291ea `sim/validate.py` change is not smoke-tested by anything.** smoke_4c03ab91 runs w6 at `4c03ab91`, but the real runs use `4dc291ea`, whose `wse_alt()` and new score keys are new code. A crash there makes w6 exit non-zero, so the job is marked `failed` *after* its 4 h w4 has already uploaded. The worker then auto-retries the **whole job** (w4 again), and the second failure locks it.
*Fix:* add a few-minute validate check at 4dc291ea before brch, with no `only` and prio 12, and put it in the `after` lists of brch, snapb, dryK, dryAK and n13:
`{"id":"score_jul2023_southriver_v3_10m_4dc291ea","kind":"score","run_dir":"runs/jul2023_southriver_v3_10m","env":{"RUN_DIR":"runs/jul2023_southriver_v3_10m","GIT_SHA":"4dc291ea"},"steps":["w6"],"gpu_gb":1,"priority":12,"requires_run_dir":true}`
Alternatively, re-pin smoke_4c03ab91 itself to 4dc291ea (the engine is byte-identical).

**5. Value order: the drier-ground and roughness tests run on the un-breached bed before the breaching result is in.** The 07:44 diagnosis puts the South River bias (+2.2 to +2.8 m) on a 1.3 m sill in the burnt channel. dryK (prio 9) starts at about 11:50 and dryAK at about 14:15, before or right as brch reports, so their numbers will be dominated by the sill. snapb (defaults at 4dc291ea, saves hsnap) is the clean same-commit control for brch, yet it sits *below* them at prio 7.
*Fix:* move snapb to prio 10 (with issue 1). Give dryK, dryAK and n13 `after: ["jul2023_southriver_v3brch_10m"]`, then decide whether to run them as BREACH=1 variants (new TAGs, for example `_v3brchdryK`) once brch is scored.

**6. All three running workers use the pre-`031998ce` worker.py.** They were launched before 07:18. Old behaviour: (i) a failed status-file read is logged and skipped, so that job looks `queued` and can be claimed again; (ii) a failed owner check is treated as "still ours", so a worker can overwrite a newer claim. The concrete risk is that an idle colab1 re-runs **done** `dec2023_v3_30m` (prio 9, no `only`) after one transient HF read error, spending 8.5 h and overwriting `runs/dec2023_v3_30m`.
*Fix:* (a) Mo restarts the worker cell on colab1 as soon as sep finishes, and on colab2 and Kaggle at their next session start. (b) Meanwhile, the lead can prune finished jobs from jobs.json (smoke_e31e82b5, dec2023_v3_30m, tiles_jul2023_southriver_v3_10m). A job absent from the list can never be picked, and `after` checks HF status, not the list, so dryK and dryAK still see smoke_e31e82b5 as done.

**7. Unpinned jobs run whatever commit each worker started at.** coast_northshore, coast_southshore and both tiles jobs have no `GIT_SHA`, so w8, w5 and w6 run at the worker's start-up sha. That sha differs per machine and predates `031998ce` on all three. `w8_coast_gpu.py` also lacks the upload-failure exit and the meta.json-last ordering that w4 got.
*Fix:* pin coast and tiles jobs to `4dc291ea` (or later). Port the w4 upload guard (`sys.exit(1)` on a failed chunk, meta.json last) to w8 before the coast 10 m jobs run.

**8. Runs on older commits need re-scoring before they are compared.** n07b and sep2023_v3b (`6f12a7b4`) and dryA (`e31e82b5`) run w6 at their own sha, which has no hsnap scoring (added in `67669294`) and no nearest/median WSE metrics (added in `4dc291ea`). They also lack the meta provenance fields (git_sha, antecedent source, hours) and the upload-failure guard, so a half-uploaded run could still report `done`.
*Fix:* after each finishes, check its log for `UPLOAD`/`retry 4` and for "14/14 days" antecedent. Then queue `score` jobs at 4dc291ea for `runs/jul2023_southriver_v3n07_10m`, `runs/jul2023_southriver_v3dryA_10m` and `runs/sep2023_v3_30m` (`requires_run_dir: true`, gpu_gb 1, no `only`). These are good filler for colab1. dryA (e31e82b5) compared with dryK and dryAK (4dc291ea) is a fair comparison only if the dryA log shows 14/14 antecedent days, because the 12/14 rescaling in `031998ce` is the only default-path engine change.

**9. Dead "running" claims.**
- `jul2023_southriver_v3snapb_10m`: claim from the old Kaggle session, stale (more than 40 min). The next free colab2 or kaggle worker will re-claim it as **attempt 2 of 2** (see issue 1).
- `sep2023_v3_30m`: claim from colab2, stale for 132 min. The job is no longer in jobs.json, so nothing will ever pick it up. Its HF status will say `running` forever, which can mislead dashboards and the progress page. *Fix (optional):* the lead writes a final status `{"state":"failed","note":"superseded by sep2023_v3b_30m"}`.
- `n07` and `snap` are `failed` and removed from the list. Their retries reuse the same run dirs on purpose (see issue 10).

**10. Shared run dirs (intentional, but worth knowing).** No two *pending* jobs write the same dir. Three retries reuse their predecessor's dir by keeping the TAG and changing only the id:
- sep2023_v3b goes to `runs/sep2023_v3_30m`
- n07b goes to `runs/jul2023_southriver_v3n07_10m`
- snapb goes to `runs/jul2023_southriver_v3snap_10m`

Each predecessor died before upload, so nothing is half-mixed. But a re-upload only *adds or overwrites* files, so a stale file that an older attempt uploaded would survive.
*Fix:* when retrying a job whose predecessor reached the upload step, change the TAG (for example `_v3snapc`) or delete the old dir first.

**11. Smaller items.**
- **Kaggle uses one of two T4s.** A second worker pinned to the other card (`CUDA_VISIBLE_DEVICES=1`, `WORKER=kaggle2`, with `kaggle2` added to `only` lists) could double Kaggle throughput for the same quota hours. Check host RAM (about 29 GB) for two 10 m runs first.
- **Smoke-run naming is inconsistent.** smoke_e31e82b5 uses `RUN=test_leominster`. smoke_4c03ab91 uses `RUN=jul2023_southriver`, so its output `runs/jul2023_southriver_smoke_4c03ab91_10m` sits among the real South River runs and may appear in the v2 run picker. See RULES.md for naming.
- **Notes do not match envs.** smoke_e31e82b5's note says "2-hour", but it has `HOURS=3`. snapb's TAG `_v3snap` and its "Manning x1.0" note describe what is now just the defaults control run.
- **`docs/progress.json` stage 3 still reads "Kaggle: Dec v3 finishing".** Dec finished hours ago; Kaggle is on dryA.
- **`tiles_jul2023_whetstone_v3_10m` is not in the snapshot.** It runs on any worker as soon as `runs/jul2023_whetstone_v3_10m/meta.json` exists. If that run was made before meta.json was guaranteed, confirm the file exists, or the job waits forever.
