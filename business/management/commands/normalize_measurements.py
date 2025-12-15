from django.core.management.base import BaseCommand
from django.db import transaction
from business.models import Product
import json
import re

def _normalize_key(k):
    k = str(k).strip().lower().replace(' ', '_')
    if k.startswith('measurement_'):
        k = k[len('measurement_'):]
    d = {
        'len': 'length',
        'length': 'length',
        'chest': 'bust',
        'bust': 'bust',
        'waist': 'waist',
        'hip': 'hips',
        'hips': 'hips',
        'shoulders': 'shoulder',
        'shoulder': 'shoulder',
        'sleeve_length': 'sleeve',
        'sleeve': 'sleeve',
        'arm_hole': 'armhole',
        'armhole': 'armhole',
        'neck_line': 'neckline',
        'neck': 'neckline',
        'neckline': 'neckline',
        'crotch': 'crotch',
        'thigh': 'thigh',
        'knee': 'knee',
        'bottom': 'bottom',
        'leg_opening': 'bottom',
        'hemwidth': 'hem_width',
        'hem_width': 'hem_width'
    }
    return d.get(k, k)

def _extract(desc):
    if not desc or 'Measurements:' not in desc:
        return None, desc
    s = desc.find('Measurements:')
    part = desc[s + len('Measurements:'):].strip()
    pre = desc[:s].strip()
    try:
        data = json.loads(part)
        return data if isinstance(data, dict) else {}, pre
    except json.JSONDecodeError:
        m = re.search(r'\{[\s\S]*\}', part, re.MULTILINE | re.DOTALL)
        if m:
            js = m.group()
            lb = js.rfind('}')
            js = js[:lb+1] if lb != -1 else js
            try:
                data = json.loads(js)
                return data if isinstance(data, dict) else {}, pre
            except json.JSONDecodeError:
                return {}, pre
    return {}, pre

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **opts):
        dry = opts['dry_run']
        total = Product.objects.count()
        processed = 0
        updated = 0
        skipped = 0
        self.stdout.write(f'Processing {total} products...')
        for p in Product.objects.all().iterator():
            measurements, pre = _extract(p.description or '')
            if measurements is None:
                skipped += 1
                continue
            norm = {}
            for k, v in measurements.items():
                nk = _normalize_key(k)
                norm[nk] = (str(v).strip() if v is not None else '')
            processed += 1
            if norm != measurements:
                updated += 1
                block = json.dumps(norm, indent=2)
                new_desc = (pre + '\n\n' if pre else '') + 'Measurements:\n' + block
                if dry:
                    self.stdout.write(f'Would update Product ID {p.id} ({p.name})')
                else:
                    p.description = new_desc
                    p.save(update_fields=['description'])
            else:
                skipped += 1
        self.stdout.write(f'Processed: {processed}, Updated: {updated}, Skipped: {skipped}')
        if dry:
            self.stdout.write('Dry run complete. Re-run without --dry-run to save changes.')