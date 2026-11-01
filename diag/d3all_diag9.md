# Turing diagnostics: d3all_diag9

2026-11-01T22:13:24Z on compute-2-02.int.turing.wpi.edu, job 2443898, repo 26e5a208

## disk and quota

```
$ df -h /home/mgeldokla /home/mgeldokla/scratch /home/mgeldokla/scratch/lisflood
Filesystem                                                                                                                                                        Size  Used Avail Use% Mounted on
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/home/1c0b431a-0173-438f-85b5-1dfe3ac805cc     1.8P  1.2P  655T  64% /home
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  655T  64% /scratch
10.128.144.101:6789,10.128.144.102:6789,10.128.144.103:6789,10.128.144.104:6789,10.128.144.105:6789:/volumes/turing/scratch/b64517ac-7392-486c-abd8-53a3a064990c  1.8P  1.2P  655T  64% /scratch
$ readlink -f /home/mgeldokla/scratch
/scratch/mgeldokla
$ quota -s
timeout: failed to run command 'quota': Permission denied
$ bash -c du -sh /home/mgeldokla/scratch/lisflood/* 2>/dev/null | sort -h | tail -n 50
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
4.2G	/home/mgeldokla/scratch/lisflood/run_forecast_fcd3_e2etest2_d3_2023091112_m0
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
34G	/home/mgeldokla/scratch/lisflood/amcnwm_v1
41G	/home/mgeldokla/scratch/lisflood/inlets_v1
73G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any
253G	/home/mgeldokla/scratch/lisflood/d3all_v1
$ du -sh /home/mgeldokla/scratch/lisflood
813G	/home/mgeldokla/scratch/lisflood
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

$ squeue -u mgeldokla -o %i %j %P %T %M %l %R %b
JOBID NAME PARTITION STATE TIME TIME_LIMIT NODELIST(REASON) TRES_PER_NODE
2443862 q_pack_t2_sep2018m_milford long PENDING 0:00 3:00:00 (Dependency) N/A
2443860 q_pack_t2_sep2018_fitchburg long PENDING 0:00 3:00:00 (Dependency) N/A
2443858 q_pack_t2_jul2023_worcester long PENDING 0:00 3:00:00 (Dependency) N/A
2443856 q_pack_t2_jun2020_northbridge long PENDING 0:00 3:00:00 (Dependency) N/A
2443854 q_pack_t2_aug2023_metrowest long PENDING 0:00 3:00:00 (Dependency) N/A
2443852 q_pack_t2_sep2022_webster long PENDING 0:00 3:00:00 (Dependency) N/A
2443850 q_pack_t2_sep2021_worcester long PENDING 0:00 3:00:00 (Dependency) N/A
2443848 q_pack_t2_aug2026_leominster long PENDING 0:00 3:00:00 (Dependency) N/A
2443846 q_pack_t2_worcester_aug2021 long PENDING 0:00 3:00:00 (Dependency) N/A
2443844 q_pack_t2_leominster_sep2023 long PENDING 0:00 3:00:00 (Dependency) N/A
2443842 q_pack_d3_sep2023_20m_t2 long PENDING 0:00 10:00:00 (Dependency) N/A
2443209_[0] q_fcd3_e2etest_d3_2023091112_g short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443461_[5-11%2] q_d3all_v1_c short PENDING 0:00 16:00:00 (JobArrayTaskLimit) gres/gpu:1
2443863_[0-23%2] q_d3all_v2_a short PENDING 0:00 16:00:00 (Priority) gres/gpu:1
2443857 q_run_t2_jul2023_worcester short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443859 q_run_t2_sep2018_fitchburg short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443861 q_run_t2_sep2018m_milford short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443855 q_run_t2_jun2020_northbridge short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443853 q_run_t2_aug2023_metrowest short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443851 q_run_t2_sep2022_webster short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443849 q_run_t2_sep2021_worcester short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443847 q_run_t2_aug2026_leominster short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443845 q_run_t2_worcester_aug2021 short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443843 q_run_t2_leominster_sep2023 short PENDING 0:00 6:00:00 (Priority) gres/gpu:1
2443840_[0-11%2] q_d3all_v1_b4 short PENDING 0:00 16:00:00 (Priority) gres/gpu:1
2443841 q_run_d3_sep2023_20m_t2 short PENDING 0:00 16:00:00 (Priority) gres/gpu:1
2443895 flood_queue short PENDING 0:00 20:00 (BeginTime) N/A
2443461_4 q_d3all_v1_c short RUNNING 17:44 16:00:00 gpu-5-23 gres/gpu:1
2443461_3 q_d3all_v1_c short RUNNING 29:21 16:00:00 gpu-5-21 gres/gpu:1
2443897 q_d3all_v1_adopt1 short RUNNING 2:05 2:00:00 compute-2-02 N/A
2443898 q_d3all_diag9 short RUNNING 2:05 30:00 compute-2-02 N/A
array tasks expanded: 71, job records: 31
```

