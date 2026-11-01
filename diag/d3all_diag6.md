# Turing diagnostics: d3all_diag6

2026-11-01T19:41:56Z on compute-2-05.int.turing.wpi.edu, job 2443650, repo 9308fb07

## disk and quota

```
$ df -h /home/mgeldokla /home/mgeldokla/scratch /home/mgeldokla/scratch/lisflood
Filesystem                                                                                                                                                        Size  Used Avail Use% Mounted on
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/home/1c0b431a-0173-438f-85b5-1dfe3ac805cc     1.8P  1.2P  656T  64% /home
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  656T  64% /scratch
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  656T  64% /scratch
$ readlink -f /home/mgeldokla/scratch
/scratch/mgeldokla
$ quota -s
timeout: failed to run command 'quota': Permission denied
$ bash -c du -sh /home/mgeldokla/scratch/lisflood/* 2>/dev/null | sort -h | tail -n 50
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r050_normal_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r050_normal_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r050_wet_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r050_wet_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_dry_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_dry_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_frozen_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_frozen_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_normal_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_normal_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_wet_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r075_wet_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_dry_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_dry_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_frozen_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_frozen_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_normal_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_normal_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_wet_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r100_wet_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_dry_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_dry_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_frozen_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_frozen_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_normal_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_normal_open
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_wet_blocked
2.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_whatif_r125_wet_open
5.0G	/home/mgeldokla/scratch/lisflood/run_sep2018m_proto_site_sep2018m_milford
5.1G	/home/mgeldokla/scratch/lisflood/run_aug2023_proto_site_aug2023_metrowest
5.1G	/home/mgeldokla/scratch/lisflood/run_jul2023_proto_site_jul2023_worcester
5.1G	/home/mgeldokla/scratch/lisflood/run_jun2020_proto_site_jun2020_northbridge
5.3G	/home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster
5.4G	/home/mgeldokla/scratch/lisflood/run_aug2026_proto_site_aug2026_leominster
5.4G	/home/mgeldokla/scratch/lisflood/run_sep2018_proto_site_sep2018_fitchburg
6.1G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_sep2023_10m
6.5G	/home/mgeldokla/scratch/lisflood/run_sep2021_proto_site_sep2021_worcester
7.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_sep2023_5min
7.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_sep2023_p
7.9G	/home/mgeldokla/scratch/lisflood/run_aug2021_proto_worcester_aug2021_5min
7.9G	/home/mgeldokla/scratch/lisflood/run_aug2021_proto_worcester_aug2021_p
8.5G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_vel
27G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_20m
27G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_p
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_18z_nb10p90
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_18z_nb20p75
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_18z_raw
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_sep2023_18z
35G	/home/mgeldokla/scratch/lisflood/amcnwm_v1
41G	/home/mgeldokla/scratch/lisflood/inlets_v1
$ du -sh /home/mgeldokla/scratch/lisflood
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0013.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0016.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0018.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0023.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0026.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0012.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0019.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0027.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0027.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0031.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0020.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0034.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0042.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0020.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0021.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0012.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0022.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0019.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0036.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0035.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0015.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0038.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0025.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0023.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0039.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0022.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0044.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0032.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0024.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0016.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0029.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0015.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0029.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0037.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0034.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0033.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0017.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0041.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0048.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0030.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0039.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0045.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0040.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0042.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0014.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0031.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0024.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0013.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0050.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0014.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0041.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0032.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0047.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0043.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0028.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0017.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0040.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0025.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0049.Qx': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0026.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0044.Qy': No such file or directory
du: cannot access '/home/mgeldokla/scratch/lisflood/amcnwm_v1/work_amcnwm_base_sep2023/run_sep2023_proto_amcnwm_base_sep2023/results/res-0043.Qy': No such file or directory
461G	/home/mgeldokla/scratch/lisflood
```

## Slurm limits (submit cap)

