# Turing diagnostics: d3all_diag1

2026-11-01T14:09:21Z on compute-2-01.int.turing.wpi.edu, job 2442909, repo 02fd3739

## disk and quota

```
$ df -h /home/mgeldokla /home/mgeldokla/scratch /home/mgeldokla/scratch/lisflood
Filesystem                                                                                                                                                        Size  Used Avail Use% Mounted on
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/home/1c0b431a-0173-438f-85b5-1dfe3ac805cc     1.8P  1.2P  657T  64% /home
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  657T  64% /scratch
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  657T  64% /scratch
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
6.7G	/home/mgeldokla/scratch/lisflood/amcnwm_v1
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
41G	/home/mgeldokla/scratch/lisflood/inlets_v1
$ du -sh /home/mgeldokla/scratch/lisflood
434G	/home/mgeldokla/scratch/lisflood
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
short* up 1-00:00:00 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
short* up 1-00:00:00 30 (null) 64+ 512000+
short* up 1-00:00:00 1 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 96 1024000
long up 7-00:00:00 4 gpu:A100:4,gpumem:no_consume:80G 64 512000
long up 7-00:00:00 12 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 96 512000
long up 7-00:00:00 20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 96 512000
long up 7-00:00:00 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
long up 7-00:00:00 30 (null) 64+ 512000+
long up 7-00:00:00 1 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 96 1024000
quick up 12:00:00 4 gpu:A100:4,gpumem:no_consume:80G 64 512000
quick up 12:00:00 1 gpu:H200:8(S:0-1),gpumem:no_consume:141G 128 1536000
quick up 12:00:00 12 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 96 512000
quick up 12:00:00 2 gpu:H100:4(S:0-1),gpumem:no_consume:80G 128 512000
quick up 12:00:00 20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 96 512000
quick up 12:00:00 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
quick up 12:00:00 30 (null) 64+ 512000+
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
scavenger up infinite 1 gpu:A100:2(S:0-1),gpumem:no_consume:40G 112 512000
scavenger up infinite 31 (null) 64+ 512000+
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

$ squeue -u mgeldokla -o %i %j %P %T %M %l %R
JOBID NAME PARTITION STATE TIME TIME_LIMIT NODELIST(REASON)
2442908 q_pack_d3_sep2023_20m_b long PENDING 0:00 10:00:00 (Dependency)
2442906_[0] q_fcd3_e2etest_d3_2023091112 quick PENDING 0:00 6:00:00 (Nodes required for job are DOWN, DRAINED, REBOOTING or reserved for jobs in higher priority partitions)
2442907 q_run_d3_sep2023_20m_b quick PENDING 0:00 8:00:00 (Priority)
2442905 flood_queue short PENDING 0:00 20:00 (BeginTime)
2442909 q_d3all_diag1 short RUNNING 0:07 30:00 compute-2-01
array tasks expanded: 5, job records: 5
```

## sacct 2442643,2442677,2439816,2439311,2439813,2439505

