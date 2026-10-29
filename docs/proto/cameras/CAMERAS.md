# Cameras as flood evidence

## USGS stream-gauge cameras (in use)

The USGS National Imagery Management System (NIMS) serves the stills of its stream-gauge cameras through a public API
(`https://api.waterdata.usgs.gov/nims/v0`: `/cameras`, `/listFiles?camId=&after=&before=&rawItem=true`; image URL = the camera's
`smallDir` + file name). No key is needed. A free key from `api.waterdata.usgs.gov/signup` raises the rate limit; it can be set as the repository
secret `API_USGS_PAT`. USGS imagery is public domain, so stills can be stored and shown. Endpoints were taken from the `flowcam` R package
(github.com/connorb/flowcam).

What it gives us:

- **History.** NIMS keeps past images, so the catalogue storms can be checked after the fact, unlike traffic cameras.
- **Timing.** A still every few minutes shows when a stream rose and fell, which checks the model's timing at that point.
- **Road crossings.** Several cameras look at a culvert or bridge on a road, so a still can show the road overtopped.

Limits: few cameras, and they point at streams, not streets. This is supporting evidence for some sites, not a new label source for the
whole district.

Code: `proto/cameras.py` (`list`, `fetch`, `storm`, `catalog`, `sheet`, `upload`). Workflow: `.github/workflows/cameras.yml` (manual).
Every archived storm also gets its stills automatically in `archive_followup.yml` (index in the storm folder, images on the Hugging Face
dataset under `cameras/<storm id>/`). Images are never committed to git.

## MassDOT traffic cameras (needs permission)

MassDOT's road cameras are the better source for water on the road, but they are not open. mass.gov "Highway data for developers" sends
camera access to TrafficLand, which issues a per-user API feed of JPEG stills (one frame per 120 s). There is no archive, so this works
forward only. Access needs a request by Mo (TrafficLand or MassDOT); terms of storage and sharing have to be checked before anything is
kept or published. Until then nothing is collected from these cameras.

When access exists, the plan is: a logger that saves District 3 stills every 2 minutes only while a storm is archived (gate, NWS alert or
flood report), to the HF dataset, plus a manual "water on road: yes / no / can't tell" labelling pass. After enough storms, train a small
image classifier on those labels.
