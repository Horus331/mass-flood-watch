"""Open / update / close GitHub Issues from the latest result of each live workflow (ADR-004; RUNBOOK).

    GH_TOKEN=... GITHUB_REPOSITORY=owner/repo python tools/health_issues.py

Run by sentinel.yml every ~15 min.  Polling, because runs started by the keeper chain are too deep for `workflow_run` events to fire
(found 11 Nov 2026: failure_issue.yml never saw keeper-started runs).  One open Issue per workflow, title "Failing: <workflow name>";
each new failed run adds one comment; the next successful run closes it.  Cancelled / skipped runs are ignored.
"""
import json, os, subprocess, sys

WATCH = ['sentinel.yml', 'forecast.yml', 'live_feeds.yml', 'keeper.yml', 'archive_followup.yml', 'events_log.yml', 'storm_watch.yml']
REPO = os.environ.get('GITHUB_REPOSITORY', 'Horus331/mass-flood-watch')


def gh(*a, data=None):
    r = subprocess.run(['gh', 'api', *a], capture_output=True, text=True, timeout=60)
    if r.returncode: raise RuntimeError(r.stderr.strip()[:300])
    return json.loads(r.stdout) if r.stdout.strip() else None


def main():
    issues = [i for i in gh(f'repos/{REPO}/issues?state=open&per_page=100') if 'pull_request' not in i and i['title'].startswith('Failing: ')]
    bad = 0
    for wf in WATCH:
        try: runs = gh(f'repos/{REPO}/actions/workflows/{wf}/runs?status=completed&per_page=10')['workflow_runs']
        except Exception as e: print(wf, 'not readable:', e); continue
        runs = [r for r in runs if r['conclusion'] in ('success', 'failure', 'timed_out', 'startup_failure')]
        if not runs: continue
        r = runs[0]; name = r['name']; title = f'Failing: {name}'; iss = next((i for i in issues if i['title'] == title), None)
        if r['conclusion'] == 'success':
            if iss:
                gh(f"repos/{REPO}/issues/{iss['number']}/comments", '-f', f"body=Recovered: succeeded {r['updated_at']} ({r['html_url']}). Closing.")
                gh('-X', 'PATCH', f"repos/{REPO}/issues/{iss['number']}", '-f', 'state=closed'); print(wf, 'recovered, closed', iss['number'])
            continue
        bad += 1
        if not iss:
            body = (f"The workflow **{name}** failed ({r['conclusion']}) at {r['updated_at']}.\n\nRun: {r['html_url']}\n\n"
                    "Opened automatically by tools/health_issues.py (sentinel). It closes itself on the next successful run. What to check: docs/RUNBOOK.md.")
            n = gh(f'repos/{REPO}/issues', '-f', f'title={title}', '-f', f'body={body}')['number']; print(wf, 'opened', n)
        else:
            seen = iss['body'] or ''
            for c in gh(f"repos/{REPO}/issues/{iss['number']}/comments?per_page=100"): seen += c['body']
            if r['html_url'] not in seen:
                gh(f"repos/{REPO}/issues/{iss['number']}/comments", '-f', f"body=Failed again {r['updated_at']}: {r['html_url']}"); print(wf, 'commented', iss['number'])
    print('failing workflows:', bad)


if __name__ == '__main__':
    main()
