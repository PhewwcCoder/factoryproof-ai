from io import BytesIO
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from .database import Record, uid
from .extraction import extract
from .schemas import Requirement
from .storage import put

BUYERS = [('northstar', 'Northstar Apparel', 'NA'), ('loom', 'Loom & Field', 'LF')]
TOPICS = [('fire_drill', 'Fire drill record'), ('fire_certificate', 'Fire safety certificate'),
          ('electrical_inspection', 'Electrical inspection'), ('safety_training', 'Safety training'),
          ('wage_register', 'Wage register'), ('water_test', 'Drinking water test'),
          ('building_inspection', 'Building inspection'), ('worker_committee', 'Worker committee minutes')]


def requirements():
    result = []
    for buyer, _, _ in BUYERS:
        for kind, title in TOPICS:
            months = 6 if buyer == 'northstar' else 12
            r = Requirement(id=f'{buyer}-{kind}', buyer_id=buyer, title=title,
                            text=f'{title} covering the entire factory, dated within {months} months.',
                            evidence_type=kind, months=months)
            if kind == 'fire_certificate':
                r.mandatory_fields.append('expiry_date')
            if kind in {'fire_drill', 'safety_training'}:
                r.signatures = ['safety_officer']
            if kind == 'electrical_inspection':
                r.minimum_frequency = 4 if buyer == 'northstar' else 2
            if kind == 'water_test':
                r.minimum_value = 95
            if kind == 'wage_register':
                from datetime import date
                r.period_start, r.period_end = date(2026, 9, 1), date(2026, 9, 30)
            result.append(r)
    return result


def fixtures():
    docs = [
        ('Fire drill - March 2026', 'fire_drill', '2026-03-01', {'signatures': 'safety_officer'}),
        ('Fire safety certificate', 'fire_certificate', '2026-01-10', {'expiry_date': '2026-09-30'}),
        ('Electrical inspection - Q3', 'electrical_inspection', '2026-09-18', {'frequency': '2'}),
        ('Safety training attendance', 'safety_training', '2026-10-05', {}),
        ('September wage register', 'wage_register', '2026-10-02', {'period_start': '2026-09-01', 'period_end': '2026-09-30'}),
        ('Drinking water laboratory test', 'water_test', '2026-10-12', {'value': '98'}),
        ('Building inspection - disputed', 'building_inspection', '2026-08-15', {'conflicting_date': '2027-08-15'}),
        ('Machine maintenance log', 'machine_maintenance', '2026-10-10', {}),
        ('First aid inventory', 'first_aid', '2026-10-14', {}),
        ('Evacuation route inspection', 'evacuation_routes', '2026-09-20', {}),
        ('Waste transfer manifest', 'waste_manifest', '2026-09-28', {}),
        ('Chemical inventory', 'chemical_inventory', '2026-10-01', {}),
        ('Overtime register', 'overtime_register', '2026-10-02', {}),
        ('PPE distribution record', 'ppe_distribution', '2026-10-06', {}),
        ('Boiler inspection certificate', 'boiler_inspection', '2026-09-01', {'expiry_date': '2027-09-01'}),
    ]
    for name, kind, event, extra in docs:
        lines = [f'evidence_type: {kind}', f'event_date: {event}', 'scope: entire_factory',
                 'factory_id: DEMO-001', 'issuing_authority: Synthetic training dataset']
        lines += [f"{'event_date' if key == 'conflicting_date' else key}: {value}" for key, value in extra.items()]
        yield name, lines


def make_pdf(name, lines):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595, 842))
    c.setTitle(name)
    c.setFillColor(HexColor('#173c40'))
    c.rect(0, 752, 595, 90, fill=1, stroke=0)
    c.setFillColor(HexColor('#ffffff'))
    c.setFont('Helvetica-Bold', 19)
    c.drawString(45, 797, 'FACTORYPROOF / EVIDENCE RECORD')
    c.setFont('Helvetica', 10)
    c.drawString(45, 775, 'SYNTHETIC DOCUMENT - FICTIONAL FACTORY - NOT AN AUDIT RECORD')
    c.setFillColor(HexColor('#172b3a'))
    c.setFont('Helvetica-Bold', 20)
    c.drawString(45, 710, name)
    c.setFont('Helvetica', 12)
    for i, line in enumerate(lines):
        c.drawString(45, 659 - i * 29, line)
    c.setStrokeColor(HexColor('#c8d6d1'))
    c.line(45, 180, 550, 180)
    c.setFont('Helvetica', 10)
    c.drawString(45, 155, 'Created for reproducible software evaluation. All rules and records are fictional.')
    c.drawString(45, 135, 'Reference date: 2026-11-01. Field text above is the source of extracted facts.')
    c.drawString(45, 60, 'FactoryProof AI / Demonstration dataset')
    c.drawRightString(550, 60, 'Page 1 of 1')
    c.showPage()
    c.save()
    return buffer.getvalue()


def seed(db, tenant):
    for key, name, initials in BUYERS:
        db.add(Record(tenant=tenant, kind='buyer', payload={'key': key, 'name': name, 'initials': initials, 'fictional': True}))
    for req in requirements():
        db.add(Record(tenant=tenant, kind='requirement', payload=req.model_dump(mode='json')))
    for name, lines in fixtures():
        doc_id = uid()
        content = make_pdf(name, lines)
        key = f'{tenant}/{doc_id}.pdf'
        put(key, content)
        payload = {**extract(content, name + '.pdf'), 'name': name + '.pdf', 'storage_key': key,
                   'size': len(content), 'version': 1, 'synthetic': True, 'content_type': 'application/pdf'}
        db.add(Record(id=doc_id, tenant=tenant, kind='document', payload=payload))
    db.commit()


if __name__ == '__main__':
    folder = Path('datasets/synthetic')
    folder.mkdir(parents=True, exist_ok=True)
    for name, lines in fixtures():
        (folder / (name.lower().replace(' ', '-') + '.pdf')).write_bytes(make_pdf(name, lines))
