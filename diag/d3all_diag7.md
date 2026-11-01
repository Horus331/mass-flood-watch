# Turing diagnostics: d3all_diag7

2026-11-01T20:42:34Z on compute-2-07.int.turing.wpi.edu, job 2443757, repo 5cb53de2

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
136G	/home/mgeldokla/scratch/lisflood/run_sep2023_proto_site_d3_sep2023_any
199G	/home/mgeldokla/scratch/lisflood/d3all_v1
$ du -sh /home/mgeldokla/scratch/lisflood
797G	/home/mgeldokla/scratch/lisflood
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
2443461_[2-11%2] q_d3all_v1_c short PENDING 0:00 16:00:00 (JobArrayTaskLimit) gres/gpu:1
2443460_[0-11%2] q_d3all_v1_b2 short PENDING 0:00 10:00:00 (Priority) gres/gpu:1
2443754 flood_queue short PENDING 0:00 20:00 (BeginTime) N/A
2443418 q_run_d3_sep2023_20m_any short RUNNING 59:11 16:00:00 gpu-5-21 gres/gpu:1
2443461_1 q_d3all_v1_c short RUNNING 37:30 16:00:00 gpu-5-28 gres/gpu:1
2443461_0 q_d3all_v1_c short RUNNING 53:38 16:00:00 gpu-5-23 gres/gpu:1
2443757 q_d3all_diag7 short RUNNING 1:38 30:00 compute-2-07 N/A
array tasks expanded: 31, job records: 11
```

## GPU queue position (short / quick)

```
$ sprio -u mgeldokla
          JOBID PARTITION     USER   PRIORITY       SITE        AGE  FAIRSHARE    JOBSIZE  PARTITION
        2443209 short     mgeldokl      81246          0       1053      79188          6       1000
        2443210 short     mgeldokl      81246          0       1053      79188          6       1000
        2443211 long      mgeldokl      80346          0       1053      79188          6        100
        2443419 long      mgeldokl      80046          0        753      79188          6        100
        2443460 short     mgeldokl      80796          0        603      79188          6       1000
        2443461 short     mgeldokl      80796          0        603      79188          6       1000
        2443754 short     mgeldokl      80196          0          3      79188          5       1000
      1 whitehill-0-02 A100 gpu:A100:2(S:0-1),gpumem:no_consume:40G mixed
      3 gpu-4-12 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G down*
      1 gpu-4-11 A100,EPYC-7543,A100-80G gpu:A100:4,gpumem:no_consume:80G mixed@
      1 aswin-02 EPYC-7543 (null) mixed
      6 aswin-03 EPYC-7543 (null) reserved
      5 compute-2-01 EPYC-7543,AMD (null) allocated
      1 compute-2-04 EPYC-7543,AMD (null) drained
      2 compute-2-02 EPYC-7543,AMD (null) mixed
      4 compute-3-01 EPYC-9654,AMD (null) allocated
      3 compute-3-03 EPYC-9654,AMD (null) mixed
      1 compute-3-06 EPYC-9654,AMD (null) mixed-
      2 gpu-5-11 H100 gpu:H100:4(S:0-1),gpumem:no_consume:80G down*
      1 gpu-5-32 H200 gpu:H200:8(S:0-1),gpumem:no_consume:141G mixed@
      2 compute-4-01 Intel,6767P (null) allocated
      5 compute-4-02 Intel,6767P (null) mixed
      1 murai-01 L40S gpu:L40S:2(S:0-1),gpumem:no_consume:48G reserved
      9 gpu-5-22 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G down*
      2 gpu-5-21 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G mixed-
      1 gpu-5-28 L40S gpu:L40S:4(S:0-1),gpumem:no_consume:48G mixed@
     17 gpu-6-01 RTX6000B,Intel gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G down*
      3 gpu-6-07 RTX6000B,Intel gpu:rtx_pro_6000_b:2(S:0-1),gpumem:no_consume:96G mixed@
      1 $ sinfo -N -p short -o %N %f %G %T --noheader
