import hashlib
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import UTC, date

from fastapi import (
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Request,
    Response,
    UploadFile,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession

from . import storage
from .auth import can_write, current_session, issue_session, password_valid
from .database import (
    Base,
    Record,
    Session,
    SessionLocal,
    User,
    engine,
    get_db,
    now,
    records,
    serialize,
    uid,
)
from .engine import verify
from .extraction import extract
from .public_demo import seed_public
from .retrieval import rank
from .schemas import BuyerInput, LoginInput, Requirement, ReviewInput, RunInput

logger = logging.getLogger('factoryproof')
logging.basicConfig(level=logging.INFO)
rate_buckets = {}


@asynccontextmanager
async def lifespan(app):
    # Production schema changes are performed by Alembic, not application startup.
    if os.getenv('AUTO_CREATE_SCHEMA', 'true') == 'true':
        Base.metadata.create_all(engine)
    yield


app = FastAPI(title='FactoryProof evidence API', version='0.1.0', lifespan=lifespan,
              docs_url='/api/openapi', openapi_url='/api/openapi.json')


@app.middleware('http')
async def boundaries(request: Request, call_next):
    started = time.perf_counter()
    origin = request.headers.get('origin')
    if request.method not in {'GET', 'HEAD', 'OPTIONS'} and origin and origin != os.getenv('APP_ORIGIN', 'http://localhost:3000'):
        return JSONResponse({'detail': 'Untrusted request origin.'}, status_code=403)
    if request.method == 'POST' and request.url.path.startswith('/api/auth/'):
        key = request.client.host if request.client else 'unknown'
        bucket = int(time.time() // 60)
        # Bound memory; production multi-worker deployment needs a shared limiter.
        for old_key in list(rate_buckets):
            if rate_buckets[old_key][0] != bucket:
                del rate_buckets[old_key]
        previous, count = rate_buckets.get(key, (bucket, 0))
        count = count + 1 if previous == bucket else 1
        rate_buckets[key] = (bucket, count)
        if count > 20:
            return JSONResponse({'detail': 'Too many attempts. Try again in one minute.'}, status_code=429)
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    logger.info(json.dumps({'path': request.url.path, 'status': response.status_code,
                            'latency_ms': round((time.perf_counter() - started) * 1000, 2)}))
    return response


def owned(db, session, record_id, kind=None):
    record = db.query(Record).filter_by(id=record_id, tenant=session.tenant).first()
    if not record or kind and record.kind != kind:
        raise HTTPException(404, 'Record not found in this workspace.')
    return record


def audit(db, session, action, subject):
    db.add(Record(tenant=session.tenant, kind='audit', payload={'actor': session.user_id, 'action': action, 'subject': subject}))


def document_view(record):
    data = serialize(record)
    data.pop('storage_key', None)
    return data


def reconcile(db, tenant, reference):
    docs = [document_view(d) for d in records(db, tenant, 'document')]
    findings = []
    for row in records(db, tenant, 'requirement'):
        req = Requirement.model_validate(row.payload)
        candidates = rank(req.text + ' ' + req.evidence_type.replace('_', ' '), docs, req.evidence_type)
        outcomes = [(verify(req, c['document'], reference), c) for c in candidates]
        priority = {'SUPPORTED': 0, 'INSUFFICIENT': 1, 'NEEDS_REVIEW': 2, 'MISSING': 3}
        outcomes.sort(key=lambda item: (priority[item[0]['status']], -item[1]['score']))
        outcome, candidate = outcomes[0] if outcomes else (verify(req, None, reference), None)
        findings.append({**outcome, 'id': uid(), 'requirement': req.model_dump(mode='json'),
                         'document_name': candidate['document']['name'] if candidate else None,
                         'retrieval': [{k: v for k, v in c.items() if k != 'document'} | {'document_id': c['document']['id']} for c in candidates[:5]],
                         'review': None})
    run = Record(tenant=tenant, kind='run', payload={'reference_date': reference.isoformat(), 'findings': findings})
    db.add(run)
    db.commit()
    return serialize(run)


@app.get('/api/health')
def health():
    return {'status': 'ok', 'version': '0.1.0'}


@app.post('/api/auth/demo')
def demo(request: Request, response: Response, db: DBSession = Depends(get_db)):
    if os.getenv('DEMO_ENABLED', 'true') != 'true':
        raise HTTPException(403, 'Demonstration access is disabled.')
    existing = db.get(Session, hashlib.sha256(request.cookies.get('fp_session', '').encode()).hexdigest())
    if existing and existing.expires.replace(tzinfo=UTC) > now():
        return {'ok': True}
    tenant = 'demo-' + uid()
    seed_public(db, tenant)
    issue_session(db, response, tenant, 'demo-reviewer', demo=True)
    return {'ok': True}


@app.post('/api/auth/reset-demo')
def reset_demo(response: Response, session=Depends(current_session), db: DBSession = Depends(get_db)):
    if not session.demo:
        raise HTTPException(403, 'Only demonstration workspaces can be reset.')
    tenant = 'demo-' + uid()
    seed_public(db, tenant)
    db.delete(session)
    issue_session(db, response, tenant, 'demo-reviewer', demo=True)
    return {'ok': True}


@app.post('/api/auth/login')
def login(body: LoginInput, response: Response, db: DBSession = Depends(get_db)):
    user = db.query(User).filter_by(email=body.email.strip().lower()).first()
    if not user or not password_valid(body.password, user.password):
        raise HTTPException(401, 'Email or password is incorrect.')
    issue_session(db, response, user.tenant, user.id, user.role)
    return {'ok': True}


@app.post('/api/auth/logout')
def logout(response: Response, session=Depends(current_session), db: DBSession = Depends(get_db)):
    db.delete(session)
    db.commit()
    response.delete_cookie('fp_session', path='/')
    return {'ok': True}


@app.get('/api/workspace')
def workspace(session=Depends(current_session), db: DBSession = Depends(get_db)):
    return {'name': 'Demo Threadworks Ltd.' if session.demo else 'Factory workspace',
            'demo': session.demo, 'role': session.role, 'user': session.user_id,
            'buyers': [serialize(b) for b in records(db, session.tenant, 'buyer')],
            'requirements': [serialize(r) for r in records(db, session.tenant, 'requirement')],
            'documents': [document_view(d) for d in records(db, session.tenant, 'document')],
            'run': serialize(runs[-1]) if (runs := records(db, session.tenant, 'run')) else None,
            'audit': [serialize(a) for a in records(db, session.tenant, 'audit')][-20:]}


@app.post('/api/buyers')
def add_buyer(body: BuyerInput, session=Depends(current_session), db: DBSession = Depends(get_db)):
    can_write(session)
    key = uid()
    buyer = Record(tenant=session.tenant, kind='buyer', payload={'key': key, 'name': body.name,
                   'initials': ''.join(word[0] for word in body.name.split())[:2], 'fictional': session.demo})
    db.add(buyer)
    audit(db, session, 'buyer.created', key)
    db.commit()
    return serialize(buyer)


@app.post('/api/requirements')
def add_requirement(body: Requirement, session=Depends(current_session), db: DBSession = Depends(get_db)):
    can_write(session)
    if body.buyer_id not in [b.payload['key'] for b in records(db, session.tenant, 'buyer')]:
        raise HTTPException(422, 'Select a buyer in this workspace.')
    record = Record(tenant=session.tenant, kind='requirement', payload=body.model_dump(mode='json'))
    db.add(record)
    audit(db, session, 'requirement.created', body.title)
    db.commit()
    return serialize(record)


@app.put('/api/requirements/{record_id}')
def update_requirement(record_id: str, body: Requirement, session=Depends(current_session), db: DBSession = Depends(get_db)):
    can_write(session)
    record = owned(db, session, record_id, 'requirement')
    if body.buyer_id != record.payload['buyer_id']:
        raise HTTPException(422, 'Buyer cannot be changed on an existing requirement.')
    db.add(Record(tenant=session.tenant, kind='requirement_history', payload={'record_id': record.id, 'previous': record.payload}))
    record.payload = {**body.model_dump(mode='json'), 'version': record.payload['version'] + 1}
    audit(db, session, 'requirement.updated', record.id)
    db.commit()
    return serialize(record)


def process_document(record_id, tenant):
    with SessionLocal() as db:
        record = db.query(Record).filter_by(id=record_id, tenant=tenant, kind='document').one()
        start = time.perf_counter()
        try:
            result = extract(storage.get(record.payload['storage_key']), record.payload['name'])
            record.payload = {**record.payload, **result, 'latency_ms': round((time.perf_counter() - start) * 1000, 2)}
        except Exception:
            logger.exception('Document processing failed for %s', record_id)
            record.payload = {**record.payload, 'processing_status': 'error', 'message': 'Extraction failed. Use an unlocked, valid PDF or UTF-8 text file.'}
        db.commit()


@app.post('/api/documents')
async def upload(file: UploadFile, background: BackgroundTasks, session=Depends(current_session), db: DBSession = Depends(get_db)):
    can_write(session)
    if len(records(db, session.tenant, 'document')) >= 100:
        raise HTTPException(413, 'Workspace limit of 100 documents reached.')
    name = (file.filename or 'document').replace('\\', '/').split('/')[-1][:180]
    if not name.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(415, 'Upload a PDF or UTF-8 .txt document.')
    content = await file.read(10 * 1024 * 1024 + 1)
    if not content or len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, 'Choose a nonempty document no larger than 10 MB.')
    if name.lower().endswith('.pdf') and not content.startswith(b'%PDF-'):
        raise HTTPException(415, 'The file does not contain a PDF.')
    if name.lower().endswith('.txt'):
        try:
            content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(415, 'Text files must use UTF-8 encoding.') from None
    doc_id = uid()
    key = f'{session.tenant}/{doc_id}'
    storage.put(key, content)
    previous = [d for d in records(db, session.tenant, 'document') if d.payload['name'] == name]
    record = Record(id=doc_id, tenant=session.tenant, kind='document', payload={'name': name, 'storage_key': key,
                    'size': len(content), 'version': len(previous) + 1, 'synthetic': False,
                    'content_type': 'application/pdf' if name.lower().endswith('.pdf') else 'text/plain',
                    'processing_status': 'processing', 'facts': {}, 'citations': {}, 'pages': [], 'conflicts': []})
    db.add(record)
    audit(db, session, 'document.uploaded', doc_id)
    db.commit()
    background.add_task(process_document, doc_id, session.tenant)
    return document_view(record)


@app.post('/api/documents/{record_id}/process')
def reprocess(record_id: str, background: BackgroundTasks, session=Depends(current_session), db: DBSession = Depends(get_db)):
    can_write(session)
    record = owned(db, session, record_id, 'document')
    record.payload = {**record.payload, 'processing_status': 'processing'}
    db.commit()
    background.add_task(process_document, record_id, session.tenant)
    return {'ok': True}


@app.get('/api/documents/{record_id}/file')
def download(record_id: str, session=Depends(current_session), db: DBSession = Depends(get_db)):
    record = owned(db, session, record_id, 'document')
    return Response(storage.get(record.payload['storage_key']), media_type=record.payload['content_type'],
                    headers={'Content-Disposition': 'inline', 'Content-Security-Policy': "sandbox; default-src 'none'"})


@app.get('/api/search')
def search(q: str, session=Depends(current_session), db: DBSession = Depends(get_db)):
    if len(q) > 500:
        raise HTTPException(422, 'Search must be shorter than 500 characters.')
    docs = [document_view(d) for d in records(db, session.tenant, 'document')]
    return rank(q, docs)[:20]


@app.post('/api/runs')
def run(body: RunInput, session=Depends(current_session), db: DBSession = Depends(get_db)):
    can_write(session)
    if session.demo:
        body.reference_date = date(2026, 12, 26)
        recent = records(db, session.tenant, 'run')
        if len(recent) >= 30:
            raise HTTPException(429, 'Demo limit reached. Reset the demonstration to start again.')
    # Re-read the stored originals on every requested run, never fixture facts.
    for document in records(db, session.tenant, 'document'):
        process_document(document.id, session.tenant)
    db.expire_all()
    audit(db, session, 'verification.started', body.reference_date.isoformat())
    return reconcile(db, session.tenant, body.reference_date)


@app.post('/api/runs/{run_id}/findings/{finding_id}/review')
def review(run_id: str, finding_id: str, body: ReviewInput, session=Depends(current_session), db: DBSession = Depends(get_db)):
    can_write(session, review=True)
    run = owned(db, session, run_id, 'run')
    payload = json.loads(json.dumps(run.payload))
    finding = next((f for f in payload['findings'] if f['id'] == finding_id), None)
    if not finding:
        raise HTTPException(404, 'Finding not found.')
    finding['review'] = {**body.model_dump(), 'reviewer': session.user_id, 'at': now().isoformat()}
    run.payload = payload
    audit(db, session, 'finding.' + body.decision, {'finding_id': finding_id, 'note': body.note})
    db.commit()
    return finding


@app.get('/api/runs/{run_id}/report')
def report(run_id: str, buyer: str, final: bool = False, session=Depends(current_session), db: DBSession = Depends(get_db)):
    run = owned(db, session, run_id, 'run')
    findings = [f for f in run.payload['findings'] if f['requirement']['buyer_id'] == buyer]
    if not findings:
        raise HTTPException(404, 'Buyer findings not found.')
    if final:
        can_write(session, review=True)
        if any(not f['review'] or f['review']['decision'] != 'approved' for f in findings):
            raise HTTPException(409, 'Every included finding needs reviewer approval before final export.')
    lines = ['# FactoryProof evidence preparation report', '',
             'SYNTHETIC DEMONSTRATION' if session.demo else 'Private factory workspace',
             'REVIEWED' if final else 'DRAFT - human review pending',
             'This report is not compliance certification.', f"Reference date: {run.payload['reference_date']}", '']
    for f in findings:
        lines += [f"## {f['requirement']['title']}: {f['status']}",
                  f"Rule source: {f['requirement']['source_reference']}; version {f['requirement']['version']}",
                  f"Evidence: {f['document_name'] or 'Missing'}", f"Review: {json.dumps(f['review'])}"]
        for c in f['checks']:
            lines.append(f"- {c['status']}: {c['reason']}")
            if c['citation']:
                lines.append(f"  Source page {c['citation']['page']}: {c['citation']['quote']}")
        if f['document_id']:
            lines.append(f"  [Open original](/api/documents/{f['document_id']}/file)")
        lines.append('')
    audit(db, session, 'report.exported', {'run': run_id, 'buyer': buyer, 'final': final})
    db.commit()
    return Response('\n'.join(lines), media_type='text/markdown', headers={'Content-Disposition': 'attachment; filename="factoryproof-report.md"'})