```
$ sacctmgr -n -P show assoc user=mgeldokla format=cluster,account,partition,qos,maxsubmit,maxjobs,grptres,maxwall
slurm|taomj||long,quick,short||||
$ sacctmgr -n -P show qos format=name,maxsubmitpu,maxjobspu,maxtrespu,maxwall,grpjobs,grpsubmit,flags
normal|||||||DenyOnLimit
short|100||cpu=1024,gres/gpu=12,mem=8T||||DenyOnLimit
long|100||cpu=256,gres/gpu=4,mem=3T||||DenyOnLimit
quick|20||cpu=64,gres/gpu=1,mem=256G||||DenyOnLimit
academic||24|cpu=64,gres/gpu=2,mem=250G||||DenyOnLimit
scavenger|||||||DenyOnLimit,NoReserve
service|||||||
$ sinfo -o %P %a %l %D %G %c %m
PARTITION AVAIL TIMELIMIT NODES GRES CPUS MEMORY
academic up 2-00:00:00 8 gpu:A30:4(S:0-1),gpumem:no_consume:24G 96 244140
academic up 2-00:00:00 8 (null) 192 1536000
short* up 1-00:00:00 4 gpu:A100:4,gpumem:no_consume:80G 64 512000
short* up 1-00:00:00 1 gpu:H200:8(S:0-1),gpumem:no_consume:141G 128 1536000
short* up 1-00:00:00 12 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 96 512000
short* up 1-00:00:00 2 gpu:H100:4(S:0-1),gpumem:no_consume:80G 128 512000
short* up 1-00:00:00 20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 96 512000
short* up 1-00:00:00 30 (null) 64+ 512000+
short* up 1-00:00:00 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
short* up 1-00:00:00 1 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 96 1024000
long up 7-00:00:00 4 gpu:A100:4,gpumem:no_consume:80G 64 512000
long up 7-00:00:00 12 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 96 512000
long up 7-00:00:00 20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 96 512000
long up 7-00:00:00 30 (null) 64+ 512000+
long up 7-00:00:00 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
long up 7-00:00:00 1 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 96 1024000
quick up 12:00:00 4 gpu:A100:4,gpumem:no_consume:80G 64 512000
quick up 12:00:00 1 gpu:H200:8(S:0-1),gpumem:no_consume:141G 128 1536000
quick up 12:00:00 12 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 96 512000
quick up 12:00:00 2 gpu:H100:4(S:0-1),gpumem:no_consume:80G 128 512000
quick up 12:00:00 20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 96 512000
quick up 12:00:00 30 (null) 64+ 512000+
quick up 12:00:00 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
quick up 12:00:00 1 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 96 1024000
research up infinite 4 gpu:A100:4,gpumem:no_consume:80G 64 512000
research up infinite 1 gpu:H200:8(S:0-1),gpumem:no_consume:141G 128 1536000
research up infinite 12 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 96 512000
research up infinite 2 gpu:H100:4(S:0-1),gpumem:no_consume:80G 128 512000
research up infinite 20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 96 512000
research up infinite 24 (null) 64+ 512000+
scavenger up infinite 4 gpu:A100:4,gpumem:no_consume:80G 64 512000
scavenger up infinite 1 gpu:H200:8(S:0-1),gpumem:no_consume:141G 128 1536000
scavenger up infinite 12 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 96 512000
scavenger up infinite 8 gpu:A30:4(S:0-1),gpumem:no_consume:24G 96 244140
scavenger up infinite 2 gpu:H100:4(S:0-1),gpumem:no_consume:80G 128 512000
scavenger up infinite 20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 96 512000
scavenger up infinite 31 (null) 64+ 512000+
scavenger up infinite 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
scavenger up infinite 1 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 96 1024000
$ scontrol show partition
PartitionName=academic
   AllowGroups=ALL AllowAccounts=courses,ch2650,che554,cs4341,cs525,cs539,cs541,cs595,ds504,rbe549,rbe595,cs545,ece545,cs3733,cs586,ph1110,ph1120,ph1140,cs534,cs534,cs568,cs568,cs568,rbe577,ds598,rbe577,cs553,cs553,ds501,ds553,ds551,cs551,cs547,ece33405,ece3405,rbe577,cs552,cs554,cs549,ece556,rbe594,rbe594,bcb699,cs542,cs3010,isp,ds5006,cs555,ds502,cs568,cs568,cs568,cs568,cs568,ece341,ece341x,test
   AllocNodes=ALL Default=NO QoS=academic
   DefaultTime=12:00:00 DisableRootJobs=NO ExclusiveUser=NO ExclusiveTopo=NO GraceTime=0 Hidden=NO
   MaxNodes=4 MaxTime=2-00:00:00 MinNodes=1 LLN=NO MaxCPUsPerNode=UNLIMITED MaxCPUsPerSocket=UNLIMITED
   Nodes=compute-0-01,compute-3-[01-08],gpu-4-[21-29]
   PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=REQUEUE
   State=UP TotalCPUs=2784 TotalNodes=18 SelectTypeParameters=NONE
   JobDefaults=DefCpuPerGPU=2
   DefMemPerCPU=2048 MaxMemPerNode=UNLIMITED
   TRES=cpu=2784,mem=26773260M,node=18,billing=2784,gres/gpu=36,gres/gpumem=231928233984
   ResumeTimeout=GLOBAL SuspendTimeout=GLOBAL SuspendTime=GLOBAL PowerDownOnIdle=NO

PartitionName=short
   AllowGroups=ALL DenyAccounts=courses,ch2650,che554,cs4341,cs525,cs539,cs541,cs595,ds504,rbe549,rbe595,cs545,ece545,ece545,cs3733,cs586,ph1110,ph1120,ph1140,cs534,cs534,cs568,cs568,cs568,rbe577,ds598,rbe577,cs553,cs553,ds501,ds553,ds551,cs551,cs547,ece33405,ece3405,rbe577,cs552,cs554,cs549,ece556,rbe594,rbe594,bcb699,cs542,cs3010,isp,ds5006,cs555,ds502,cs568,cs568,cs568,cs568,cs568,ece341,ece341
   AllocNodes=ALL Default=YES CpuBind=cores  QoS=short
   DefaultTime=1-00:00:00 DisableRootJobs=NO ExclusiveUser=NO ExclusiveTopo=NO GraceTime=0 Hidden=NO
   MaxNodes=UNLIMITED MaxTime=1-00:00:00 MinNodes=1 LLN=NO MaxCPUsPerNode=UNLIMITED MaxCPUsPerSocket=UNLIMITED
   Nodes=aswin-[01-08],compute-0-01,compute-1-05,compute-2-[01-08],compute-3-[01-08],compute-4-[01-08],emmanuel-01,gpu-3-01,gpu-4-[11-15],gpu-5-[01,11-12,21-28,31-32,41-44],gpu-6-[01-20],murai-01,whitehill-0-[01-02],zhong-0-[01-04]
   PriorityJobFactor=10 PriorityTier=10 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=REQUEUE
   State=UP TotalCPUs=8524 TotalNodes=85 SelectTypeParameters=NONE
   JobDefaults=DefCpuPerGPU=2
   DefMemPerCPU=2048 MaxMemPerNode=UNLIMITED
   TRES=cpu=8488,mem=66478000M,node=85,billing=8488,gres/gpu=154,gres/gpumem=3833258311680
   ResumeTimeout=GLOBAL SuspendTimeout=GLOBAL SuspendTime=GLOBAL PowerDownOnIdle=NO

PartitionName=long
   AllowGroups=ALL DenyAccounts=courses,ch2650,che554,cs4341,cs525,cs539,cs541,cs595,ds504,rbe549,rbe595,cs545,ece545,ece545,cs3733,cs586,ph1110,ph1120,ph1140,cs534,cs534,cs568,cs568,cs568,rbe577,ds598,rbe577,cs553,cs553,ds501,ds553,ds551,cs551,cs547,ece33405,ece3405,rbe577,cs552,cs554,cs549,ece556,rbe594,rbe594,bcb699,cs542,cs3010,isp,ds5006,cs555,ds502,cs568,cs568,cs568,cs568,cs568,ece341,ece341
   AllocNodes=ALL Default=NO CpuBind=cores  QoS=long
   DefaultTime=3-00:00:00 DisableRootJobs=NO ExclusiveUser=NO ExclusiveTopo=NO GraceTime=0 Hidden=NO
   MaxNodes=UNLIMITED MaxTime=7-00:00:00 MinNodes=1 LLN=NO MaxCPUsPerNode=UNLIMITED MaxCPUsPerSocket=UNLIMITED
   Nodes=aswin-[01-08],compute-0-01,compute-1-05,compute-2-[01-08],compute-3-[01-08],compute-4-[01-08],emmanuel-01,gpu-3-01,gpu-4-[11-15],gpu-5-[01,21-28,41-44],gpu-6-[01-20],murai-01,whitehill-0-[01-02],zhong-0-[01-04]
   PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=REQUEUE
   State=UP TotalCPUs=8012 TotalNodes=81 SelectTypeParameters=NONE
   JobDefaults=(null)
   DefMemPerCPU=2048 MaxMemPerNode=UNLIMITED
   TRES=cpu=7980,mem=62382000M,node=81,billing=7980,gres/gpu=130,gres/gpumem=3358664425472
   ResumeTimeout=GLOBAL SuspendTimeout=GLOBAL SuspendTime=GLOBAL PowerDownOnIdle=NO

PartitionName=quick
   AllowGroups=ALL DenyAccounts=courses DenyQos=scavenger
   AllocNodes=ALL Default=NO CpuBind=cores  QoS=quick
   DefaultTime=06:00:00 DisableRootJobs=NO ExclusiveUser=NO ExclusiveTopo=NO GraceTime=0 Hidden=NO
   MaxNodes=2 MaxTime=12:00:00 MinNodes=1 LLN=NO MaxCPUsPerNode=UNLIMITED MaxCPUsPerSocket=UNLIMITED
   Nodes=aswin-[01-08],compute-0-01,compute-1-05,compute-2-[01-08],compute-3-[01-08],compute-4-[01-08],emmanuel-01,gpu-3-01,gpu-4-[11-15],gpu-5-[01,11-12,21-28,31-32,41-44],gpu-6-[01-20],murai-01,whitehill-0-[01-02],zhong-0-[01-04]
   PriorityJobFactor=100 PriorityTier=10 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=REQUEUE
   State=UP TotalCPUs=8524 TotalNodes=85 SelectTypeParameters=NONE
   JobDefaults=DefCpuPerGPU=2
   DefMemPerCPU=1024 MaxMemPerNode=UNLIMITED
   TRES=cpu=8488,mem=66478000M,node=85,billing=8488,gres/gpu=154,gres/gpumem=3833258311680
   ResumeTimeout=GLOBAL SuspendTimeout=GLOBAL SuspendTime=GLOBAL PowerDownOnIdle=NO

PartitionName=research
   AllowGroups=ALL AllowAccounts=turing-testing,vllm AllowQos=ALL
   AllocNodes=ALL Default=NO CpuBind=cores  QoS=N/A
   DefaultTime=1-00:00:00 DisableRootJobs=NO ExclusiveUser=NO ExclusiveTopo=NO GraceTime=0 Hidden=NO
   MaxNodes=UNLIMITED MaxTime=UNLIMITED MinNodes=1 LLN=NO MaxCPUsPerNode=UNLIMITED MaxCPUsPerSocket=UNLIMITED
   NodeSets=research
   Nodes=compute-0-01,compute-1-05,compute-2-[01-09],compute-3-[01-08],compute-4-[01-08],gpu-3-01,gpu-4-[11-15],gpu-5-[01,11-12,21-28,31-32,41-44],gpu-6-[01-20]
   PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=REQUEUE
   State=UP TotalCPUs=7640 TotalNodes=70 SelectTypeParameters=NONE
   JobDefaults=DefCpuPerGPU=2
   DefMemPerCPU=1024 MaxMemPerNode=UNLIMITED
   TRES=cpu=7604,mem=60306000M,node=70,billing=7604,gres/gpu=144,gres/gpumem=3704409292800
   ResumeTimeout=GLOBAL SuspendTimeout=GLOBAL SuspendTime=GLOBAL PowerDownOnIdle=NO

PartitionName=scavenger
   AllowGroups=ALL AllowAccounts=turing-testing AllowQos=scavenger
   AllocNodes=ALL Default=NO CpuBind=cores  QoS=N/A
   DefaultTime=1-00:00:00 DisableRootJobs=NO ExclusiveUser=NO ExclusiveTopo=NO GraceTime=0 Hidden=NO
   MaxNodes=UNLIMITED MaxTime=UNLIMITED MinNodes=1 LLN=NO MaxCPUsPerNode=UNLIMITED MaxCPUsPerSocket=UNLIMITED
   NodeSets=research,academic,whitehill,zhong,murai,aswin,emmanuel
   Nodes=aswin-[01-08],compute-0-01,compute-1-05,compute-2-[01-09],compute-3-[01-08],compute-4-[01-08],emmanuel-01,gpu-3-01,gpu-4-[11-15,21-29],gpu-5-[01,11-12,21-28,31-32,41-44],gpu-6-[01-20],murai-01,testnode,whitehill-0-[01-02],zhong-0-[01-04]
   PriorityJobFactor=1 PriorityTier=1 RootOnly=NO ReqResv=NO OverSubscribe=NO
   OverTimeLimit=NONE PreemptMode=REQUEUE
   State=UP TotalCPUs=9836 TotalNodes=96 SelectTypeParameters=NONE
   JobDefaults=DefCpuPerGPU=2
   DefMemPerCPU=1024 MaxMemPerNode=UNLIMITED
   TRES=cpu=9800,mem=81475260M,node=96,billing=9800,gres/gpu=190,gres/gpumem=4065186545664
   ResumeTimeout=GLOBAL SuspendTimeout=GLOBAL SuspendTime=GLOBAL PowerDownOnIdle=NO

$ squeue -u mgeldokla -o %i %j %P %T %M %l %R %b
JOBID NAME PARTITION STATE TIME TIME_LIMIT NODELIST(REASON) TRES_PER_NODE
2443211 q_pack_d3_sep2023_20m_d long PENDING 0:00 10:00:00 (Dependency) N/A
2443419 q_pack_d3_sep2023_20m_any long PENDING 0:00 10:00:00 (Dependency) N/A
2443210 q_run_d3_sep2023_20m_d short PENDING 0:00 10:00:00 (Priority) gres/gpu:1
2443209_[0] q_fcd3_e2etest_d3_2023091112_g short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443418 q_run_d3_sep2023_20m_any short PENDING 0:00 16:00:00 (Priority) gres/gpu:1
2443420_[0] q_fcd3_e2etest2_d3_2023091112_any short PENDING 0:00 12:00:00 (Priority) gres/gpu:1
2443461_[0-11%2] q_d3all_v1_c short PENDING 0:00 16:00:00 (Priority) gres/gpu:1
2443460_[0-11%2] q_d3all_v1_b2 short PENDING 0:00 10:00:00 (Priority) gres/gpu:1
2443649 flood_queue short PENDING 0:00 20:00 (BeginTime) N/A
2443118_39 q_amcnwm_v1_arr3 short RUNNING 1:13 3:00:00 gpu-5-23 gres/gpu:1
2443118_38 q_amcnwm_v1_arr3 short RUNNING 4:45 3:00:00 gpu-5-21 gres/gpu:1
2443650 q_d3all_diag6 short RUNNING 0:43 30:00 compute-2-05 N/A
array tasks expanded: 34, job records: 12
```