$ squeue -p short -t PD --sort=-p -o %i %u %Q %b %r
JOBID USER PRIORITY TRES_PER_NODE REASON
2210407 zhuang5 155508 N/A DependencyNeverSatisfied
2210346 zhuang5 155508 N/A DependencyNeverSatisfied
2413510 ttjokro 121490 N/A DependencyNeverSatisfied
2415396 afrenk 104288 N/A Dependency
2424758 mataeikachooei 101153 gres/gpu:4 Resources
2413506 zcheng3 100309 N/A BeginTime
2413505 zcheng3 100309 N/A BeginTime
2413504 zcheng3 100309 N/A BeginTime
2413503 zcheng3 100309 N/A BeginTime
2413502 zcheng3 100309 N/A BeginTime
2413501 zcheng3 100309 N/A BeginTime
2413500 zcheng3 100309 N/A BeginTime
2413499 zcheng3 100309 N/A BeginTime
2413498 zcheng3 100309 N/A BeginTime
2413497 zcheng3 100309 N/A BeginTime
2443214 cirwin 91036 gres/gpu:1 Priority
2424755 ssunku 89212 gres/gpu:1 Priority
2442010 jchang2 82962 N/A Dependency
2443210 mgeldokla 81246 gres/gpu:1 Priority
2443209_[0] mgeldokla 81246 gres/gpu:1 Priority
2443461_[2-11%2] mgeldokla 80796 gres/gpu:1 JobArrayTaskLimit
2443460_[0-11%2] mgeldokla 80796 gres/gpu:1 Priority
2435968 afrenk 80239 gres/gpu:4 Priority
2435970 afrenk 80237 gres/gpu:4 Dependency
2435969 afrenk 80237 gres/gpu:4 Dependency
2443754 mgeldokla 80196 N/A BeginTime
2443394 jchang2 80019 N/A Dependency
2443741 vajagadeesh 78442 N/A Dependency
2437827 afrenk 73781 gres/gpu:4 Priority
2430148_5 yzhao19 73381 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_8 yzhao19 72629 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_7 yzhao19 72629 gres/gpu:A100:1,gres/gpumem:75G Priority
2430148_6 yzhao19 72629 gres/gpu:A100:1,gres/gpumem:75G Priority
2440465_[0-5] pgundu 72319 gres/gpu:L40S:1 Dependency
2439491 alignatiev 70436 gres/gpu:1 Priority
2440527 bdweber 69509 gres/gpu:1 Priority
2440534 bdweber 69509 gres/gpu:1 Priority
2443752 svnikam 67787 gres/gpu:1 Priority
2439443_1 pgundu 65097 gres/gpu:L40S:1 Priority
2439443_3 pgundu 64953 gres/gpu:L40S:1 Priority
2439443_2 pgundu 64953 gres/gpu:L40S:1 Priority
2439443_4 pgundu 64953 gres/gpu:L40S:1 Priority
2440754 nbpulsone 64944 gres/gpu:1 Priority
2439442_0 pgundu 64888 gres/gpu:L40S:1 Priority
2442340 klin5 64545 gres/gpu:1 Priority
2442342 klin5 64545 gres/gpu:1 Priority
2442338 klin5 64545 gres/gpu:1 Priority
2443035 alignatiev 63566 gres/gpu:1 Priority
2443482 yzhao19 60451 gres/gpu:rtx_pro_6000_b:1 Priority
2443481_[9-10] yzhao19 60451 gres/gpu:A100:1,gres/gpumem:75G Priority
2422034 bluitel 60180 N/A DependencyNeverSatisfied
2441592 zhuang5 60049 N/A Dependency
2441591 zhuang5 60049 N/A Dependency
2441590 zhuang5 60049 N/A Dependency
2441589 zhuang5 60049 N/A Dependency
2441588 zhuang5 60049 N/A Dependency
2441587 zhuang5 60049 N/A Dependency
2441597 zhuang5 60036 N/A Dependency
2441596 zhuang5 60036 N/A Dependency
$ squeue -p quick -t PD --sort=-p -o %i %u %Q %b %r
JOBID USER PRIORITY TRES_PER_NODE REASON
2440722 dehalloran 88195 gres/gpu:A100:1 Nodes required for job are DOWN, DRAINED, REBOOTING or reserved for jobs in higher priority partitions
2440504 spatadia 86741 gres/gpu:A100:1 Priority
2441582 zhuang5 64649 gres/gpu:1,gres/gpumem:16G Priority
2441842 sselvaraj 23982 gres/gpu:1 Priority
2441863 sselvaraj 23959 gres/gpu:1 Dependency
2441862 sselvaraj 23959 gres/gpu:1 Dependency
2441861 sselvaraj 23959 gres/gpu:1 Dependency
2441860 sselvaraj 23959 gres/gpu:1 Dependency
2441859 sselvaraj 23959 gres/gpu:1 Dependency
2441858 sselvaraj 23959 gres/gpu:1 Dependency
2441857 sselvaraj 23959 gres/gpu:1 Dependency
2441856 sselvaraj 23959 gres/gpu:1 Dependency
2439893_[0-5,8] tdappenzeller 21522 gres/gpu:rtx_pro_6000_b:1 Priority
2439896_[6-7] tdappenzeller 21519 gres/gpu:rtx_pro_6000_b:1 Priority
2443732 sselvaraj 20828 gres/gpu:1 Priority
2441270 kle6 20565 gres/gpu:1 Priority
2441269 kle6 20565 gres/gpu:1 Priority
2439853 tmondal 20401 gres/gpu:1 Priority
2443726 aakarande 17607 gres/gpu:1 Priority
2439800 aakarande 15994 gres/gpu:1 Priority
2437169 aakarande 15967 gres/gpu:1 Priority
2440949 aakarande 13929 gres/gpu:1 Priority
2443525_[0] aakarande 8074 gres/gpu:1 Priority
$ bash -c squeue -p short -t R -h -o '%b %N' | sort | uniq -c | sort -rn | head -30
     10 N/A compute-2-08
     10 N/A compute-2-07
      9 N/A compute-3-01
      9 N/A compute-2-06
      8 N/A compute-3-02
      7 N/A compute-2-01
      6 N/A compute-3-08
      6 N/A compute-2-03
      5 N/A compute-3-07
      5 N/A compute-3-05
      4 N/A compute-4-08
      4 N/A compute-4-03
      4 N/A compute-3-06
      3 gres/gpu:L40S:1 gpu-5-23
      3 gres/gpu:L40S:1 gpu-5-21
      3 N/A compute-4-05
      3 N/A compute-3-04
      3 N/A compute-3-03
      3 N/A compute-2-05
      2 gres/gpu:4 gpu-5-32
      2 gres/gpu:1 whitehill-0-02
      2 gres/gpu:1 gpu-5-28
      2 N/A compute-4-01
      1 gres/gpu:1,gres/gpumem:80G gpu-6-07
      1 gres/gpu:1 gpu-5-23
      1 gres/gpu:1 gpu-5-21
      1 N/A compute-4-06
      1 N/A compute-4-02
      1 N/A compute-2-02
      1 N/A aswin-02
