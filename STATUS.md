# Turing queue status

Updated 2026-10-31T16:25:38Z by `proto/turing/queue_runner.py` on Turing. Requests: `jobs.json` on this branch.

| request | kind | status | Slurm job | tasks done / failed | submitted | finished | note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| surr_pipe_b1 | surrogate_pipeline | completed | 2429764 | 1 / 0 | 2026-10-29T20:41:52Z | 2026-10-29T22:42:00Z |  |
| whatif_v1 | whatif_pipeline | completed | 2431083 | 1 / 0 | 2026-10-30T05:12:49Z | 2026-10-30T05:42:40Z |  |
| vel_run_v1 | run_storm | completed | 2439311 | 1 / 0 | 2026-10-31T13:53:49Z | 2026-10-31T14:24:14Z |  |
| vel_pack_v1 | pack_site | completed | 2439312 | 1 / 0 | 2026-10-31T13:53:49Z | 2026-10-31T15:55:20Z |  |
| run_aug2026_leominster | run_storm | completed | 2439493 | 1 / 0 | 2026-10-31T15:24:48Z | 2026-10-31T16:25:37Z |  |
| pack_aug2026_leominster | pack_site | running | 2439494 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| run_sep2021_worcester | run_storm | completed | 2439495 | 1 / 0 | 2026-10-31T15:24:48Z | 2026-10-31T16:25:37Z |  |
| pack_sep2021_worcester | pack_site | running | 2439496 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| run_jun2020_northbridge | run_storm | pending | 2439497 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| pack_jun2020_northbridge | pack_site | pending | 2439498 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| run_aug2023_metrowest | run_storm | pending | 2439499 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| pack_aug2023_metrowest | pack_site | pending | 2439500 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| run_jul2023_worcester | run_storm | pending | 2439501 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| pack_jul2023_worcester | pack_site | pending | 2439502 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| run_sep2018_fitchburg | run_storm | pending | 2439503 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| pack_sep2018_fitchburg | pack_site | pending | 2439504 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| run_sep2022_webster | run_storm | pending | 2439505 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| pack_sep2022_webster | pack_site | pending | 2439506 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| run_sep2018m_milford | run_storm | pending | 2439507 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| pack_sep2018m_milford | pack_site | pending | 2439508 | 0 / 0 | 2026-10-31T15:24:48Z |  |  |
| amcnwm_base_aug2018b | run_storm | submitted | 2439666 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_nwm_aug2018b | run_storm | submitted | 2439667 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_base_aug2019 | run_storm | submitted | 2439668 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_nwm_aug2019 | run_storm | submitted | 2439669 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_base_aug2020b | run_storm | submitted | 2439670 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_nwm_aug2020b | run_storm | submitted | 2439671 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_base_aug2021 | run_storm | submitted | 2439672 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_nwm_aug2021 | run_storm | submitted | 2439673 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_base_aug2023 | run_storm | submitted | 2439674 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_nwm_aug2023 | run_storm | submitted | 2439675 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_collect_1 | collect_group | submitted | 2439676 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_base_aug2023b | run_storm | submitted | 2439677 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_nwm_aug2023b | run_storm | submitted | 2439678 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_base_aug2026 | run_storm | submitted | 2439679 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_nwm_aug2026 | run_storm | submitted | 2439681 |  /  | 2026-10-31T16:25:37Z |  |  |
| amcnwm_base_jul2019 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jul2019 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_jul2021 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jul2021 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_jul2021b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jul2021b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_collect_2 |  | rejected |  |  /  | 2026-10-31T16:25:37Z |  | a dependency failed or was rejected |
| amcnwm_base_jul2023 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jul2023 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_jul2023b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jul2023b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_jul2023c | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jul2023c | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_jul2023d | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jul2023d | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_jun2020 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jun2020 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_collect_3 |  | rejected |  |  /  | 2026-10-31T16:25:37Z |  | a dependency failed or was rejected |
| amcnwm_base_jun2020b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_jun2020b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_may2018 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_may2018 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_sep2018 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2018 | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_sep2018b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2018b | run_storm | failed |  |  /  | 2026-10-31T16:25:37Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_sep2018m | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2018m | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_collect_4 |  | rejected |  |  /  | 2026-10-31T16:25:38Z |  | a dependency failed or was rejected |
| amcnwm_base_sep2018w | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2018w | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_sep2019 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2019 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_sep2021 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2021 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_sep2022 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2022 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_base_sep2023 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_nwm_sep2023 | run_storm | failed |  |  /  | 2026-10-31T16:25:38Z |  | sbatch: error: QOSMaxSubmitJobPerUserLimit
sbatch: error: Batch job submission failed: Job violates accounting/QOS polic |
| amcnwm_collect_5 |  | rejected |  |  /  | 2026-10-31T16:25:38Z |  | a dependency failed or was rejected |
