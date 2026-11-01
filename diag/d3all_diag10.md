# Turing diagnostics: d3all_diag10

2026-11-01T23:14:06Z on compute-2-01.int.turing.wpi.edu, job 2444162, repo 6b352f11

## disk and quota

```
$ df -h /home/mgeldokla /home/mgeldokla/scratch /home/mgeldokla/scratch/lisflood
Filesystem                                                                                                                                                        Size  Used Avail Use% Mounted on
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/home/1c0b431a-0173-438f-85b5-1dfe3ac805cc     1.8P  1.2P  666T  64% /home
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  666T  64% /scratch
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  666T  64% /scratch
$ readlink -f /home/mgeldokla/scratch
/scratch/mgeldokla
$ quota -s
timeout: failed to run command 'quota': Permission denied
$ bash -c du -sh /home/mgeldokla/scratch/lisflood/* 2>/dev/null | sort -h | tail -n 50
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
4.2G	/home/mgeldokla/scratch/lisflood/run_forecast_fcd3_e2etest2_d3_2023091112_m0
5.0G	/home/mgeldokla/scratch/lisflood/run_sep2018m_proto_site_sep2018m_milford
5.1G	/home/mgeldokla/scratch/lisflood/run_aug2023_proto_site_aug2023_metrowest
5.1G	/home/mgeldokla/scratch/lisflood/run_aug2023_proto_site_aug2023_metrowest_t2
5.1G	/home/mgeldokla/scratch/lisflood/run_jul2023_proto_site_jul2023_worcester
5.1G	/home/mgeldokla/scratch/lisflood/run_jul2023_proto_site_jul2023_worcester_t2
5.1G	/home/mgeldokla/scratch/lisflood/run_jun2020_proto_site_jun2020_northbridge
5.1G	/home/mgeldokla/scratch/lisflood/run_jun2020_proto_site_jun2020_northbridge_t2
5.2G	/home/mgeldokla/scratch/lisflood/run_sep2021_proto_d3all_sep2021
5.3G	/home/mgeldokla/scratch/lisflood/run_aug2026_proto_site_aug2026_leominster_t2
5.3G	/home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster
5.3G	/home/mgeldokla/scratch/lisflood/run_sep2022_proto_site_sep2022_webster_t2
5.4G	/home/mgeldokla/scratch/lisflood/run_aug2026_proto_site_aug2026_leominster
5.4G	/home/mgeldokla/scratch/lisflood/run_sep2018_proto_site_sep2018_fitchburg
5.9G	/home/mgeldokla/scratch/lisflood/run_sep2018_proto_site_sep2018_fitchburg_t2
6.1G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_sep2023_10m
6.4G	/home/mgeldokla/scratch/lisflood/run_sep2018m_proto_site_sep2018m_milford_t2
6.5G	/home/mgeldokla/scratch/lisflood/run_sep2021_proto_site_sep2021_worcester
6.5G	/home/mgeldokla/scratch/lisflood/run_sep2021_proto_site_sep2021_worcester_t2
7.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_sep2023_5min
7.8G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_sep2023_p
7.9G	/home/mgeldokla/scratch/lisflood/run_aug2021_proto_worcester_aug2021_5min
7.9G	/home/mgeldokla/scratch/lisflood/run_aug2021_proto_worcester_aug2021_p
7.9G	/home/mgeldokla/scratch/lisflood/run_aug2021_proto_worcester_aug2021_t2
8.5G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_sep2023_t2
8.5G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_leominster_vel
27G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_20m
27G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_d3_sep2023_p
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_18z_nb10p90
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_18z_nb20p75
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_18z_raw
30G	/home/mgeldokla/scratch/lisflood/run_forecast_hindcast_d3_sep2023_18z
34G	/home/mgeldokla/scratch/lisflood/amcnwm_v1
41G	/home/mgeldokla/scratch/lisflood/inlets_v1
73G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any
184G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_t2
191G	/home/mgeldokla/scratch/lisflood/d3all_v1
$ du -sh /home/mgeldokla/scratch/lisflood
1.0T	/home/mgeldokla/scratch/lisflood
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
academic up 2-00:00:00 8 (null) 192 1536000
academic up 2-00:00:00 8 gpu:A30:4(S:0-1),gpumem:no_consume:24G 96 244140
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
2443972 q_pack_d3_sep2023_20m_t2b long PENDING 0:00 10:00:00 (Dependency) N/A
2444002 q_pack_t2b_sep2018m_milford long PENDING 0:00 3:00:00 (Dependency) N/A
2443999 q_pack_t2b_sep2018_fitchburg long PENDING 0:00 3:00:00 (Dependency) N/A
2443996 q_pack_t2b_jul2023_worcester long RUNNING 0:28 3:00:00 compute-2-03 N/A
2443993 q_pack_t2b_jun2020_northbridge long RUNNING 2:00 3:00:00 compute-2-01 N/A
2443209_[0] q_fcd3_e2etest_d3_2023091112_g short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443971 q_run_d3_sep2023_20m_t2b_p short PENDING 0:00 12:00:00 (Priority) gres/gpu:1
2444007_[2-11%2] q_d3all_v2_b_s short PENDING 0:00 4:00:00 (JobArrayTaskLimit) gres/gpu:1
2444005_[2-3%2] q_d3all_v1_c2_s short PENDING 0:00 4:00:00 (JobArrayTaskLimit) gres/gpu:1
2444003_[2-5%2] q_d3all_v1_b5_s short PENDING 0:00 4:00:00 (JobArrayTaskLimit) gres/gpu:1
2444008_[0-5%3] q_d3all_v2_b_p short PENDING 0:00 12:00:00 (Dependency) N/A
2444006_[0-1%3] q_d3all_v1_c2_p short PENDING 0:00 12:00:00 (Dependency) N/A
2444004_[0-2%3] q_d3all_v1_b5_p short PENDING 0:00 12:00:00 (Dependency) N/A
2444161 flood_queue short PENDING 0:00 20:00 (BeginTime) N/A
2444007_1 q_d3all_v2_b_s short RUNNING 0:59 4:00:00 gpu-5-23 gres/gpu:1
2444007_0 q_d3all_v2_b_s short RUNNING 2:00 4:00:00 gpu-5-23 gres/gpu:1
2444005_1 q_d3all_v1_c2_s short RUNNING 2:00 4:00:00 gpu-5-21 gres/gpu:1
2444001 q_run_t2b_sep2018m_milford_p short RUNNING 6:35 4:00:00 gpu-5-23 gres/gpu:1
2443998 q_run_t2b_sep2018_fitchburg_p short RUNNING 8:06 4:00:00 gpu-5-21 gres/gpu:1
2444005_0 q_d3all_v1_c2_s short RUNNING 8:06 4:00:00 gpu-5-23 gres/gpu:1
2444003_1 q_d3all_v1_b5_s short RUNNING 9:07 4:00:00 gpu-5-21 gres/gpu:1
2444003_0 q_d3all_v1_b5_s short RUNNING 9:38 4:00:00 gpu-5-21 gres/gpu:1
2444162 q_d3all_diag10 short RUNNING 4:32 30:00 compute-2-01 N/A
array tasks expanded: 44, job records: 23
```