```
$ sacct -P -j 2442643,2442677,2439816,2439311,2439813,2439505 --format=JobID,JobName%30,Partition,State,ExitCode,Submit,Start,End,Elapsed,MaxRSS,ReqMem,AllocTRES%60,NodeList
JobID|JobName|Partition|State|ExitCode|Submit|Start|End|Elapsed|MaxRSS|ReqMem|AllocTRES|NodeList
2439311|q_vel_run_v1|quick|COMPLETED|0:0|2026-10-31T13:53:49|2026-10-31T14:01:42|2026-10-31T14:19:59|00:18:17||96G|billing=8,cpu=8,gres/gpu=1,mem=96G,node=1|gpu-5-22
2439311.batch|batch||COMPLETED|0:0|2026-10-31T14:01:42|2026-10-31T14:01:42|2026-10-31T14:19:59|00:18:17|24766820K||cpu=8,gres/gpu=1,mem=96G,node=1|gpu-5-22
2439505|q_run_sep2022_webster|quick|COMPLETED|0:0|2026-10-31T15:24:48|2026-10-31T17:57:36|2026-10-31T18:08:49|00:11:13||96G|billing=8,cpu=8,gres/gpu=1,mem=96G,node=1|gpu-5-28
2439505.batch|batch||COMPLETED|0:0|2026-10-31T17:57:36|2026-10-31T17:57:36|2026-10-31T18:08:49|00:11:13|15406252K||cpu=8,gres/gpu=1,mem=96G,node=1|gpu-5-28
2439816|q_amcnwm_v1_collect|long|CANCELLED by 901022506|0:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-11-01T14:08:56|21:12:35||2G|billing=1,cpu=1,mem=2G,node=1|compute-2-01
2439816.batch|batch||CANCELLED|0:15|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-11-01T14:08:57|21:12:36|803080K||cpu=1,mem=2G,node=1|compute-2-01
2439813_0|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:25:17|00:28:56||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-02
2439813_0.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:25:17|00:28:56|4628996K||cpu=16,mem=64G,node=1|compute-4-02
2439813_1|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T18:44:48|01:48:27||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-01
2439813_1.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T18:44:48|01:48:27|7123008K||cpu=16,mem=64G,node=1|compute-4-01
2439813_2|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:31:40|00:35:19||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_2.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:31:40|00:35:19|4513048K||cpu=16,mem=64G,node=1|compute-4-03
2439813_3|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:29:40|00:33:19||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_3.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:29:40|00:33:19|4345424K||cpu=16,mem=64G,node=1|compute-4-03
2439813_4|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:05:54|00:09:33||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_4.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:05:54|00:09:33|2879516K||cpu=16,mem=64G,node=1|compute-4-08
2439813_5|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:14:13|00:17:52||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_5.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:14:13|00:17:52|2501920K||cpu=16,mem=64G,node=1|compute-4-07
2439813_6|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:09:06|00:12:45||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_6.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:09:06|00:12:45|2478988K||cpu=16,mem=64G,node=1|compute-4-07
2439813_7|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:12:40|00:16:19||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_7.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:12:40|00:16:19|2842780K||cpu=16,mem=64G,node=1|compute-4-07
2439813_8|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:09:32|00:13:11||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_8.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:09:32|00:13:11|2458300K||cpu=16,mem=64G,node=1|compute-4-07
2439813_9|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T16:56:21|2026-10-31T17:12:57|00:16:36||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_9.batch|batch||FAILED|1:0|2026-10-31T16:56:21|2026-10-31T16:56:21|2026-10-31T17:12:57|00:16:36|2529860K||cpu=16,mem=64G,node=1|compute-4-07
2439813_10|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:05:59|2026-10-31T17:14:10|00:08:11||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_10.batch|batch||FAILED|1:0|2026-10-31T17:05:59|2026-10-31T17:05:59|2026-10-31T17:14:10|00:08:11|2519664K||cpu=16,mem=64G,node=1|compute-4-08
2439813_11|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:09:32|2026-10-31T17:25:53|00:16:21||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_11.batch|batch||FAILED|1:0|2026-10-31T17:09:32|2026-10-31T17:09:32|2026-10-31T17:25:53|00:16:21|2501956K||cpu=16,mem=64G,node=1|compute-4-07
2439813_12|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:10:03|2026-10-31T17:21:32|00:11:29||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_12.batch|batch||FAILED|1:0|2026-10-31T17:10:03|2026-10-31T17:10:03|2026-10-31T17:21:32|00:11:29|2477960K||cpu=16,mem=64G,node=1|compute-4-07
2439813_13|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:13:05|2026-10-31T17:29:00|00:15:55||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_13.batch|batch||FAILED|1:0|2026-10-31T17:13:05|2026-10-31T17:13:05|2026-10-31T17:29:00|00:15:55|2474796K||cpu=16,mem=64G,node=1|compute-4-07
2439813_14|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:13:05|2026-10-31T17:30:35|00:17:30||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_14.batch|batch||FAILED|1:0|2026-10-31T17:13:05|2026-10-31T17:13:05|2026-10-31T17:30:35|00:17:30|3037984K||cpu=16,mem=64G,node=1|compute-4-07
2439813_15|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:14:36|2026-10-31T17:37:47|00:23:11||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_15.batch|batch||FAILED|1:0|2026-10-31T17:14:36|2026-10-31T17:14:36|2026-10-31T17:37:47|00:23:11|3049676K||cpu=16,mem=64G,node=1|compute-4-07
2439813_16|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:14:36|2026-10-31T17:22:20|00:07:44||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_16.batch|batch||FAILED|1:0|2026-10-31T17:14:36|2026-10-31T17:14:36|2026-10-31T17:22:20|00:07:44|2461016K||cpu=16,mem=64G,node=1|compute-4-08
2439813_17|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:21:42|2026-10-31T17:37:44|00:16:02||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_17.batch|batch||FAILED|1:0|2026-10-31T17:21:42|2026-10-31T17:21:42|2026-10-31T17:37:44|00:16:02|2477748K||cpu=16,mem=64G,node=1|compute-4-07
2439813_18|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:22:43|2026-10-31T17:30:21|00:07:38||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_18.batch|batch||FAILED|1:0|2026-10-31T17:22:43|2026-10-31T17:22:43|2026-10-31T17:30:21|00:07:38|2485380K||cpu=16,mem=64G,node=1|compute-4-08
2439813_19|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:25:45|2026-10-31T17:40:01|00:14:16||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-02
2439813_19.batch|batch||FAILED|1:0|2026-10-31T17:25:45|2026-10-31T17:25:45|2026-10-31T17:40:01|00:14:16|2501212K||cpu=16,mem=64G,node=1|compute-4-02
2439813_20|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:26:15|2026-10-31T17:40:54|00:14:39||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_20.batch|batch||FAILED|1:0|2026-10-31T17:26:15|2026-10-31T17:26:15|2026-10-31T17:40:54|00:14:39|2834588K||cpu=16,mem=64G,node=1|compute-4-07
2439813_21|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:29:17|2026-10-31T17:48:59|00:19:42||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_21.batch|batch||FAILED|1:0|2026-10-31T17:29:17|2026-10-31T17:29:17|2026-10-31T17:48:59|00:19:42|2847440K||cpu=16,mem=64G,node=1|compute-4-07
2439813_22|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:29:48|2026-10-31T17:40:46|00:10:58||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_22.batch|batch||FAILED|1:0|2026-10-31T17:29:48|2026-10-31T17:29:48|2026-10-31T17:40:46|00:10:58|2475172K||cpu=16,mem=64G,node=1|compute-4-03
2439813_23|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:30:48|2026-10-31T17:46:37|00:15:49||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_23.batch|batch||FAILED|1:0|2026-10-31T17:30:48|2026-10-31T17:30:48|2026-10-31T17:46:37|00:15:49|2472888K||cpu=16,mem=64G,node=1|compute-4-07
2439813_24|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:30:48|2026-10-31T17:38:39|00:07:51||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_24.batch|batch||FAILED|1:0|2026-10-31T17:30:48|2026-10-31T17:30:48|2026-10-31T17:38:39|00:07:51|2450852K||cpu=16,mem=64G,node=1|compute-4-08
2439813_25|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:31:49|2026-10-31T17:48:54|00:17:05||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_25.batch|batch||FAILED|1:0|2026-10-31T17:31:49|2026-10-31T17:31:49|2026-10-31T17:48:54|00:17:05|2495268K||cpu=16,mem=64G,node=1|compute-4-03
2439813_26|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:37:53|2026-10-31T17:51:30|00:13:37||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_26.batch|batch||FAILED|1:0|2026-10-31T17:37:53|2026-10-31T17:37:53|2026-10-31T17:51:30|00:13:37|2437892K||cpu=16,mem=64G,node=1|compute-4-07
2439813_27|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:37:53|2026-10-31T17:55:06|00:17:13||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_27.batch|batch||FAILED|1:0|2026-10-31T17:37:53|2026-10-31T17:37:53|2026-10-31T17:55:06|00:17:13|2451260K||cpu=16,mem=64G,node=1|compute-4-07
2439813_28|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:38:54|2026-10-31T17:45:34|00:06:40||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_28.batch|batch||FAILED|1:0|2026-10-31T17:38:54|2026-10-31T17:38:54|2026-10-31T17:45:34|00:06:40|2500420K||cpu=16,mem=64G,node=1|compute-4-08
2439813_29|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:40:25|2026-10-31T17:58:50|00:18:25||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-02
2439813_29.batch|batch||FAILED|1:0|2026-10-31T17:40:25|2026-10-31T17:40:25|2026-10-31T17:58:50|00:18:25|2498184K||cpu=16,mem=64G,node=1|compute-4-02
2439813_30|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:40:56|2026-10-31T17:51:20|00:10:24||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_30.batch|batch||FAILED|1:0|2026-10-31T17:40:56|2026-10-31T17:40:56|2026-10-31T17:51:20|00:10:24|2503372K||cpu=16,mem=64G,node=1|compute-4-03
2439813_31|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:40:56|2026-10-31T17:56:53|00:15:57||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_31.batch|batch||FAILED|1:0|2026-10-31T17:40:56|2026-10-31T17:40:56|2026-10-31T17:56:53|00:15:57|2525916K||cpu=16,mem=64G,node=1|compute-4-07
2439813_32|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:45:59|2026-10-31T17:53:43|00:07:44||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_32.batch|batch||FAILED|1:0|2026-10-31T17:45:59|2026-10-31T17:45:59|2026-10-31T17:53:43|00:07:44|2450800K||cpu=16,mem=64G,node=1|compute-4-08
2439813_33|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:47:00|2026-10-31T18:01:03|00:14:03||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_33.batch|batch||FAILED|1:0|2026-10-31T17:47:00|2026-10-31T17:47:00|2026-10-31T18:01:03|00:14:03|2463508K||cpu=16,mem=64G,node=1|compute-4-07
2439813_34|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:49:01|2026-10-31T18:00:01|00:11:00||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_34.batch|batch||FAILED|1:0|2026-10-31T17:49:01|2026-10-31T17:49:01|2026-10-31T18:00:01|00:11:00|2497960K||cpu=16,mem=64G,node=1|compute-4-03
2439813_35|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:49:01|2026-10-31T18:02:29|00:13:28||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_35.batch|batch||FAILED|1:0|2026-10-31T17:49:01|2026-10-31T17:49:01|2026-10-31T18:02:29|00:13:28|2462980K||cpu=16,mem=64G,node=1|compute-4-07
2439813_36|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:51:32|2026-10-31T18:04:02|00:12:30||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_36.batch|batch||FAILED|1:0|2026-10-31T17:51:32|2026-10-31T17:51:32|2026-10-31T18:04:02|00:12:30|2524564K||cpu=16,mem=64G,node=1|compute-4-03
2439813_37|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:51:32|2026-10-31T18:05:36|00:14:04||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-07
2439813_37.batch|batch||FAILED|1:0|2026-10-31T17:51:32|2026-10-31T17:51:32|2026-10-31T18:05:36|00:14:04|2482572K||cpu=16,mem=64G,node=1|compute-4-07
2439813_38|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:54:04|2026-10-31T18:04:11|00:10:07||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-01
2439813_38.batch|batch||FAILED|1:0|2026-10-31T17:54:04|2026-10-31T17:54:04|2026-10-31T18:04:11|00:10:07|2589508K||cpu=16,mem=64G,node=1|compute-4-01
2439813_39|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:55:35|2026-10-31T18:06:27|00:10:52||64G|billing=16,cpu=16,mem=64G,node=1|compute-3-08
2439813_39.batch|batch||FAILED|1:0|2026-10-31T17:55:35|2026-10-31T17:55:35|2026-10-31T18:06:27|00:10:52|2909284K||cpu=16,mem=64G,node=1|compute-3-08
2439813_40|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:57:06|2026-10-31T18:04:45|00:07:39||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_40.batch|batch||FAILED|1:0|2026-10-31T17:57:06|2026-10-31T17:57:06|2026-10-31T18:04:45|00:07:39|2512540K||cpu=16,mem=64G,node=1|compute-4-08
2439813_41|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T17:59:07|2026-10-31T18:19:07|00:20:00||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-02
2439813_41.batch|batch||FAILED|1:0|2026-10-31T17:59:07|2026-10-31T17:59:07|2026-10-31T18:19:07|00:20:00|2559648K||cpu=16,mem=64G,node=1|compute-4-02
2439813_42|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:00:08|2026-10-31T18:18:20|00:18:12||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_42.batch|batch||FAILED|1:0|2026-10-31T18:00:08|2026-10-31T18:00:08|2026-10-31T18:18:20|00:18:12|3039716K||cpu=16,mem=64G,node=1|compute-4-03
2439813_43|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:01:09|2026-10-31T18:24:38|00:23:29||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-06
2439813_43.batch|batch||FAILED|1:0|2026-10-31T18:01:09|2026-10-31T18:01:09|2026-10-31T18:24:38|00:23:29|3465332K||cpu=16,mem=64G,node=1|compute-4-06
2439813_44|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:02:40|2026-10-31T18:14:14|00:11:34||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-06
2439813_44.batch|batch||FAILED|1:0|2026-10-31T18:02:40|2026-10-31T18:02:40|2026-10-31T18:14:14|00:11:34|2491948K||cpu=16,mem=64G,node=1|compute-4-06
2439813_45|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:04:11|2026-10-31T18:22:57|00:18:46||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-03
2439813_45.batch|batch||FAILED|1:0|2026-10-31T18:04:11|2026-10-31T18:04:11|2026-10-31T18:22:57|00:18:46|2471096K||cpu=16,mem=64G,node=1|compute-4-03
2439813_46|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:04:42|2026-10-31T18:16:33|00:11:51||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-01
2439813_46.batch|batch||FAILED|1:0|2026-10-31T18:04:42|2026-10-31T18:04:42|2026-10-31T18:16:33|00:11:51|2438872K||cpu=16,mem=64G,node=1|compute-4-01
2439813_47|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:05:12|2026-10-31T18:15:01|00:09:49||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-08
2439813_47.batch|batch||FAILED|1:0|2026-10-31T18:05:12|2026-10-31T18:05:12|2026-10-31T18:15:01|00:09:49|2471532K||cpu=16,mem=64G,node=1|compute-4-08
2439813_48|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:05:43|2026-10-31T18:15:58|00:10:15||64G|billing=16,cpu=16,mem=64G,node=1|compute-4-06
2439813_48.batch|batch||FAILED|1:0|2026-10-31T18:05:43|2026-10-31T18:05:43|2026-10-31T18:15:58|00:10:15|2493032K||cpu=16,mem=64G,node=1|compute-4-06
2439813_49|q_inl1_runs|long|FAILED|1:0|2026-10-31T16:55:56|2026-10-31T18:06:43|2026-10-31T18:19:44|00:13:01||64G|billing=16,cpu=16,mem=64G,node=1|compute-3-08
2439813_49.batch|batch||FAILED|1:0|2026-10-31T18:06:43|2026-10-31T18:06:43|2026-10-31T18:19:44|00:13:01|2457324K||cpu=16,mem=64G,node=1|compute-3-08
2442643|q_run_d3_sep2023_20m|quick|CANCELLED by 901022506|0:0|2026-11-01T12:38:16|None|2026-11-01T14:08:56|00:00:00||96G||None assigned
2442677|q_pack_d3_sep2023_20m|long|CANCELLED by 901022506|0:0|2026-11-01T13:08:26|None|2026-11-01T14:08:56|00:00:00||64G||None assigned
```