$ sinfo -p short -N -o %N %G %C %T --noheader
aswin-02 (null) 1/63/0/64 mixed
aswin-03 (null) 0/64/0/64 reserved
aswin-04 (null) 0/64/0/64 reserved
aswin-05 (null) 0/64/0/64 reserved
aswin-06 (null) 0/64/0/64 reserved
aswin-07 (null) 0/64/0/64 reserved
aswin-08 (null) 0/64/0/64 reserved
compute-2-01 (null) 64/0/0/64 allocated
compute-2-02 (null) 52/12/0/64 mixed
compute-2-03 (null) 32/32/0/64 mixed
compute-2-04 (null) 0/0/64/64 drained
compute-2-05 (null) 64/0/0/64 allocated
compute-2-06 (null) 64/0/0/64 allocated
compute-2-07 (null) 64/0/0/64 allocated
compute-2-08 (null) 64/0/0/64 allocated
compute-3-01 (null) 192/0/0/192 allocated
compute-3-02 (null) 192/0/0/192 allocated
compute-3-03 (null) 141/51/0/192 mixed
compute-3-04 (null) 192/0/0/192 allocated
compute-3-05 (null) 192/0/0/192 allocated
compute-3-06 (null) 152/40/0/192 mixed-
compute-3-07 (null) 124/68/0/192 mixed
compute-3-08 (null) 189/3/0/192 mixed
compute-4-01 (null) 128/0/0/128 allocated
compute-4-02 (null) 103/25/0/128 mixed
compute-4-03 (null) 114/14/0/128 mixed
compute-4-05 (null) 103/25/0/128 mixed
compute-4-06 (null) 128/0/0/128 allocated
compute-4-07 (null) 126/2/0/128 mixed
compute-4-08 (null) 90/38/0/128 mixed
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
gpu-5-28 gpu:L40S:4(S:0-1),gpumem:no_consume:48G 20/76/0/96 mixed@
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