## GPU queue position (short / quick)

```
$ sprio -u mgeldokla
          JOBID PARTITION     USER   PRIORITY       SITE        AGE  FAIRSHARE    JOBSIZE  PARTITION
        2443209 short     mgeldokl      81157          0        731      79421          6       1000
        2443210 short     mgeldokl      81157          0        731      79421          6       1000
        2443211 long      mgeldokl      80257          0        731      79421          6        100
        2443418 short     mgeldokl      80857          0        430      79421          6       1000
        2443419 long      mgeldokl      79957          0        430      79421          6        100
        2443420 short     mgeldokl      80857          0        430      79421          6       1000
        2443460 short     mgeldokl      80707          0        281      79421          6       1000
        2443461 short     mgeldokl      80707          0        281      79421          6       1000
        2443649 short     mgeldokl      80426          0          0      79421          5       1000
      1 whitehill-0-02 A100 gpu:A100:2(S:0-1),gpumem:no_consume:40G mixed
      3 gpu-4-12 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G down*
      1 gpu-4-11 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G mixed@
      1 aswin-02 EPYC-7543 (null) mixed
      6 aswin-03 EPYC-7543 (null) reserved
      2 compute-2-03 EPYC-7543,AMD (null) allocated
      1 compute-2-04 EPYC-7543,AMD (null) drained
      5 compute-2-01 EPYC-7543,AMD (null) mixed
      3 compute-3-02 EPYC-9654,AMD (null) allocated
      5 compute-3-01 EPYC-9654,AMD (null) mixed
      2 gpu-5-11 H100 gpu:H100:4(S:0-1),gpumem:no_consume:80G down*
      1 gpu-5-32 H200 gpu:H200:8(S:0-1),gpumem:no_consume:141G mixed@
      7 compute-4-01 Intel,6767P (null) allocated
      1 murai-01 L40S gpu:L40S:2(S:0-1),gpumem:no_consume:48G reserved
      8 gpu-5-22 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G down*
      2 gpu-5-21 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G mixed-
      2 gpu-5-28 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G mixed@
     17 gpu-6-01 RTX6000B,Intel gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G down*
      3 gpu-6-07 RTX6000B,Intel gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G mixed@
      1 $ sinfo -N -p short -o %N %f %G %T --noheader
$ squeue -p short -t PD --sort=-p -o %i %u %Q %b %r
JOBID USER PRIORITY TRES_PER_NODE REASON
2210407 zhuang5 155508 N/A DependencyNeverSatisfied
2210346 zhuang5 155508 N/A DependencyNeverSatisfied
2413510 ttjokro 121167 N/A DependencyNeverSatisfied
2415396 afrenk 103965 N/A Dependency
2424757 mataeikachooei 100830 gres/gpu:4 Resources
2424758 mataeikachooei 100830 gres/gpu:4 Priority
2413506 zcheng3 99986 N/A BeginTime
2413505 zcheng3 99986 N/A BeginTime
2413504 zcheng3 99986 N/A BeginTime
2413503 zcheng3 99986 N/A BeginTime
2413502 zcheng3 99986 N/A BeginTime
2413501 zcheng3 99986 N/A BeginTime
2413500 zcheng3 99986 N/A BeginTime
2413499 zcheng3 99986 N/A BeginTime
2413498 zcheng3 99986 N/A BeginTime
2413497 zcheng3 99986 N/A BeginTime
2443214 cirwin 90713 gres/gpu:1 Priority
2424755 ssunku 88890 gres/gpu:1 Priority
2442010 jchang2 82640 N/A Dependency
2443210 mgeldokla 81157 gres/gpu:1 Priority
2443209_[0] mgeldokla 81157 gres/gpu:1 Priority
2443418 mgeldokla 80857 gres/gpu:1 Priority
2443420_[0] mgeldokla 80857 gres/gpu:1 Priority
2443461_[0-11%2] mgeldokla 80707 gres/gpu:1 Priority
2443460_[0-11%2] mgeldokla 80707 gres/gpu:1 Priority
2443649 mgeldokla 80426 N/A BeginTime
2435968 afrenk 79916 gres/gpu:4 Priority
2435970 afrenk 79915 gres/gpu:4 Dependency
2435969 afrenk 79915 gres/gpu:4 Dependency
2443393 jchang2 79697 gres/gpu:1 Priority
2443394 jchang2 79697 N/A Dependency
2437827 afrenk 73458 gres/gpu:4 Priority
2430148_5 yzhao19 73059 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_8 yzhao19 72306 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_7 yzhao19 72306 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_6 yzhao19 72306 gres/gpu:A100:1,gres/gpumem:75G Priority
2440628 vmullur 72189 gres/gpu:L40S:1 Priority
2440465_[0-5] pgundu 71997 gres/gpu:L40S:1 Dependency
2439442_0 pgundu 70540 gres/gpu:L40S:1 Priority
2441415 vmullur 70180 gres/gpu:L40S:1 Priority
2439491 alignatiev 70113 gres/gpu:1 Priority
2440534 bdweber 69187 gres/gpu:1 Priority
2440527 bdweber 69187 gres/gpu:1 Priority
2443078 vmullur 66655 gres/gpu:1 Priority
2439443_0 pgundu 64976 gres/gpu:L40S:1 Priority
2439443_1 pgundu 64775 gres/gpu:L40S:1 Priority
2440754 nbpulsone 64621 gres/gpu:1 Priority
2442340 klin5 64223 gres/gpu:1 Priority
2442342 klin5 64223 gres/gpu:1 Priority
2442338 klin5 64223 gres/gpu:1 Priority
2443035 alignatiev 63243 gres/gpu:1 Priority
2443482 yzhao19 60129 gres/gpu:rtx_pro_6000_b:1 Priority
2443481_[9-10] yzhao19 60129 gres/gpu:A100:1,gres/gpumem:75G Priority
2422034 bluitel 59857 N/A DependencyNeverSatisfied
2441592 zhuang5 59727 N/A Dependency
2441591 zhuang5 59727 N/A Dependency
2441590 zhuang5 59727 N/A Dependency
2441589 zhuang5 59727 N/A Dependency
2441588 zhuang5 59727 N/A Dependency
$ squeue -p quick -t PD --sort=-p -o %i %u %Q %b %r
JOBID USER PRIORITY TRES_PER_NODE REASON
2440722 dehalloran 87873 gres/gpu:A100:1 Nodes required for job are DOWN, DRAINED, REBOOTING or reserved for jobs in higher priority partitions
2440504 spatadia 86419 gres/gpu:A100:1 Priority
2441582 zhuang5 68727 gres/gpu:1,gres/gpumem:16G Priority
2441842 sselvaraj 23660 gres/gpu:1 Priority
2441863 sselvaraj 23637 gres/gpu:1 Dependency
2441862 sselvaraj 23637 gres/gpu:1 Dependency
2441861 sselvaraj 23637 gres/gpu:1 Dependency
2441860 sselvaraj 23637 gres/gpu:1 Dependency
2441859 sselvaraj 23637 gres/gpu:1 Dependency
2441858 sselvaraj 23637 gres/gpu:1 Dependency
2441857 sselvaraj 23637 gres/gpu:1 Dependency
2441856 sselvaraj 23637 gres/gpu:1 Dependency
2439893_[0-5,8] tdappenzeller 21199 gres/gpu:rtx_pro_6000_b:1 Priority
2439896_[6-7] tdappenzeller 21197 gres/gpu:rtx_pro_6000_b:1 Priority
2441270 kle6 20243 gres/gpu:1 Priority
2441269 kle6 20243 gres/gpu:1 Priority
2439853 tmondal 20079 gres/gpu:1 Priority
2443645 aakarande 17565 gres/gpu:1 Priority
2439800 aakarande 15672 gres/gpu:1 Priority
2437169 aakarande 15644 gres/gpu:1 Priority
2440949 aakarande 13606 gres/gpu:1 Priority
2443525_[0] aakarande 7752 gres/gpu:1 Priority
$ bash -c squeue -p short -t R -h -o '%b %N' | sort | uniq -c | sort -rn | head -30
     10 N/A compute-2-06
     10 N/A compute-2-03
      9 N/A compute-3-01
      9 N/A compute-2-08
      8 N/A compute-3-02
      8 N/A compute-2-07
      6 N/A compute-3-08
      5 N/A compute-3-07
      5 N/A compute-3-05
      5 N/A compute-2-01
      4 N/A compute-4-08
      4 N/A compute-4-05
      4 N/A compute-4-03
      4 N/A compute-3-06
      3 gres/gpu:L40S:1 gpu-5-21
      3 N/A compute-3-04
      3 N/A compute-3-03
      3 N/A compute-2-02
      2 gres/gpu:L40S:1 gpu-5-44
      2 gres/gpu:L40S:1 gpu-5-23
      2 gres/gpu:4 gpu-5-32
      2 gres/gpu:1 whitehill-0-02
      2 N/A compute-4-01
      2 N/A compute-2-05
      1 gres/gpu:1,gres/gpumem:80G gpu-6-07
      1 gres/gpu:1 gpu-5-23
      1 gres/gpu:1 gpu-5-21
      1 N/A compute-4-06
      1 N/A compute-4-02
      1 N/A aswin-02
$ sinfo -p short -N -o %N %G %C %T --noheader
aswin-02 (null) 1/63/0/64 mixed
aswin-03 (null) 0/64/0/64 reserved
aswin-04 (null) 0/64/0/64 reserved
aswin-05 (null) 0/64/0/64 reserved
aswin-06 (null) 0/64/0/64 reserved
aswin-07 (null) 0/64/0/64 reserved
aswin-08 (null) 0/64/0/64 reserved
compute-2-01 (null) 54/10/0/64 mixed
compute-2-02 (null) 61/3/0/64 mixed
compute-2-03 (null) 64/0/0/64 allocated
compute-2-04 (null) 0/0/64/64 drained
compute-2-05 (null) 63/1/0/64 mixed
compute-2-06 (null) 64/0/0/64 allocated
compute-2-07 (null) 61/3/0/64 mixed
compute-2-08 (null) 62/2/0/64 mixed
compute-3-01 (null) 184/8/0/192 mixed
compute-3-02 (null) 192/0/0/192 allocated
compute-3-03 (null) 125/67/0/192 mixed
compute-3-04 (null) 192/0/0/192 allocated
compute-3-05 (null) 192/0/0/192 allocated
compute-3-06 (null) 160/32/0/192 mixed
compute-3-07 (null) 124/68/0/192 mixed
compute-3-08 (null) 189/3/0/192 mixed
compute-4-01 (null) 128/0/0/128 allocated
compute-4-02 (null) 128/0/0/128 allocated
compute-4-03 (null) 128/0/0/128 allocated
compute-4-05 (null) 128/0/0/128 allocated
compute-4-06 (null) 128/0/0/128 allocated
compute-4-07 (null) 128/0/0/128 allocated
compute-4-08 (null) 128/0/0/128 allocated
gpu-4-11 gpu:A100:4,gpumem:no_consume:80G 32/32/0/64 mixed@
gpu-4-12 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-4-14 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-4-15 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-5-11 gpu:H100:4(S:0-1),gpumem:no_consume:80G 0/0/128/128 down*
gpu-5-12 gpu:H100:4(S:0-1),gpumem:no_consume:80G 0/0/128/128 down*
gpu-5-21 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 20/76/0/96 mixed-
gpu-5-22 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-23 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 18/78/0/96 mixed-
gpu-5-24 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-25 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-26 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-27 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-28 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 4/92/0/96 mixed@
gpu-5-32 gpu:H200:8(S:0-1),gpumem:no_consume:141G 32/96/0/128 mixed@
gpu-5-41 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-42 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-43 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-44 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 8/88/0/96 mixed@
gpu-6-01 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-02 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-03 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-04 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-05 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-06 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-07 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 8/88/0/96 mixed@
gpu-6-08 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-09 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-10 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-11 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-12 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 24/72/0/96 mixed@
gpu-6-13 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-14 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-15 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 32/64/0/96 mixed@
gpu-6-16 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-17 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-18 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-19 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
murai-01 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 0/96/0/96 reserved
whitehill-0-02 gpu:A100:2(S:0-1),gpumem:no_consume:40G 10/102/0/112 mixed
```

