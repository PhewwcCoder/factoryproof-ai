"""Pure reproducible rules. Candidate ranking never grants support."""
import calendar
from datetime import date

from .schemas import Requirement


def months_before(value: date, months: int) -> date:
    index = value.year * 12 + value.month - 1 - months
    year, month = divmod(index, 12)
    return date(year, month + 1, min(value.day, calendar.monthrange(year, month + 1)[1]))


def verify(req: Requirement, evidence: dict | None, reference: date) -> dict:
    checks = []

    def check(rule, status, reason, field=None):
        citation = evidence.get('citations', {}).get(field) if evidence and field else None
        checks.append(dict(rule=rule, status=status, reason=reason, citation=citation))

    if evidence is None:
        check('evidence', 'MISSING', 'No relevant evidence was found.')
    else:
        facts = evidence.get('facts', {})
        if evidence.get('processing_status') != 'ready':
            check('extraction', 'NEEDS_REVIEW', 'Extraction is incomplete; inspect the original.')
        if facts.get('evidence_type') != req.evidence_type:
            check('type', 'INSUFFICIENT', 'Document type does not match the required evidence.', 'evidence_type')
        else:
            check('type', 'SUPPORTED', f"Document type: {req.evidence_type.replace('_', ' ')}.", 'evidence_type')
        for field in set(req.mandatory_fields + ['scope']):
            if facts.get(field) in (None, '', []):
                check(field, 'NEEDS_REVIEW', f"Missing {field.replace('_', ' ')}; a reviewer must resolve it.")
        if facts.get('scope') and facts['scope'] != req.scope:
            check('scope', 'INSUFFICIENT', f"Scope is {facts['scope']}; required {req.scope}.", 'scope')
        elif facts.get('scope'):
            check('scope', 'SUPPORTED', 'Evidence covers the required scope.', 'scope')
        if evidence.get('conflicts'):
            check('conflict', 'NEEDS_REVIEW', 'Conflicting source values: ' + ', '.join(evidence['conflicts']))
        event = None
        for field in ['event_date', 'expiry_date', 'period_start', 'period_end']:
            value = facts.get(field)
            if value:
                try:
                    parsed = date.fromisoformat(value)
                except (ValueError, TypeError):
                    check(field, 'NEEDS_REVIEW', f'Invalid {field} in source.', field)
                    continue
                if field == 'event_date':
                    event = parsed
                    if parsed > reference:
                        check('date', 'NEEDS_REVIEW', 'Event date is after the evaluation date.', field)
                    elif req.months:
                        cutoff = months_before(reference, req.months)
                        accepted = parsed >= cutoff
                        check('date_window', 'SUPPORTED' if accepted else 'INSUFFICIENT',
                              f"{parsed.isoformat()} {'falls within' if accepted else 'is outside'} the {req.months}-month window (from {cutoff.isoformat()}).", field)
                if field == 'expiry_date':
                    check('expiry', 'SUPPORTED' if parsed >= reference else 'INSUFFICIENT',
                          f'Valid until {parsed.isoformat()}; evaluated on {reference.isoformat()}.', field)
        if req.months and not facts.get('event_date') and 'event_date' not in req.mandatory_fields:
            check('date_window', 'NEEDS_REVIEW', 'No event date to verify the date window.')
        if event and facts.get('expiry_date'):
            try:
                if date.fromisoformat(facts['expiry_date']) < event:
                    check('chronology', 'NEEDS_REVIEW', 'Expiry date precedes the issue/event date.', 'expiry_date')
            except ValueError:
                pass
        for signature in req.signatures:
            present = signature.lower() in [s.lower() for s in facts.get('signatures', [])]
            check('signature', 'SUPPORTED' if present else 'INSUFFICIENT',
                  f"Required {signature} signature {'recorded' if present else 'not recorded'}.", 'signatures')
        for field, threshold in [('frequency', req.minimum_frequency), ('value', req.minimum_value)]:
            if threshold is not None:
                value = facts.get(field)
                if value is None:
                    check(field, 'NEEDS_REVIEW', f'No {field} value available.')
                else:
                    check(field, 'SUPPORTED' if value >= threshold else 'INSUFFICIENT',
                          f'Recorded {field}: {value}; required at least {threshold}.', field)
        for field, required in [('period_start', req.period_start), ('period_end', req.period_end)]:
            if required:
                value = facts.get(field)
                try:
                    actual = date.fromisoformat(value)
                    accepted = actual <= required if field == 'period_start' else actual >= required
                    check(field, 'SUPPORTED' if accepted else 'INSUFFICIENT', f'Recorded {field}: {value}; required {required}.', field)
                except (ValueError, TypeError):
                    check(field, 'NEEDS_REVIEW', f'Missing or invalid {field}.')
    statuses = {c['status'] for c in checks}
    status = next((s for s in ['MISSING', 'NEEDS_REVIEW', 'INSUFFICIENT'] if s in statuses), 'SUPPORTED')
    return {'status': status, 'checks': checks, 'reference_date': reference.isoformat(),
            'requirement_id': req.id, 'document_id': evidence.get('id') if evidence else None}
