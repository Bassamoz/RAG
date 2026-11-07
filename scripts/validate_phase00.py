"""Check archived phase-00 checkpoint and planning artifacts, not current application readiness."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import platform
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

def validate(root):
    errors = []
    def check(condition, message):
        if not condition:
            errors.append(message)
    required = ['PROJECT_BRIEF.md', 'RESEARCH_ALIGNMENT.md', 'REQUIREMENTS_TRACEABILITY.md',
                'SCREEN_MAP.md', 'ROLE_PERMISSIONS.md', 'ARCHITECTURE.md', 'THREAT_MODEL.md',
                'TESTING.md', 'EXTERNAL_DEPENDENCIES.md', 'ACCEPTANCE_BUDGETS.md',
                'PROJECT_STATE.json', 'NEXT_ACTIONS.md', 'IMPLEMENTATION_EXPLAINED_AR.md',
                'phase-reports/00_research_and_plan.md', 'IMPLEMENTATION_PLAN.md']
    for name in required:
        check((root/'docs'/name).is_file(), f'Missing artifact: {name}')
    original = (root/'codex-plan/REQUIREMENTS.md').read_text(encoding='utf-8')
    trace = (root/'docs/REQUIREMENTS_TRACEABILITY.md').read_text(encoding='utf-8')
    expected = re.findall(r'^\| (R\d{2}) \|', original, re.M)
    actual = re.findall(r'^\| (R\d{2}) \|', trace, re.M)
    check(len(actual)==48 and set(actual)==set(expected), 'Requirement set missing or duplicated')
    for line in original.splitlines():
        if re.match(r'\| R\d\d \|', line):
            rid, meaning, owner, acceptance = [x.strip() for x in line.strip('|').split('|')]
            matches = [x for x in trace.splitlines() if x.startswith(f'| {rid} |')]
            check(len(matches)==1 and all(x in matches[0] for x in [meaning,owner,acceptance,f'T-{rid}']), f'Meaning/owner/test changed: {rid}')
    state = json.loads((root/'docs/evidence/phase-00/planning-state.json').read_text(encoding='utf-8'))
    phases = state['phases']
    check([p['id'] for p in phases]==[f'{i:02}' for i in range(19)], 'Phases must be ordered 00–18')
    check(phases[0]['status'] in {'implemented','verified_local'}, 'Phase 00 missing evidence status')
    check(all(p['status']=='planned' for p in phases[1:]), 'Later phase was incorrectly advanced')
    check(not any(state['delivery'].values()), 'Planning must not assert application readiness')
    check(state['completed_requirements']==['R01'], 'Cross-phase requirements incorrectly completed')
    check({'R02','R44','R47'}==set(state['partial_requirements']), 'Missing ongoing obligations')
    check(len(list((root/'docs/adr').glob('*.md')))==6, 'Expected six architectural decisions')
    architecture=(root/'docs/ARCHITECTURE.md').read_text(encoding='utf-8')
    check(architecture.count('```mermaid')==8, 'Expected eight design diagrams')
    manifest=json.loads((root/'codex-plan/MANIFEST.json').read_text(encoding='utf-8'))
    check(hashlib.sha256((root/'codex-plan/references/research.pdf').read_bytes()).hexdigest()==manifest['source_pdf']['sha256'], 'Research source changed')
    check((root/'y.py').stat().st_size==0, 'Existing empty file changed')
    for page in [48,52,53,56,64,87,99,102]:
        check((root/f'docs/evidence/phase-00/page-{page}.png').is_file(), f'Missing PDF visual evidence {page}')
    return errors

if __name__=='__main__':
    errors=validate(ROOT)
    # Preserve the original accepted evidence; later checkpoint checks have a separate artifact.
    output=ROOT/'docs/evidence/phase-00/validation-latest.json'
    record={'command':'python -X utf8 scripts/validate_phase00.py','exit_code':int(bool(errors)),
            'time':datetime.now(timezone.utc).isoformat(),'environment':f'{platform.system()} {platform.release()}; Python {platform.python_version()}',
            'commit':None,'scope':'documentation integrity only; no application/provider tests',
            'errors':errors,'result':'failed' if errors else 'passed',
            'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False,indent=2))
    sys.exit(record['exit_code'])