## sacct 2443461,2443418

```
$ sacct -P -j 2443461,2443418 --format=JobID,JobName%30,Partition,State,ExitCode,Submit,Start,End,Elapsed,MaxRSS,ReqMem,AllocTRES%60,NodeList
JobID|JobName|Partition|State|ExitCode|Submit|Start|End|Elapsed|MaxRSS|ReqMem|AllocTRES|NodeList
2443418|q_run_d3_sep2023_20m_any|short|RUNNING|0:0|2026-11-01T18:10:56|2026-11-01T19:44:55|Unknown|00:59:11||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443418.batch|batch||RUNNING|0:0|2026-11-01T19:44:55|2026-11-01T19:44:55|Unknown|00:59:11|||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-21
2443461_0|q_d3all_v1_c|short|RUNNING|0:0|2026-11-01T18:41:02|2026-11-01T19:50:28|Unknown|00:53:38||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_0.batch|batch||RUNNING|0:0|2026-11-01T19:50:28|2026-11-01T19:50:28|Unknown|00:53:38|||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-23
2443461_1|q_d3all_v1_c|short|RUNNING|0:0|2026-11-01T18:41:02|2026-11-01T20:06:36|Unknown|00:37:30||160G|billing=8,cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-28
2443461_1.batch|batch||RUNNING|0:0|2026-11-01T20:06:36|2026-11-01T20:06:36|Unknown|00:37:30|||cpu=8,gres/gpu=1,mem=160G,node=1|gpu-5-28
2443461_[2-11%2]|q_d3all_v1_c|short|PENDING|0:0|2026-11-01T18:41:02|Unknown|Unknown|00:00:00||160G||None assigned
```

## work folder d3all_v1/work_d3all_aug2026/run_aug2026_proto_d3all_aug2026

```
not a folder (or name refused): d3all_v1/work_d3all_aug2026/run_aug2026_proto_d3all_aug2026
```

## tail plan_display_2443461_0.out

```
$ ls -la /home/mgeldokla/mass-flood-watch/plan_display_2443461_0.out
-rw-rw-r-- 1 mgeldokla mgeldokla 7881 Nov  1 19:51 /home/mgeldokla/mass-flood-watch/plan_display_2443461_0.out
$ tail -n 25 /home/mgeldokla/mass-flood-watch/plan_display_2443461_0.out
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
Preparing worktree (detached HEAD ebcd9c31)
Updating files:   1% (603/39257)Updating files:   2% (786/39257)Updating files:   3% (1178/39257)Updating files:   3% (1194/39257)Updating files:   4% (1571/39257)Updating files:   4% (1733/39257)Updating files:   5% (1963/39257)Updating files:   6% (2356/39257)Updating files:   6% (2565/39257)Updating files:   7% (2748/39257)Updating files:   8% (3141/39257)Updating files:   8% (3288/3
HEAD is now at ebcd9c31 Turing display runs: short partition on A100 (quick allows one GPU per user, needed by the forecast), 160G, 1-byte depth frames (frames_u8.npz, ARCHITECTURE 4.2 code); QUEUE.md: measured per-user limits (array tasks count one by one)
code ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906 in /home/mgeldokla/scratch/lisflood/code_ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906
plan proto/turing/plans/d3all_v1.json indices: 0 
== task 0: d3all_aug2026 (aug2026) box 128000,856000,206000,946000 hours 30, 671318G free  2026-11-01T19:51:23Z
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
NAME=d3all_aug2026
RES=20
RESULTS_ROOT=d3all_v1
STORM=aug2026
```