## work folder run_sep2023_proto_site_d3_sep2023

```
not a folder (or name refused): run_sep2023_proto_site_d3_sep2023
```

## work folder run_sep2023_proto_d3_sep2023_p

```
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_p
27G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_p
$ ls -la /home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_p/out
total 659228
drwxrwxr-x 2 mgeldokla mgeldokla        16 Oct 24 00:06 .
drwxrwxr-x 4 mgeldokla mgeldokla         9 Oct 24 00:05 ..
-rw-rw-r-- 1 mgeldokla mgeldokla  92626349 Oct 24 00:05 frames_cm.npz
-rw-rw-r-- 1 mgeldokla mgeldokla  70200128 Oct 24 00:05 hmax.npy
-rw-rw-r-- 1 mgeldokla mgeldokla  70200128 Oct 24 00:05 hsnap.npy
-rw-rw-r-- 1 mgeldokla mgeldokla     84971 Oct 24 00:06 lisflood.mass
-rw-rw-r-- 1 mgeldokla mgeldokla   4731899 Oct 24 00:06 lisflood_stdout.txt
-rw-rw-r-- 1 mgeldokla mgeldokla     10795 Oct 24 00:06 meta.json
-rw-rw-r-- 1 mgeldokla mgeldokla 183725496 Oct 24 00:06 rainstats.npz
-rw-rw-r-- 1 mgeldokla mgeldokla       100 Oct 24 00:06 run.bci
-rw-rw-r-- 1 mgeldokla mgeldokla       223 Oct 24 00:06 run.par
-rw-rw-r-- 1 mgeldokla mgeldokla   1297538 Oct 24 00:06 timing.npz
-rw-rw-r-- 1 mgeldokla mgeldokla  43507304 Oct 24 00:06 vel_max.npz
-rw-rw-r-- 1 mgeldokla mgeldokla    197397 Oct 24 00:06 w9_log.txt
-rw-rw-r-- 1 mgeldokla mgeldokla  17550128 Oct 24 00:05 watermask.npy
-rw-rw-r-- 1 mgeldokla mgeldokla   2046341 Oct 24 00:06 xings.json
-rw-rw-r-- 1 mgeldokla mgeldokla  70200128 Oct 24 00:05 z.npy
-rw-rw-r-- 1 mgeldokla mgeldokla 118666599 Oct 24 00:06 z_raw.npz
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_p/results
23G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_p/results
wd: 97 files, last res-0096.wd 105304633 bytes
elev: 97 files, last res-0096.elev 137225849 bytes
Vx: 0 files, last none  bytes
Vy: 0 files, last none  bytes
Qx: 0 files, last none  bytes
Qy: 0 files, last none  bytes
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Oct 23 23:41 res-0092.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225788 Oct 23 23:41 res-0093.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Oct 23 23:41 res-0093.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225788 Oct 23 23:41 res-0094.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Oct 23 23:41 res-0094.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225809 Oct 23 23:42 res-0095.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Oct 23 23:42 res-0095.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225849 Oct 23 23:42 res-0096.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Oct 23 23:42 res-0096.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 152054592 Oct 23 23:42 res.inittm
-rw-rw-r-- 1 mgeldokla mgeldokla     84971 Oct 23 23:42 res.mass
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Oct 23 23:42 res.max
```