## GPU queue position (short / quick)

```
$ sprio -u mgeldokla
          JOBID PARTITION     USER   PRIORITY       SITE        AGE  FAIRSHARE    JOBSIZE  PARTITION
        2443209 short     mgeldokl      81922          0       1822      79095          6       1000
        2443971 short     mgeldokl      80271          0        171      79095          6       1000
        2443972 long      mgeldokl      79371          0        171      79095          6        100
        2443999 long      mgeldokl      79370          0        171      79095          6        100
        2444002 long      mgeldokl      79370          0        171      79095          6        100
        2444003 short     mgeldokl      80270          0        171      79095          6       1000
        2444004 short     mgeldokl      80270          0        171      79095          6       1000
        2444005 short     mgeldokl      80270          0        171      79095          6       1000
        2444006 short     mgeldokl      80270          0        171      79095          6       1000
        2444007 short     mgeldokl      80270          0        171      79095          6       1000
        2444008 short     mgeldokl      80270          0        171      79095          6       1000
        2444161 short     mgeldokl      80120          0         20      79095          5       1000
      1 whitehill-0-02 A100 gpu:A100:2(S:0-1),gpumem:no_consume:40G mixed
      3 gpu-4-12 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G down*
      1 gpu-4-11 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G mixed@
      1 aswin-02 EPYC-7543 (null) mixed
      6 aswin-03 EPYC-7543 (null) reserved
      1 compute-2-06 EPYC-7543,AMD (null) allocated
      1 compute-2-04 EPYC-7543,AMD (null) drained
      6 compute-2-01 EPYC-7543,AMD (null) mixed
      1 compute-3-04 EPYC-9654,AMD (null) allocated
      6 compute-3-02 EPYC-9654,AMD (null) mixed
      1 compute-3-01 EPYC-9654,AMD (null) mixed-
      2 gpu-5-11 H100 gpu:H100:4(S:0-1),gpumem:no_consume:80G down*
      1 gpu-5-32 H200 gpu:H200:8(S:0-1),gpumem:no_consume:141G mixed@
      4 compute-4-01 Intel,6767P (null) allocated
      3 compute-4-02 Intel,6767P (null) mixed
      1 murai-01 L40S gpu:L40S:2(S:0-1),gpumem:no_consume:48G reserved
      9 gpu-5-22 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G down*
      2 gpu-5-21 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G mixed-
      1 gpu-5-28 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G mixed@
     18 gpu-6-01 RTX6000B,Intel gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G down*
      2 gpu-6-12 RTX6000B,Intel gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G mixed@
      1 $ sinfo -N -p short -o %N %f %G %T --noheader
$ squeue -p short -t PD --sort=-p -o %i %u %Q %b %r
JOBID USER PRIORITY TRES_PER_NODE REASON
2210407 zhuang5 155508 N/A DependencyNeverSatisfied
2210346 zhuang5 155508 N/A DependencyNeverSatisfied
2413510 ttjokro 122258 N/A DependencyNeverSatisfied
2415396 afrenk 105057 N/A Dependency
2413506 zcheng3 101077 N/A BeginTime
2413505 zcheng3 101077 N/A BeginTime
2413504 zcheng3 101077 N/A BeginTime
2413503 zcheng3 101077 N/A BeginTime
2413502 zcheng3 101077 N/A BeginTime
2413501 zcheng3 101077 N/A BeginTime
2413500 zcheng3 101077 N/A BeginTime
2413499 zcheng3 101077 N/A BeginTime
2413498 zcheng3 101077 N/A BeginTime
2413497 zcheng3 101077 N/A BeginTime
2424755 ssunku 89981 gres/gpu:1 Priority
2443209_[0] mgeldokla 81922 gres/gpu:1 Priority
2435968 afrenk 81008 gres/gpu:4 Priority
2435970 afrenk 81006 gres/gpu:4 Dependency
2435969 afrenk 81006 gres/gpu:4 Dependency
2443394 jchang2 80788 N/A Dependency
2443971 mgeldokla 80271 gres/gpu:1 Priority
2444007_[2-11%2] mgeldokla 80270 gres/gpu:1 JobArrayTaskLimit
2444005_[2-3%2] mgeldokla 80270 gres/gpu:1 JobArrayTaskLimit
2444003_[2-5%2] mgeldokla 80270 gres/gpu:1 JobArrayTaskLimit
2444008_[0-5%3] mgeldokla 80270 N/A Dependency
2444006_[0-1%3] mgeldokla 80270 N/A Dependency
2444004_[0-2%3] mgeldokla 80270 N/A Dependency
2444161 mgeldokla 80120 N/A BeginTime
2443770 jchang2 79932 N/A Dependency
2443769 jchang2 79892 gres/gpu:1,gres/gpumem:80G Priority
2437827 afrenk 74550 gres/gpu:4 Priority
2430148_5 yzhao19 74150 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_8 yzhao19 73397 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_7 yzhao19 73397 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_6 yzhao19 73397 gres/gpu:A100:1,gres/gpumem:75G Priority
2440465_[0-5] pgundu 73088 gres/gpu:L40S:1 Dependency
2439491 alignatiev 71204 gres/gpu:1 Priority
2440534 bdweber 70278 gres/gpu:1 Priority
2440527 bdweber 70278 gres/gpu:1 Priority
2443752 svnikam 68556 gres/gpu:1 Priority
2443916 ctighe 68086 gres/gpu:1 Priority
2443801 bdweber 67665 gres/gpu:1 Priority
2443786 vmullur 65930 gres/gpu:1 Priority
2439443_1 pgundu 65866 gres/gpu:L40S:1 Priority
2439443_3 pgundu 65722 gres/gpu:L40S:1 Priority
2439443_2 pgundu 65722 gres/gpu:L40S:1 Priority
2439443_4 pgundu 65722 gres/gpu:L40S:1 Priority
2440754 nbpulsone 65712 gres/gpu:1 Priority
2439442_0 pgundu 65657 gres/gpu:L40S:1 Priority
2442340 klin5 65314 gres/gpu:1 Priority
2442338 klin5 65314 gres/gpu:1 Priority
2442342 klin5 65314 gres/gpu:1 Priority
2439443_8 pgundu 64886 gres/gpu:L40S:1 Priority
2439443_7 pgundu 64886 gres/gpu:L40S:1 Priority
2439443_6 pgundu 64886 gres/gpu:L40S:1 Priority
2439443_5 pgundu 64886 gres/gpu:L40S:1 Priority
2439443_0 pgundu 64886 gres/gpu:L40S:1 Priority
2443035 alignatiev 64334 gres/gpu:1 Priority
2443882 afrenk 64073 gres/gpu:1 Priority
$ squeue -p quick -t PD --sort=-p -o %i %u %Q %b %r
JOBID USER PRIORITY TRES_PER_NODE REASON
2440722 dehalloran 88964 gres/gpu:A100:1 Nodes required for job are DOWN, DRAINED, REBOOTING or reserved for jobs in higher priority partitions
2440504 spatadia 87510 gres/gpu:A100:1 Priority
2441582 zhuang5 65418 gres/gpu:1,gres/gpumem:16G Priority
2441842 sselvaraj 24751 gres/gpu:1 Priority
2441863 sselvaraj 24728 gres/gpu:1 Dependency
2441862 sselvaraj 24728 gres/gpu:1 Dependency
2441861 sselvaraj 24728 gres/gpu:1 Dependency
2441860 sselvaraj 24728 gres/gpu:1 Dependency
2441859 sselvaraj 24728 gres/gpu:1 Dependency
2441858 sselvaraj 24728 gres/gpu:1 Dependency
2441857 sselvaraj 24728 gres/gpu:1 Dependency
2441856 sselvaraj 24728 gres/gpu:1 Dependency
2439893_[0-5,8] tdappenzeller 22291 gres/gpu:rtx_pro_6000_b:1 Priority
2439896_[6-7] tdappenzeller 22288 gres/gpu:rtx_pro_6000_b:1 Priority
2443732 sselvaraj 21596 gres/gpu:1 Priority
2441270 kle6 21334 gres/gpu:1 Priority
2441269 kle6 21334 gres/gpu:1 Priority
2439853 tmondal 21170 gres/gpu:1 Priority
2439800 aakarande 16763 gres/gpu:1 Priority
2437169 aakarande 16735 gres/gpu:1 Priority
2443881 jyu7 15904 gres/gpu:1,gres/gpumem:80G Priority
2443880 jyu7 15904 gres/gpu:1,gres/gpumem:80G Priority
2440949 aakarande 14698 gres/gpu:1 Priority
2443525_[0] aakarande 8843 gres/gpu:1 Priority
$ bash -c squeue -p short -t R -h -o '%b %N' | sort | uniq -c | sort -rn | head -30
     14 N/A compute-2-08
     13 N/A compute-2-06
      9 N/A compute-4-08
      8 N/A compute-2-03
      7 N/A compute-4-02
      6 N/A compute-3-08
      5 N/A compute-4-03
      5 N/A compute-3-07
      5 N/A compute-2-01
      4 gres/gpu:1 gpu-5-23
      4 gres/gpu:1 gpu-5-21
      3 N/A compute-3-06
      3 N/A compute-3-05
      3 N/A compute-2-07
      3 N/A compute-2-02
      2 gres/gpu:4 gpu-5-32
      2 N/A compute-4-01
      2 N/A compute-3-04
      2 N/A compute-3-02
      2 N/A compute-3-01
      2 N/A compute-2-05
      1 gres/gpu:1 whitehill-0-02
      1 gres/gpu:1 gpu-6-12
      1 gres/gpu:1 gpu-5-28
      1 gres/gpu:1 gpu-4-11
      1 N/A compute-4-06
      1 N/A compute-4-05
      1 N/A compute-3-03
      1 N/A aswin-02
$ sinfo -p short -N -o %N %G %C %T --noheader
aswin-02 (null) 1/63/0/64 mixed
aswin-03 (null) 0/64/0/64 reserved
aswin-04 (null) 0/64/0/64 reserved
aswin-05 (null) 0/64/0/64 reserved
aswin-06 (null) 0/64/0/64 reserved
aswin-07 (null) 0/64/0/64 reserved
aswin-08 (null) 0/64/0/64 reserved
compute-2-01 (null) 63/1/0/64 mixed
compute-2-02 (null) 60/4/0/64 mixed
compute-2-03 (null) 52/12/0/64 mixed
compute-2-04 (null) 0/0/64/64 drained
compute-2-05 (null) 62/2/0/64 mixed
compute-2-06 (null) 64/0/0/64 allocated
compute-2-07 (null) 33/31/0/64 mixed
compute-2-08 (null) 62/2/0/64 mixed
compute-3-01 (null) 128/64/0/192 mixed-
compute-3-02 (null) 152/40/0/192 mixed
compute-3-03 (null) 189/3/0/192 mixed
compute-3-04 (null) 192/0/0/192 allocated
compute-3-05 (null) 120/72/0/192 mixed
compute-3-06 (null) 184/8/0/192 mixed
compute-3-07 (null) 124/68/0/192 mixed
compute-3-08 (null) 189/3/0/192 mixed
compute-4-01 (null) 128/0/0/128 allocated
compute-4-02 (null) 127/1/0/128 mixed
compute-4-03 (null) 125/3/0/128 mixed
compute-4-05 (null) 112/16/0/128 mixed
compute-4-06 (null) 128/0/0/128 allocated
compute-4-07 (null) 128/0/0/128 allocated
compute-4-08 (null) 128/0/0/128 allocated
gpu-4-11 gpu:A100:4,gpumem:no_consume:80G 33/31/0/64 mixed@
gpu-4-12 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-4-14 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-4-15 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-5-11 gpu:H100:4(S:0-1),gpumem:no_consume:80G 0/0/128/128 down*
gpu-5-12 gpu:H100:4(S:0-1),gpumem:no_consume:80G 0/0/128/128 down*
gpu-5-21 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 32/64/0/96 mixed-
gpu-5-22 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-23 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 32/64/0/96 mixed-
gpu-5-24 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-25 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-26 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-27 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-28 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 12/84/0/96 mixed@
gpu-5-32 gpu:H200:8(S:0-1),gpumem:no_consume:141G 32/96/0/128 mixed@
gpu-5-41 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-42 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-43 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-44 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-6-01 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-02 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-03 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-04 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-05 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-06 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-07 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-08 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-09 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-10 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-11 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-12 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 32/64/0/96 mixed@
gpu-6-13 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-14 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-15 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 32/64/0/96 mixed@
gpu-6-16 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-17 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-18 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-19 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
gpu-6-20 gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G 0/0/96/96 down*
murai-01 gpu:L40S:2(S:0-1),gpumem:no_consume:48G 0/96/0/96 reserved
whitehill-0-02 gpu:A100:2(S:0-1),gpumem:no_consume:40G 8/104/0/112 mixed
```