## tail plan_display_2443461_1.out

```
$ ls -la /home/mgeldokla/mass-flood-watch/plan_display_2443461_1.out
-rw-rw-r-- 1 mgeldokla mgeldokla 2398 Nov  1 20:06 /home/mgeldokla/mass-flood-watch/plan_display_2443461_1.out
$ tail -n 25 /home/mgeldokla/mass-flood-watch/plan_display_2443461_1.out

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
code ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906 in /home/mgeldokla/scratch/lisflood/code_ebcd9c318eae0fc5f3ce93f3c8e368a0dba54906
plan proto/turing/plans/d3all_v1.json indices: 1 
== task 1: d3all_sep2021 (sep2021) box 128000,856000,206000,946000 hours 36, 671129G free  2026-11-01T20:06:46Z
BOX=128000,856000,206000,946000
HOURS=36
LF_CN_SCALE=0.88
LF_INFIL_MMH=2
LF_LOSS=cn
LF_PARITY=1
LF_QOUT=1
LF_SAVEINT=600
LF_VFRAMES=1
LF_VOUT=1
NAME=d3all_sep2021
RES=20
RESULTS_ROOT=d3all_v1
STORM=sep2021
```

## tail $LF_WORK/d3all_v1/work_d3all_aug2026/w9_log.txt

```
$ tail -n 25 /home/mgeldokla/scratch/lisflood/d3all_v1/work_d3all_aug2026/w9_log.txt
t=107983.000000	dt=1.000000
t=107984.000000	dt=1.000000
t=107985.000000	dt=1.000000
t=107986.000000	dt=1.000000
t=107987.000000	dt=1.000000
t=107988.000000	dt=1.000000
t=107989.000000	dt=1.000000
t=107990.000000	dt=1.000000
t=107991.000000	dt=1.000000
t=107992.000000	dt=1.000000
t=107993.000000	dt=1.000000
t=107994.000000	dt=1.000000
t=107995.000000	dt=1.000000
t=107996.000000	dt=1.000000
t=107997.000000	dt=1.000000
t=107998.000000	dt=1.000000
t=107999.000000	dt=1.000000
Writing snapshot at t=108000.000000
loop time 908.000000
Writing max files

20:10:44 CUDA: t = 0 snapshot replaced by the start file (the initial state), as the CPU build writes it
20:19:25 peak wet (hmax >= 10 cm, land) 55.2 km2; largest snapshot wet area 24.6 km2; 181 snapshots
20:19:25 flux files scaled by 20 (unit-width q from the CUDA solver -> m3/s)
20:31:54 fluxes: 181 snapshots read in 750s; gauge peak flow 01094400 32.5 m3/s (obs 41.1), 01094500 76.0 m3/s (obs 79.6)
```

## tail $LF_WORK/d3all_v1/work_d3all_sep2021/w9_log.txt

```
$ tail -n 25 /home/mgeldokla/scratch/lisflood/d3all_v1/work_d3all_sep2021/w9_log.txt
t=129582.000000	dt=1.000000
t=129583.000000	dt=1.000000
t=129584.000000	dt=1.000000
t=129585.000000	dt=1.000000
t=129586.000000	dt=1.000000
t=129587.000000	dt=1.000000
t=129588.000000	dt=1.000000
t=129589.000000	dt=1.000000
t=129590.000000	dt=1.000000
t=129591.000000	dt=1.000000
t=129592.000000	dt=1.000000
t=129593.000000	dt=1.000000
t=129594.000000	dt=1.000000
t=129595.000000	dt=1.000000
t=129596.000000	dt=1.000000
t=129597.000000	dt=1.000000
t=129598.000000	dt=1.000000
t=129599.000000	dt=1.000000
Writing snapshot at t=129600.000000
loop time 1274.000000
Writing max files

20:33:03 CUDA: t = 0 snapshot replaced by the start file (the initial state), as the CPU build writes it
20:43:23 peak wet (hmax >= 10 cm, land) 199.2 km2; largest snapshot wet area 120.7 km2; 217 snapshots
20:43:23 flux files scaled by 20 (unit-width q from the CUDA solver -> m3/s)
```
