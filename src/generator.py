import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'data' / 'generated'

DATE_FMT = '%Y-%m-%d'
VALID_STATUS = ['active','under repair','decommissioned']
VALID_TYPE = {'MTR':'motor','PMP':'pump','GEN':'generator','TRN':'transformer','BLR':'boiler','HVC':'hvac'}
locations = ['Boiler Room', 'Pump Room 1', 'Generator Room', 'Substation', 'Rooftop', 'Pump Room 2']
fields = ['asset_id','type','description','location','commissioning_date','status','linked_asset_id']
descriptions = {
    'pump': ['Feedwater Pump', 'Cooling Water Pump', 'Booster Pump', 'Standby Feedwater Pump', 'Transfer Pump'],
    'motor': ['Feedwater Pump Motor', 'Mixer Motor', 'Spare Motor', 'Booster Motor'],
    'generator': ['Diesel Generator', 'Backup Generator', 'Inverter Generator'],
    'transformer': ['Main Transformer', 'Backup Transformer', 'Step-Down Transformer'],
    'boiler': ['Steam Boiler', 'Fire-Tube Boiler'],
    'hvac': ['HVAC Unit', 'Air Handling Unit']
}
OTHER_PREFIXES = ['GEN', 'TRN', 'HVC', 'BLR']

def plan_counts(rng):

    total = rng.randint(30, 40)
    max_pairs = (total - 8) // 2
    n_pairs = rng.randint(8, min(10, max_pairs))
    counts = {'PMP': n_pairs, 'MTR': n_pairs}

    for prefix in OTHER_PREFIXES:
        counts[prefix] = 2

    spare = total - 2 * n_pairs - 8
    
    for _ in range(spare):
        p = rng.choice(OTHER_PREFIXES)
        counts[p] += 1

    return counts

def make_asset(rng, today, prefix, number, linked_id=''):
    asset_id = f'{prefix}-{number:03d}'
    asset_type = VALID_TYPE[prefix]
    dsc = rng.choice(descriptions[asset_type])
    lct = rng.choice(locations)
    days_back = rng.randint(30, 1500)
    cmms = (today - timedelta(days=days_back)).strftime(DATE_FMT)
    status = 'active'

    return {'asset_id': asset_id,'type': asset_type,'description': dsc,'location': lct,'commissioning_date': cmms,'status': status,'linked_asset_id': linked_id}

if __name__ == '__main__':
    print(make_asset(random.Random(1), datetime(2026, 10, 28), 'PMP', 1, 'MTR-001'))