## sacct 2443897,2443461,2443970

```
$ sacct -P -j 2443897,2443461,2443970 --format=JobID,JobName%30,Partition,State,ExitCode,Submit,Start,End,Elapsed,MaxRSS,ReqMem,AllocTRES%60,NodeList
JobID|JobName|Partition|State|ExitCode|Submit|Start|End|Elapsed|MaxRSS|ReqMem|AllocTRES|NodeList
2443461_0|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T19:50:28|2026-11-01T20:55:34|01:05:06||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_0.batch|batch||FAILED|1:0|2026-11-01T19:50:28|2026-11-01T19:50:28|2026-11-01T20:55:34|01:05:06|142872536K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_1|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T20:06:36|2026-11-01T21:31:23|01:24:47||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-28
2443461_1.batch|batch||FAILED|1:0|2026-11-01T20:06:36|2026-11-01T20:06:36|2026-11-01T21:31:23|01:24:47|166617764K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-28
2443461_2|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T20:55:36|2026-11-01T21:57:16|01:01:40||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_2.batch|batch||FAILED|1:0|2026-11-01T20:55:36|2026-11-01T20:55:36|2026-11-01T21:57:16|01:01:40|131414392K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_3|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T21:46:05|2026-11-01T22:46:36|01:00:31||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443461_3.batch|batch||FAILED|1:0|2026-11-01T21:46:05|2026-11-01T21:46:05|2026-11-01T22:46:36|01:00:31|139024716K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443461_4|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T21:57:42|2026-11-01T22:58:36|01:00:54||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_4.batch|batch||FAILED|1:0|2026-11-01T21:57:42|2026-11-01T21:57:42|2026-11-01T22:58:36|01:00:54|120808952K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_[5-11%2]|q_d3all_v1_c|short|CANCELLED by 901022506|0:0|2026-11-01T18:41:02|None|2026-11-01T22:43:14|00:00:00||160G||None assigned
2443897|q_d3all_v1_adopt1|short|COMPLETED|0:0|2026-11-01T22:12:56|2026-11-01T22:13:21|2026-11-01T22:15:55|00:02:34||64G|billing=8,cpu=8,mem=64G,node=1|compute-2-02
2443897.batch|batch||COMPLETED|0:0|2026-11-01T22:13:21|2026-11-01T22:13:21|2026-11-01T22:15:55|00:02:34|15649736K||cpu=8,mem=64G,node=1|compute-2-02
2443970|q_run_d3_sep2023_20m_t2b_s|short|COMPLETED|0:0|2026-11-01T22:43:14|2026-11-01T22:46:41|2026-11-01T23:16:26|00:29:45||96G|billing=8,cpu=8,gres/gpu=1,mem=96G,node=1|gpu-5-21
2443970.batch|batch||COMPLETED|0:0|2026-11-01T22:46:41|2026-11-01T22:46:41|2026-11-01T23:16:26|00:29:45|100643056K||cpu=8,gres/gpu=1,mem=96G,node=1|gpu-5-21
```