## work folder run_sep2023_proto_d3_sep2023_20m

```
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_20m
27G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_20m
$ ls -la /home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_20m/out
total 646006
drwxrwxr-x 2 mgeldokla mgeldokla        15 Oct 22 22:39 .
drwxrwxr-x 4 mgeldokla mgeldokla         9 Oct 22 22:38 ..
-rw-rw-r-- 1 mgeldokla mgeldokla 121986996 Oct 22 22:38 frames_cm.npz
-rw-rw-r-- 1 mgeldokla mgeldokla  70200128 Oct 22 22:38 hmax.npy
-rw-rw-r-- 1 mgeldokla mgeldokla  70200128 Oct 22 22:38 hsnap.npy
-rw-rw-r-- 1 mgeldokla mgeldokla     84971 Oct 22 22:39 lisflood.mass
-rw-rw-r-- 1 mgeldokla mgeldokla   4647566 Oct 22 22:39 lisflood_stdout.txt
-rw-rw-r-- 1 mgeldokla mgeldokla      7785 Oct 22 22:39 meta.json
-rw-rw-r-- 1 mgeldokla mgeldokla 183725496 Oct 22 22:39 rainstats.npz
-rw-rw-r-- 1 mgeldokla mgeldokla       100 Oct 22 22:39 run.bci
-rw-rw-r-- 1 mgeldokla mgeldokla       240 Oct 22 22:39 run.par
-rw-rw-r-- 1 mgeldokla mgeldokla   2167020 Oct 22 22:39 timing.npz
-rw-rw-r-- 1 mgeldokla mgeldokla     22719 Oct 22 22:39 w9_log.txt
-rw-rw-r-- 1 mgeldokla mgeldokla  17550128 Oct 22 22:38 watermask.npy
-rw-rw-r-- 1 mgeldokla mgeldokla   2046869 Oct 22 22:39 xings.json
-rw-rw-r-- 1 mgeldokla mgeldokla  70200128 Oct 22 22:38 z.npy
-rw-rw-r-- 1 mgeldokla mgeldokla 118666599 Oct 22 22:39 z_raw.npz
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_20m/results
23G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_20m/results
wd: 97 files, last res-0096.wd 105304642 bytes
elev: 97 files, last res-0096.elev 137225939 bytes
Vx: 0 files, last none  bytes
Vy: 0 files, last none  bytes
Qx: 0 files, last none  bytes
Qy: 0 files, last none  bytes
-rw-rw-r-- 1 mgeldokla mgeldokla 105304642 Oct 22 22:25 res-0092.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225816 Oct 22 22:25 res-0093.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304642 Oct 22 22:25 res-0093.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225817 Oct 22 22:25 res-0094.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304642 Oct 22 22:25 res-0094.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225867 Oct 22 22:25 res-0095.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304642 Oct 22 22:25 res-0095.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225939 Oct 22 22:26 res-0096.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304642 Oct 22 22:26 res-0096.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137861621 Oct 22 22:26 res.inittm
-rw-rw-r-- 1 mgeldokla mgeldokla     84971 Oct 22 22:26 res.mass
-rw-rw-r-- 1 mgeldokla mgeldokla 105305048 Oct 22 22:26 res.max
```

