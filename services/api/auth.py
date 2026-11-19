import hashlib
import hmac
import os
import secrets
from datetime import UTC, timedelta

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session as DBSession

from .database import Session, get_db, now


def password_hash(value: str, salt: str | None = None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.scrypt(value.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return salt + ':' + digest


def password_valid(value: str, stored: str):
    return hmac.compare_digest(password_hash(value, stored.split(':')[0]), stored)


def issue_session(db, response: Response, tenant, user_id, role='reviewer', demo=False):
    token = secrets.token_urlsafe(48)
    db.add(Session(id=hashlib.sha256(token.encode()).hexdigest(), tenant=tenant,
                   user_id=user_id, role=role, demo=demo, expires=now() + timedelta(hours=8)))
    db.commit()
    response.set_cookie('fp_session', token, httponly=True, secure=os.getenv('COOKIE_SECURE') == 'true',
                        samesite='strict', max_age=28800, path='/')


def current_session(request: Request, db: DBSession = Depends(get_db)):
    token = request.cookies.get('fp_session', '')
    session = db.get(Session, hashlib.sha256(token.encode()).hexdigest())
    if not session or session.expires.replace(tzinfo=UTC) < now():
        raise HTTPException(401, 'Sign in or open a demonstration workspace.')
    return session


def can_write(session, review=False):
    permitted = {'administrator', 'reviewer'} if review else {'administrator', 'compliance_officer'}
    if session.role not in permitted and not session.demo:
        raise HTTPException(403, 'Your workspace role does not allow this action.')