## tail $LF_WORK/d3all_v1/d3all_aug2026/report.json

```
$ tail -n 60 /home/mgeldokla/scratch/lisflood/d3all_v1/d3all_aug2026/report.json
{
 "name": "d3all_aug2026",
 "storm": "aug2026",
 "box": [
  128000.0,
  856000.0,
  206000.0,
  946000.0
 ],
 "shape": [
  4500,
  3900
 ],
 "t0": "2026-08-03T04:00Z",
 "hours": "30",
 "saveint_s": "600",
 "wall_s": 0,
 "solver_s": 925,
 "w9_total_s": 3851,
 "peak_rss_gb": null,
 "raw_results_gb": 44.41,
 "raw_results_files": 367,
 "out_gb": 2.979,
 "out_mb": {
  "frames_cm.npz": 202.1,
  "frames_u8.npz": 104.3,
  "hmax.npy": 70.2,
  "hsnap.npy": 70.2,
  "lisflood_stdout.txt": 2.9,
  "rainstats.npz": 181.7,
  "timing.npz": 1.4,
  "vel_frames.npz": 2085.3,
  "vel_max.npz": 52.4,
  "watermask.npy": 17.6,
  "xings.json": 2.0,
  "z.npy": 70.2,
  "z_raw.npz": 118.7
 },
 "peak_wet_km2": 55.2,
 "rain_total_max_mm": 125,
 "rain_missing_hours": [],
 "git_sha": "ebcd9c31",
 "env": {
  "LF_CN_SCALE": "0.88",
  "LF_EXE": "/home/mgeldokla/scratch/lisflood/build_cuda/lisflood",
  "LF_EXE_CUDA": "1",
  "LF_INFIL_MMH": "2",
  "LF_INFIL_MODE": "rain",
  "LF_INIT_TSTEP": "1",
  "LF_LOSS": "cn",
  "LF_NO_UPLOAD": "1",
  "LF_PARITY": "1",
  "LF_QOUT": "1",
  "LF_SAVEINT": "600",
  "LF_VFRAMES": "1",
  "LF_VOUT": "1"
 },
 "folder": "/home/mgeldokla/scratch/lisflood/run_aug2026_proto_d3all_aug2026"
}
```

