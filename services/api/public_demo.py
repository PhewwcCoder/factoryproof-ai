import json
from pathlib import Path

from .database import Record, uid
from .extraction import extract
from .schemas import Requirement
from .storage import put

ROOT = Path(__file__).resolve().parents[2] / 'datasets' / 'public-demo'


def seed_public(db, tenant):
    for buyer in json.loads((ROOT / 'requirements' / 'buyers.json').read_text(encoding='utf-8')):
        db.add(Record(tenant=tenant, kind='buyer', payload=buyer))
    for raw in json.loads((ROOT / 'requirements' / 'requirements.json').read_text(encoding='utf-8')):
        req = Requirement.model_validate(raw)
        db.add(Record(tenant=tenant, kind='requirement', payload=req.model_dump(mode='json')))
    for path in sorted((ROOT / 'evidence').glob('*.pdf')):
        content = path.read_bytes()
        doc_id = uid()
        key = f'{tenant}/{doc_id}.pdf'
        put(key, content)
        db.add(Record(id=doc_id, tenant=tenant, kind='document', payload={**extract(content, path.name),
                      'name': path.name, 'storage_key': key, 'size': len(content), 'version': 1,
                      'synthetic': True, 'content_type': 'application/pdf'}))
    db.commit()