## GPU queue position (short / quick)

```
$ sprio -u mgeldokla
          JOBID PARTITION     USER   PRIORITY       SITE        AGE  FAIRSHARE    JOBSIZE  PARTITION
        2443209 short     mgeldokl      81693          0       1500      79188          6       1000
        2443461 short     mgeldokl      81243          0       1050      79188          6       1000
        2443840 short     mgeldokl      80341          0        148      79188          6       1000
        2443841 short     mgeldokl      80341          0        148      79188          6       1000
        2443842 long      mgeldokl      79441          0        148      79188          6        100
        2443843 short     mgeldokl      80341          0        148      79188          6       1000
        2443844 long      mgeldokl      79441          0        148      79188          6        100
        2443845 short     mgeldokl      80341          0        148      79188          6       1000
        2443846 long      mgeldokl      79441          0        148      79188          6        100
        2443847 short     mgeldokl      80341          0        148      79188          6       1000
        2443848 long      mgeldokl      79441          0        148      79188          6        100
        2443849 short     mgeldokl      80341          0        148      79188          6       1000
        2443850 long      mgeldokl      79441          0        148      79188          6        100
        2443851 short     mgeldokl      80341          0        148      79188          6       1000
        2443852 long      mgeldokl      79441          0        148      79188          6        100
        2443853 short     mgeldokl      80341          0        148      79188          6       1000
        2443854 long      mgeldokl      79441          0        148      79188          6        100
        2443855 short     mgeldokl      80341          0        148      79188          6       1000
        2443856 long      mgeldokl      79441          0        148      79188          6        100
        2443857 short     mgeldokl      80341          0        148      79188          6       1000
        2443858 long      mgeldokl      79441          0        148      79188          6        100
        2443859 short     mgeldokl      80341          0        148      79188          6       1000
        2443860 long      mgeldokl      79441          0        148      79188          6        100
        2443861 short     mgeldokl      80341          0        148      79188          6       1000
        2443862 long      mgeldokl      79441          0        148      79188          6        100
        2443863 short     mgeldokl      80341          0        148      79188          6       1000
        2443895 short     mgeldokl      80193          0          0      79188          5       1000
      1 whitehill-0-02 A100 gpu:A100:2(S:0-1),gpumem:no_consume:40G mixed
      3 gpu-4-12 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G down*
      1 gpu-4-11 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G mixed@
      7 aswin-02 EPYC-7543 (null) reserved
      1 compute-2-04 EPYC-7543,AMD (null) drained
      7 compute-2-01 EPYC-7543,AMD (null) mixed
      7 compute-3-02 EPYC-9654,AMD (null) mixed
      1 compute-3-01 EPYC-9654,AMD (null) mixed-
      2 gpu-5-11 H100 gpu:H100:4(S:0-1),gpumem:no_consume:80G down*
      1 gpu-5-32 H200 gpu:H200:8(S:0-1),gpumem:no_consume:141G mixed@
      3 compute-4-01 Intel,6767P (null) allocated
      4 compute-4-02 Intel,6767P (null) mixed
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
2413510 ttjokro 121936 N/A DependencyNeverSatisfied
2415396 afrenk 104734 N/A Dependency
2413506 zcheng3 100755 N/A BeginTime
2413505 zcheng3 100755 N/A BeginTime
2413504 zcheng3 100755 N/A BeginTime
2413503 zcheng3 100755 N/A BeginTime
2413502 zcheng3 100755 N/A BeginTime
2413501 zcheng3 100755 N/A BeginTime
2413500 zcheng3 100755 N/A BeginTime
2413499 zcheng3 100755 N/A BeginTime
2413498 zcheng3 100755 N/A BeginTime
2413497 zcheng3 100755 N/A BeginTime
2424755 ssunku 89659 gres/gpu:1 Resources
2443209_[0] mgeldokla 81693 gres/gpu:1 Priority
2443461_[5-11%2] mgeldokla 81243 gres/gpu:1 JobArrayTaskLimit
2435968 afrenk 80685 gres/gpu:4 Priority
2435970 afrenk 80683 gres/gpu:4 Dependency
2435969 afrenk 80683 gres/gpu:4 Dependency
2443394 jchang2 80465 N/A Dependency
2443863_[0-23%2] mgeldokla 80341 gres/gpu:1 Priority
2443857 mgeldokla 80341 gres/gpu:1 Priority
2443859 mgeldokla 80341 gres/gpu:1 Priority
2443861 mgeldokla 80341 gres/gpu:1 Priority
2443855 mgeldokla 80341 gres/gpu:1 Priority
2443853 mgeldokla 80341 gres/gpu:1 Priority
2443851 mgeldokla 80341 gres/gpu:1 Priority
2443849 mgeldokla 80341 gres/gpu:1 Priority
2443847 mgeldokla 80341 gres/gpu:1 Priority
2443845 mgeldokla 80341 gres/gpu:1 Priority
2443843 mgeldokla 80341 gres/gpu:1 Priority
2443840_[0-11%2] mgeldokla 80341 gres/gpu:1 Priority
2443841 mgeldokla 80341 gres/gpu:1 Priority
2443895 mgeldokla 80193 N/A BeginTime
2443770 jchang2 79609 N/A Dependency
2443769 jchang2 79569 gres/gpu:1,gres/gpumem:80G Priority
2437827 afrenk 74227 gres/gpu:4 Priority
2430148_5 yzhao19 73827 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_8 yzhao19 73075 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_7 yzhao19 73075 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_6 yzhao19 73075 gres/gpu:A100:1,gres/gpumem:75G Priority
2440465_[0-5] pgundu 72766 gres/gpu:L40S:1 Dependency
2439491 alignatiev 70882 gres/gpu:1 Priority
2440527 bdweber 69956 gres/gpu:1 Priority
2440534 bdweber 69956 gres/gpu:1 Priority
2443752 svnikam 68233 gres/gpu:1 Priority
2443801 bdweber 67343 gres/gpu:1 Priority
2443786 vmullur 65607 gres/gpu:1 Priority
2439443_1 pgundu 65544 gres/gpu:L40S:1 Priority
2439443_4 pgundu 65400 gres/gpu:L40S:1 Priority
2439443_3 pgundu 65400 gres/gpu:L40S:1 Priority
2439443_2 pgundu 65400 gres/gpu:L40S:1 Priority
2440754 nbpulsone 65390 gres/gpu:1 Priority
2439442_0 pgundu 65335 gres/gpu:L40S:1 Priority
2442342 klin5 64992 gres/gpu:1 Priority
2442340 klin5 64992 gres/gpu:1 Priority
2442338 klin5 64992 gres/gpu:1 Priority
2443035 alignatiev 64012 gres/gpu:1 Priority
$ squeue -p quick -t PD --sort=-p -o %i %u %Q %b %r
JOBID USER PRIORITY TRES_PER_NODE REASON
2440722 dehalloran 88642 gres/gpu:A100:1 Nodes required for job are DOWN, DRAINED, REBOOTING or reserved for jobs in higher priority partitions
2440504 spatadia 87188 gres/gpu:A100:1 Priority
2441582 zhuang5 65095 gres/gpu:1,gres/gpumem:16G Priority
2441842 sselvaraj 24429 gres/gpu:1 Priority
2441863 sselvaraj 24406 gres/gpu:1 Dependency
2441862 sselvaraj 24406 gres/gpu:1 Dependency
2441861 sselvaraj 24406 gres/gpu:1 Dependency
2441860 sselvaraj 24406 gres/gpu:1 Dependency
2441859 sselvaraj 24406 gres/gpu:1 Dependency
2441858 sselvaraj 24406 gres/gpu:1 Dependency
2441857 sselvaraj 24406 gres/gpu:1 Dependency
2441856 sselvaraj 24406 gres/gpu:1 Dependency
2439893_[0-5,8] tdappenzeller 21968 gres/gpu:rtx_pro_6000_b:1 Priority
2439896_[6-7] tdappenzeller 21966 gres/gpu:rtx_pro_6000_b:1 Priority
2443732 sselvaraj 21274 gres/gpu:1 Priority
2441270 kle6 21012 gres/gpu:1 Priority
2441269 kle6 21012 gres/gpu:1 Priority
2439853 tmondal 20848 gres/gpu:1 Priority
2439800 aakarande 16441 gres/gpu:1 Priority
2437169 aakarande 16413 gres/gpu:1 Priority
2443881 jyu7 15581 gres/gpu:1,gres/gpumem:80G Priority
2443880 jyu7 15581 gres/gpu:1,gres/gpumem:80G Priority
2440949 aakarande 14375 gres/gpu:1 Priority
2443525_[0] aakarande 8521 gres/gpu:1 Priority
$ bash -c squeue -p short -t R -h -o '%b %N' | sort | uniq -c | sort -rn | head -30
      6 N/A compute-3-08
      5 N/A compute-3-07
      5 N/A compute-3-05
      5 N/A compute-2-06
      4 N/A compute-3-02
      4 N/A compute-2-08
      4 N/A compute-2-01
      3 gres/gpu:L40S:1 gpu-5-23
      3 gres/gpu:L40S:1 gpu-5-21
      3 N/A compute-3-06
      3 N/A compute-3-03
      3 N/A compute-2-03
      3 N/A compute-2-02
      2 gres/gpu:4 gpu-5-32
      2 gres/gpu:1 whitehill-0-02
      2 N/A compute-4-01
      2 N/A compute-3-04
      2 N/A compute-3-01
      2 N/A compute-2-05
      1 gres/gpu:1 gpu-5-28
      1 gres/gpu:1 gpu-5-23
      1 gres/gpu:1 gpu-5-21
      1 N/A compute-4-08
      1 N/A compute-4-06
      1 N/A compute-4-05
      1 N/A compute-4-03
      1 N/A compute-4-02
      1 N/A compute-2-07
$ sinfo -p short -N -o %N %G %C %T --noheader
aswin-02 (null) 0/64/0/64 reserved
aswin-03 (null) 0/64/0/64 reserved
aswin-04 (null) 0/64/0/64 reserved
aswin-05 (null) 0/64/0/64 reserved
aswin-06 (null) 0/64/0/64 reserved
aswin-07 (null) 0/64/0/64 reserved
aswin-08 (null) 0/64/0/64 reserved
compute-2-01 (null) 54/10/0/64 mixed
compute-2-02 (null) 61/3/0/64 mixed
compute-2-03 (null) 12/52/0/64 mixed
compute-2-04 (null) 0/0/64/64 drained
compute-2-05 (null) 62/2/0/64 mixed
compute-2-06 (null) 32/32/0/64 mixed
compute-2-07 (null) 5/59/0/64 mixed
compute-2-08 (null) 22/42/0/64 mixed
compute-3-01 (null) 128/64/0/192 mixed-
compute-3-02 (null) 160/32/0/192 mixed
compute-3-03 (null) 125/67/0/192 mixed
compute-3-04 (null) 184/8/0/192 mixed
compute-3-05 (null) 188/4/0/192 mixed
compute-3-06 (null) 152/40/0/192 mixed
compute-3-07 (null) 124/68/0/192 mixed
compute-3-08 (null) 189/3/0/192 mixed
compute-4-01 (null) 128/0/0/128 allocated
compute-4-02 (null) 103/25/0/128 mixed
compute-4-03 (null) 89/39/0/128 mixed
compute-4-05 (null) 87/41/0/128 mixed
compute-4-06 (null) 128/0/0/128 allocated
compute-4-07 (null) 128/0/0/128 allocated
compute-4-08 (null) 105/23/0/128 mixed
gpu-4-11 gpu:A100:4,gpumem:no_consume:80G 32/32/0/64 mixed@
gpu-4-12 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-4-14 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-4-15 gpu:A100:4,gpumem:no_consume:80G 0/0/64/64 down*
gpu-5-11 gpu:H100:4(S:0-1),gpumem:no_consume:80G 0/0/128/128 down*
gpu-5-12 gpu:H100:4(S:0-1),gpumem:no_consume:80G 0/0/128/128 down*
gpu-5-21 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 24/72/0/96 mixed-
gpu-5-22 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 0/0/96/96 down*
gpu-5-23 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 20/76/0/96 mixed-
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

## sacct 2443418,2443461

```
$ sacct -P -j 2443418,2443461 --format=JobID,JobName%30,Partition,State,ExitCode,Submit,Start,End,Elapsed,MaxRSS,ReqMem,AllocTRES%60,NodeList
JobID|JobName|Partition|State|ExitCode|Submit|Start|End|Elapsed|MaxRSS|ReqMem|AllocTRES|NodeList
2443418|q_run_d3_sep2023_20m_any|short|COMPLETED|0:0|2026-11-01T18:10:56|2026-11-01T19:44:55|2026-11-01T21:45:49|02:00:54||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443418.batch|batch||COMPLETED|0:0|2026-11-01T19:44:55|2026-11-01T19:44:55|2026-11-01T21:45:49|02:00:54|167751776K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443461_0|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T19:50:28|2026-11-01T20:55:34|01:05:06||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_0.batch|batch||FAILED|1:0|2026-11-01T19:50:28|2026-11-01T19:50:28|2026-11-01T20:55:34|01:05:06|142872536K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_1|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T20:06:36|2026-11-01T21:31:23|01:24:47||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-28
2443461_1.batch|batch||FAILED|1:0|2026-11-01T20:06:36|2026-11-01T20:06:36|2026-11-01T21:31:23|01:24:47|166617764K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-28
2443461_2|q_d3all_v1_c|short|FAILED|1:0|2026-11-01T18:41:02|2026-11-01T20:55:36|2026-11-01T21:57:16|01:01:40||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_2.batch|batch||FAILED|1:0|2026-11-01T20:55:36|2026-11-01T20:55:36|2026-11-01T21:57:16|01:01:40|131414392K||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_3|q_d3all_v1_c|short|RUNNING|0:0|2026-11-01T18:41:02|2026-11-01T21:46:05|Unknown|00:29:21||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443461_3.batch|batch||RUNNING|0:0|2026-11-01T21:46:05|2026-11-01T21:46:05|Unknown|00:29:21|||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443461_4|q_d3all_v1_c|short|RUNNING|0:0|2026-11-01T18:41:02|2026-11-01T21:57:42|Unknown|00:17:44||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_4.batch|batch||RUNNING|0:0|2026-11-01T21:57:42|2026-11-01T21:57:42|Unknown|00:17:44|||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_[5-11%2]|q_d3all_v1_c|short|PENDING|0:0|2026-11-01T18:41:02|Unknown|Unknown|00:00:00||160G||None assigned
```

## work folder run_sep2023_proto_site_d3_sep2023_any

```
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any
73G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any
$ ls -la /home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any/out
total 3658925
drwxrwxr-x 2 mgeldokla mgeldokla         17 Nov  1 21:24 .
drwxrwxr-x 4 mgeldokla mgeldokla          9 Nov  1 21:19 ..
-rw-rw-r-- 1 mgeldokla mgeldokla  276454281 Nov  1 21:24 frames_cm.npz
-rw-rw-r-- 1 mgeldokla mgeldokla   70200128 Nov  1 21:23 hmax.npy
-rw-rw-r-- 1 mgeldokla mgeldokla   70200128 Nov  1 21:23 hsnap.npy
-rw-rw-r-- 1 mgeldokla mgeldokla      84971 Nov  1 21:24 lisflood.mass
-rw-rw-r-- 1 mgeldokla mgeldokla    4738686 Nov  1 21:24 lisflood_stdout.txt
-rw-rw-r-- 1 mgeldokla mgeldokla      10820 Nov  1 21:24 meta.json
-rw-rw-r-- 1 mgeldokla mgeldokla  183725496 Nov  1 21:24 rainstats.npz
-rw-rw-r-- 1 mgeldokla mgeldokla        100 Nov  1 21:24 run.bci
-rw-rw-r-- 1 mgeldokla mgeldokla        222 Nov  1 21:24 run.par
-rw-rw-r-- 1 mgeldokla mgeldokla    1782791 Nov  1 21:24 timing.npz
-rw-rw-r-- 1 mgeldokla mgeldokla 2885970247 Nov  1 21:23 vel_frames.npz
-rw-rw-r-- 1 mgeldokla mgeldokla   44526125 Nov  1 21:24 vel_max.npz
-rw-rw-r-- 1 mgeldokla mgeldokla     559376 Nov  1 21:24 w9_log.txt
-rw-rw-r-- 1 mgeldokla mgeldokla   17550128 Nov  1 21:24 watermask.npy
-rw-rw-r-- 1 mgeldokla mgeldokla    2063996 Nov  1 21:24 xings.json
-rw-rw-r-- 1 mgeldokla mgeldokla   70200128 Nov  1 21:23 z.npy
-rw-rw-r-- 1 mgeldokla mgeldokla  118666599 Nov  1 21:24 z_raw.npz
$ du -sh /home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any/results
66G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any/results
wd: 289 files, last res-0288.wd 105304633 bytes
elev: 289 files, last res-0288.elev 137225849 bytes
Vx: 0 files, last none  bytes
Vy: 0 files, last none  bytes
Qx: 0 files, last none  bytes
Qy: 0 files, last none  bytes
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Nov  1 19:58 res-0092.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225941 Nov  1 19:58 res-0093.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Nov  1 19:58 res-0093.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225939 Nov  1 19:58 res-0094.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Nov  1 19:58 res-0094.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225935 Nov  1 19:58 res-0095.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Nov  1 19:58 res-0095.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225934 Nov  1 19:59 res-0096.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Nov  1 19:59 res-0096.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225934 Nov  1 19:59 res-0097.elev
-rw-rw-r-- 1 mgeldokla mgeldokla 105304633 Nov  1 19:59 res-0097.wd
-rw-rw-r-- 1 mgeldokla mgeldokla 137225934 Nov  1 19:59 res-0098.elev
```

## tail roadflood_2443418.out

```
$ ls -la /home/mgeldokla/mass-flood-watch/roadflood_2443418.out
-rw-rw-r-- 1 mgeldokla mgeldokla 11839 Nov  1 21:45 /home/mgeldokla/mass-flood-watch/roadflood_2443418.out
$ tail -n 40 /home/mgeldokla/mass-flood-watch/roadflood_2443418.out
   "obs_centroid_utc": "2023-09-12T20:18Z",
   "model_centroid_utc": null,
   "centroid_error_h": null,
   "centroid_gap_h": 0.0,
   "timing_error_robust_h": -46.75,
   "timing_metric": "peak_interval"
  }
 ],
 "mean_abs_rise_error_m": 0.42,
 "mean_rise_bias_m": -0.26,
 "mean_abs_timing_error_h": 21.1,
 "mean_abs_peak_timing_error_h": 17.1,
 "mean_abs_peak_timing_error_interval_h": 16.7,
 "mean_abs_rise50_error_h": 12.3,
 "mean_abs_centroid_error_h": 9.2,
 "gauges_gap_flagged": 1,
 "timing_note": "mean_abs_timing_error_h = mean |timing_error_robust_h| (rising-limb 50 % time; peak interval when no crossing); raw peak-time mean in mean_abs_peak_timing_error_h (until 22 Oct 2026 mean_abs_timing_error_h held that)",
 "mean_abs_wse_error_m": 2.56
}
parity pack: results/site_d3_sep2023_any {'wet_land_km2_0p1': 48.2136, 'wet_land_km2_0p3': 14.2424, 'snap_wet_land_km2_0p3': 13.828800000000001, 'spike_cells_0p3': 747}
 },
 "all": {
  "n": 121,
  "hit_10": 0.967,
  "hit_30": 0.76
 },
 "random_road_points": {
  "n": 2000,
  "hit_10": 0.207,
  "hit_30": 0.075
 }
}
 ],
 "made": "2026-11-01 21:34",
 "prototype_runtime_s": 580.9
}
wrote results/site_d3_sep2023_any
wrote /tmp/mlx_rdg0ipl_
/home/mgeldokla/mass-flood-watch/docs/proto/ml/features_sep2023.csv: 45099 segments, 114 positive, 144 sites matched
results in results/site_d3_sep2023_any (map.html, watchlist.csv, REPORT.md, summary.json, score.json)
```

## tail plan_display_2443461_2.out

```
$ ls -la /home/mgeldokla/mass-flood-watch/plan_display_2443461_2.out
-rw-rw-r-- 1 mgeldokla mgeldokla 2453 Nov  1 21:57 /home/mgeldokla/mass-flood-watch/plan_display_2443461_2.out
$ tail -n 40 /home/mgeldokla/mass-flood-watch/plan_display_2443461_2.out
ERROR: Unable to locate a modulefile for '{cuda/12.9.0/b3yzg3f <L>}'
Sun Nov  1 20:55:42 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 595.71.05              Driver Version: 595.71.05      CUDA Version: 13.2     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L40S                    Off |   00000000:4A:00.0 Off |                    0 |
| N/A   29C    P8             31W /  350W |       0MiB /  46068MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
code ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906 in /home/mgeldokla/scratch/lisflood/code_ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906
plan proto/turing/plans/d3all_v1.json indices: 6 
== task 6: d3all_sep2022 (sep2022) box 128000,856000,206000,946000 hours 30, 670774G free  2026-11-01T20:55:42Z
BOX=128000,856000,206000,946000
HOURS=30
LF_CN_SCALE=0.88
LF_INFIL_MMH=2
LF_LOSS=cn
LF_PARITY=1
LF_QOUT=1
LF_SAVEINT=600
LF_VFRAMES=1
LF_VOUT=1
NAME=d3all_sep2022
RES=20
RESULTS_ROOT=d3all_v1
STORM=sep2022
FAILED d3all_sep2022: no meta.json
tasks: 1, failed: 1
```

## tail plan_display_2443461_3.out

```
$ ls -la /home/mgeldokla/mass-flood-watch/plan_display_2443461_3.out
-rw-rw-r-- 1 mgeldokla mgeldokla 2398 Nov  1 21:46 /home/mgeldokla/mass-flood-watch/plan_display_2443461_3.out
$ tail -n 40 /home/mgeldokla/mass-flood-watch/plan_display_2443461_3.out
ERROR: Unable to locate a modulefile for '{miniconda3/25.1.1/24g7bpu <L>}'
ERROR: Unable to locate a modulefile for '{cuda/12.9.0/b3yzg3f <L>}'
ERROR: Unable to locate a modulefile for '{cuda/12.9.0/b3yzg3f <L>}'
Sun Nov  1 21:46:11 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 595.71.05              Driver Version: 595.71.05      CUDA Version: 13.2     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA L40S                    Off |   00000000:4A:00.0 Off |                    0 |
| N/A   30C    P8             33W /  350W |       0MiB /  46068MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
code ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906 in /home/mgeldokla/scratch/lisflood/code_ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906
plan proto/turing/plans/d3all_v1.json indices: 3 
== task 3: d3all_aug2023 (aug2023) box 128000,856000,206000,946000 hours 30, 670709G free  2026-11-01T21:46:12Z
BOX=128000,856000,206000,946000
HOURS=30
LF_CN_SCALE=0.88
LF_INFIL_MMH=2
LF_LOSS=cn
LF_PARITY=1
LF_QOUT=1
LF_SAVEINT=600
LF_VFRAMES=1
LF_VOUT=1
NAME=d3all_aug2023
RES=20
RESULTS_ROOT=d3all_v1
STORM=aug2023
```