## sacct 2443460,2443461

```
$ sacct -P -j 2443460,2443461 --format=JobID,JobName%30,Partition,State,ExitCode,Submit,Start,End,Elapsed,MaxRSS,ReqMem,AllocTRES%60,NodeList
JobID|JobName|Partition|State|ExitCode|Submit|Start|End|Elapsed|MaxRSS|ReqMem|AllocTRES|NodeList
2443460_[0-11%2]|q_d3all_v1_b2|short|PENDING|0:0|2026-11-01T18:41:02|Unknown|Unknown|00:00:00||160G||None assigned
2443461_[0-11%2]|q_d3all_v1_c|short|PENDING|0:0|2026-11-01T18:41:02|Unknown|Unknown|00:00:00||160G||None assigned
```

## tail plan_display_2443461_0.out

```
missing (or name refused): plan_display_2443461_0.out
```

## tail plan_display_2443461_1.out

```
missing (or name refused): plan_display_2443461_1.out
```

## tail plan_display_2443460_0.out

```
missing (or name refused): plan_display_2443460_0.out
```

## tail $LF_WORK/d3all_v1/work_d3all_aug2026/w9_log.txt

```
missing (or name refused): d3all_v1/work_d3all_aug2026/w9_log.txt
```

## tail $LF_WORK/d3all_v1/work_d3all_sep2021/w9_log.txt

```
missing (or name refused): d3all_v1/work_d3all_sep2021/w9_log.txt
```