## work folder run_sep2023_proto_leominster_vel

```
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_vel
8.5G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_vel
$ ls -la /home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_vel/out
total 792906
drwxrwxr-x 2 mgeldokla mgeldokla        17 Oct 31 14:16 .
drwxrwxr-x 4 mgeldokla mgeldokla         9 Oct 31 14:15 ..
-rw-rw-r-- 1 mgeldokla mgeldokla  49740550 Oct 31 14:16 frames_cm.npz
-rw-rw-r-- 1 mgeldokla mgeldokla   4000128 Oct 31 14:16 hmax.npy
-rw-rw-r-- 1 mgeldokla mgeldokla   4000128 Oct 31 14:16 hsnap.npy
-rw-rw-r-- 1 mgeldokla mgeldokla     84971 Oct 31 14:16 lisflood.mass
-rw-rw-r-- 1 mgeldokla mgeldokla   4748867 Oct 31 14:16 lisflood_stdout.txt
-rw-rw-r-- 1 mgeldokla mgeldokla     10741 Oct 31 14:16 meta.json
-rw-rw-r-- 1 mgeldokla mgeldokla  10236631 Oct 31 14:16 rainstats.npz
-rw-rw-r-- 1 mgeldokla mgeldokla       100 Oct 31 14:16 run.bci
-rw-rw-r-- 1 mgeldokla mgeldokla       222 Oct 31 14:16 run.par
-rw-rw-r-- 1 mgeldokla mgeldokla    308130 Oct 31 14:16 timing.npz
-rw-rw-r-- 1 mgeldokla mgeldokla 720581487 Oct 31 14:16 vel_frames.npz
-rw-rw-r-- 1 mgeldokla mgeldokla   5797776 Oct 31 14:16 vel_max.npz
-rw-rw-r-- 1 mgeldokla mgeldokla    411398 Oct 31 14:16 w9_log.txt
-rw-rw-r-- 1 mgeldokla mgeldokla   1000128 Oct 31 14:16 watermask.npy
-rw-rw-r-- 1 mgeldokla mgeldokla    141170 Oct 31 14:16 xings.json
-rw-rw-r-- 1 mgeldokla mgeldokla   4000128 Oct 31 14:16 z.npy
-rw-rw-r-- 1 mgeldokla mgeldokla   6869293 Oct 31 14:16 z_raw.npz
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_vel/results
7.5G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_vel/results
wd: 577 files, last res-0576.wd 6001133 bytes
elev: 577 files, last res-0576.elev 7871208 bytes
Vx: 0 files, last none  bytes
Vy: 0 files, last none  bytes
Qx: 0 files, last none  bytes
Qy: 0 files, last none  bytes
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 14:06 res-0092.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7871437 Oct 31 14:06 res-0093.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 14:06 res-0093.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7871438 Oct 31 14:06 res-0094.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 14:06 res-0094.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7871439 Oct 31 14:06 res-0095.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 14:06 res-0095.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7871444 Oct 31 14:06 res-0096.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 14:06 res-0096.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7871446 Oct 31 14:06 res-0097.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 14:06 res-0097.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7871447 Oct 31 14:06 res-0098.elev
```

