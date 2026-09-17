"""Field-level evidence gate. This validates recorded evidence, not restaurant truth.
Legacy 'official' labels alone are deliberately insufficient for promotion.
"""
from datetime import date
from urllib.parse import urlparse

FIELDS = ('special', 'price', 'schedule', 'location', 'hours')

def evidence_errors(entry):
    audit = entry.get('deal_audit')
    if not audit:
        return ['missing field-level deal audit']
    errors = []
    try:
        date.fromisoformat(audit.get('checked_on', ''))
    except (ValueError, TypeError):
        errors.append('invalid audit date')
    if audit.get('status') not in ('complete', 'partial'):
        errors.append('invalid audit status')
    sources = {s['url'] for s in entry.get('verification', {}).get('sources', [])}
    for name in FIELDS:
        field = audit.get('fields', {}).get(name, {})
        if field.get('status') not in ('verified', 'unknown', 'conflicting'):
            errors.append(f'{name}: missing field status')
        if field.get('status') == 'verified':
            url = field.get('source_url', '')
            if url not in sources or urlparse(url).scheme != 'https':
                errors.append(f'{name}: source must be a registered HTTPS URL')
            if not field.get('quote') or not field.get('value'):
                errors.append(f'{name}: missing evidence excerpt/value')
            if field.get('source_type') not in ('official', 'official_linked_ordering'):
                errors.append(f'{name}: not primary-source evidence')
        if audit.get('status') == 'complete' and field.get('status') != 'verified':
            errors.append(f'{name}: incomplete evidence cannot be complete')
    if audit.get('status') == 'complete':
        ls = entry.get('lunch_special', {})
        if ls.get('price_from') is None or not ls.get('days') or not ls.get('window'):
            errors.append('complete audit requires published price, days and window')
    return errors

def promotion_ready(entry):
    return entry.get('deal_audit', {}).get('status') == 'complete' and not evidence_errors(entry)
