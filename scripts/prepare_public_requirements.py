"""Transcribe the visible fictional contact-sheet rules, not evaluation predictions."""
import json
from pathlib import Path

from services.api.schemas import Requirement

scope = 'Demo Threadworks Ltd. / Production Unit A'
source = 'User-supplied contact-sheet.png: fictional buyer checklist; manually transcribed (original JSON not supplied)'
items = []
for buyer, prefix, months, attendance in [('buyer-a', 'A', 6, 20), ('buyer-b', 'B', 12, 25)]:
    specs = [
        ('FIRE', 'Fire drill record', 'fire_drill', f'Fire drill record within previous {months} calendar months; safety officer sign-off required.', {'months': months, 'signatures': ['safety_officer']}),
        ('TRAIN', 'Safety training', 'safety_training', f'Safety training within previous 12 months; at least {attendance} attendees; trainer and safety officer sign-off required.', {'months': 12, 'minimum_value': attendance, 'signatures': ['trainer', 'safety_officer']}),
        ('ELEC', 'Electrical inspection', 'electrical_inspection', 'Electrical inspection certificate must be valid on assessment date; inspector sign-off required.', {'mandatory_fields': ['event_date', 'expiry_date'], 'signatures': ['inspector']}),
        ('COMMITTEE', 'Safety committee minutes', 'worker_committee', 'Safety committee minutes within previous 90 days; management chair sign-off required.' if prefix == 'A' else 'Safety committee minutes within previous 90 days; BOTH management chair and worker representative sign-off required.', {'days': 90, 'signatures': ['management_chair'] + (['worker_representative'] if prefix == 'B' else [])}),
        ('WAGE', 'Wage summary', 'wage_register', 'Wage summary covering 2026-09, 2026-10 and 2026-11 must be available.', {'period_start': '2026-09-01', 'period_end': '2026-11-30'}),
    ]
    for code, title, kind, text, constraints in specs:
        items.append(Requirement(id=f'{prefix}-{code}-01', buyer_id=buyer, title=title, text=text,
                                 evidence_type=kind, scope=scope, source_reference=source, **constraints).model_dump(mode='json'))
Path('datasets/public-demo/requirements/requirements.json').write_text(json.dumps(items, indent=2), encoding='utf-8')