## work folder run_sep2022_proto_site_sep2022_webster

```
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster
5.3G	/home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster
$ ls -la /home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster/out
total 377488
drwxrwxr-x 2 mgeldokla mgeldokla        17 Oct 31 18:07 .
drwxrwxr-x 4 mgeldokla mgeldokla         9 Oct 31 18:06 ..
-rw-rw-r-- 1 mgeldokla mgeldokla  31453718 Oct 31 18:07 frames_cm.npz
-rw-rw-r-- 1 mgeldokla mgeldokla   4000128 Oct 31 18:07 hmax.npy
-rw-rw-r-- 1 mgeldokla mgeldokla   4000128 Oct 31 18:07 hsnap.npy
-rw-rw-r-- 1 mgeldokla mgeldokla     53219 Oct 31 18:07 lisflood.mass
-rw-rw-r-- 1 mgeldokla mgeldokla   2926690 Oct 31 18:07 lisflood_stdout.txt
-rw-rw-r-- 1 mgeldokla mgeldokla      7586 Oct 31 18:07 meta.json
-rw-rw-r-- 1 mgeldokla mgeldokla  10199549 Oct 31 18:07 rainstats.npz
-rw-rw-r-- 1 mgeldokla mgeldokla       100 Oct 31 18:07 run.bci
-rw-rw-r-- 1 mgeldokla mgeldokla       222 Oct 31 18:07 run.par
-rw-rw-r-- 1 mgeldokla mgeldokla    123845 Oct 31 18:07 timing.npz
-rw-rw-r-- 1 mgeldokla mgeldokla 316903885 Oct 31 18:07 vel_frames.npz
-rw-rw-r-- 1 mgeldokla mgeldokla   4611096 Oct 31 18:07 vel_max.npz
-rw-rw-r-- 1 mgeldokla mgeldokla    448588 Oct 31 18:07 w9_log.txt
-rw-rw-r-- 1 mgeldokla mgeldokla   1000128 Oct 31 18:07 watermask.npy
-rw-rw-r-- 1 mgeldokla mgeldokla    122345 Oct 31 18:07 xings.json
-rw-rw-r-- 1 mgeldokla mgeldokla   4000128 Oct 31 18:07 z.npy
-rw-rw-r-- 1 mgeldokla mgeldokla   6691862 Oct 31 18:07 z_raw.npz
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster/results
4.8G	/home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster/results
wd: 361 files, last res-0360.wd 6001133 bytes
elev: 361 files, last res-0360.elev 7977031 bytes
Vx: 0 files, last none  bytes
Vy: 0 files, last none  bytes
Qx: 0 files, last none  bytes
Qy: 0 files, last none  bytes
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 18:00 res-0092.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7977020 Oct 31 18:00 res-0093.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 18:00 res-0093.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7977020 Oct 31 18:00 res-0094.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 18:00 res-0094.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7977021 Oct 31 18:00 res-0095.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 18:00 res-0095.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7977021 Oct 31 18:00 res-0096.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 18:00 res-0096.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7977022 Oct 31 18:00 res-0097.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 6001133 Oct 31 18:00 res-0097.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 7977024 Oct 31 18:00 res-0098.elev
```

## tail roadflood_2442643.out

```
missing (or name refused): roadflood_2442643.out
```