## tail $LF_WORK/d3all_v1/d3all_sep2021/report.json

```
$ tail -n 60 /home/mgeldokla/scratch/lisflood/d3all_v1/d3all_sep2021/report.json
{
 "name": "d3all_sep2021",
 "storm": "sep2021",
 "box": [
  128000.0,
  856000.0,
  206000.0,
  946000.0
 ],
 "shape": [
  4500,
  3900
 ],
 "t0": "2021-09-01T18:00Z",
 "hours": "36",
 "saveint_s": "600",
 "wall_s": 0,
 "solver_s": 1292,
 "w9_total_s": 5073,
 "peak_rss_gb": null,
 "raw_results_gb": 53.1,
 "raw_results_files": 439,
 "out_gb": 5.558,
 "out_mb": {
  "frames_cm.npz": 351.1,
  "frames_u8.npz": 187.1,
  "hmax.npy": 70.2,
  "hsnap.npy": 70.2,
  "lisflood_stdout.txt": 3.5,
  "rainstats.npz": 167.6,
  "timing.npz": 3.0,
  "vel_frames.npz": 4399.9,
  "vel_max.npz": 96.3,
  "watermask.npy": 17.6,
  "xings.json": 2.1,
  "z.npy": 70.2,
  "z_raw.npz": 118.7
 },
 "peak_wet_km2": 199.2,
 "rain_total_max_mm": 158,
 "rain_missing_hours": [],
 "git_sha": "ebcd9c31",
 "env": {
  "LF_CN_SCALE": "0.88",
  "LF_EXE": "/home/mgeldokla/scratch/lisflood/build_cuda/lisflood",
  "LF_EXE_CUDA": "1",
  "LF_INFIL_MMH": "2",
  "LF_INFIL_MODE": "rain",
  "LF_INIT_TSTEP": "1",
  "LF_LOSS": "cn",
  "LF_NO_UPLOAD": "1",
  "LF_PARITY": "1",
  "LF_QOUT": "1",
  "LF_SAVEINT": "600",
  "LF_VFRAMES": "1",
  "LF_VOUT": "1"
 },
 "folder": "/home/mgeldokla/scratch/lisflood/run_sep2021_proto_d3all_sep2021"
}
```

## tail $LF_WORK/d3all_v1/d3all_sep2022/FAILED

```
$ tail -n 60 /home/mgeldokla/scratch/lisflood/d3all_v1/d3all_sep2022/FAILED
no meta.json
```
