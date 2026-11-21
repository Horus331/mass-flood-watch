"""Public FEMA Public Assistance projects (OpenFEMA, no key) for Massachusetts, damage category C (roads and bridges), to see whether a
second road-damage inventory exists in public data. Scouting only: no comparison with any model output.
    python proto/fema_pa.py  ->  papers/paper2/fema_pa_ma.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gw_scout import get
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'papers/paper2/fema_pa_ma.json')
B = 'https://www.fema.gov/api/open/v2/'


def pages(ds, flt, sel=None):
    out, skip = [], 0
    while True:
        u = f"{B}{ds}?$filter={flt}&$top=1000&$skip={skip}" + (f"&$select={sel}" if sel else '')
        r = get(u)
        if r is None or r.status_code != 200: print('fail', ds, r.status_code if r else None); break
        rows = r.json().get(ds, []); out += rows; skip += 1000
        if len(rows) < 1000: break
    return out


def main():
    dec = pages('FemaWebDisasterDeclarations', "stateCode%20eq%20'MA'%20and%20declarationDate%20ge%20'2015-01-01'")
    pa = pages('PublicAssistanceFundedProjectsDetails', "stateAbbreviation%20eq%20'MA'%20and%20damageCategoryCode%20eq%20'C'")
    if not pa: pa = pages('PublicAssistanceFundedProjectsDetails', "stateAbbreviation%20eq%20'MA'")
    keep = [p for p in pa if (p.get('declarationDate') or '') >= '2015']
    json.dump(dict(made_by='proto/fema_pa.py', declarations=[{k: d.get(k) for k in ('disasterNumber', 'declarationDate', 'incidentType', 'declarationTitle', 'incidentBeginDate', 'incidentEndDate')} for d in dec],
                   pa_projects=[{k: p.get(k) for k in ('disasterNumber', 'declarationDate', 'incidentType', 'county', 'applicantName', 'damageCategoryCode', 'damageCategory', 'projectTitle', 'projectAmount', 'federalShareObligated', 'projectSize')} for p in keep]),
              open(OUT, 'w'), indent=1)
    print(len(dec), 'declarations;', len(keep), 'PA projects (MA, since 2015)')
    import collections
    print(collections.Counter((p.get('disasterNumber'), p.get('incidentType'), p.get('damageCategoryCode')) for p in keep).most_common(20))


if __name__ == '__main__':
    main()
