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

PROC_TAGS = ['P1', 'P2', 'P3', 'P4']
SLOT_FREQ = {'P1': 'weekly', 'P2': 'monthly', 'P3': 'quarterly', 'P4': 'annually'}
proc_fields = ['procedure_id','asset_id','description','service_frequency']
proc_descriptions = {
    'pump': ['Pump Inspection', 'Vibration Analysis', 'Instrument Calibration', 'Pump Overhaul'],
    'motor': ['Motor Inspection', 'Bearing Lubrication', 'Motor Alignment', 'Motor Overhaul'],
    'generator': ['Generator Inspection', 'Belt Service', 'Coolant Replacement', 'Generator Overhaul'],
    'transformer': ['Transformer Inspection', 'Oil Level Check', 'Thermal Scan', 'Transformer Overhaul'],
    'boiler': ['Boiler Inspection', 'Sample Water Test', 'Trip Interlocks', 'Boiler Overhaul'],
    'hvac': ['HVAC Inspection', 'Filter Service', 'Line Service', 'HVAC Overhaul']
}

HISTORY_DAYS = 90
serv_hist_fields = ['record_id','procedure_id','date_completed', 'notes']
BEHAVIORS = ['up_to_date', 'overdue', 'never']
BEHAVIOR_WEIGHTS = [60, 30, 10]
FREQ_DAYS = {'weekly': 7, 'monthly': 30, 'quarterly': 90, 'annually': 365}

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

def generate_assets(rng, today):
    counts = plan_counts(rng)
    assets = []
    for n in range(1, counts['PMP'] + 1):
        pump_id = f'PMP-{n:03d}'
        motor_id = f'MTR-{n:03d}'
        assets.append(make_asset(rng, today, 'PMP', n, motor_id))
        assets.append(make_asset(rng, today, 'MTR', n, pump_id))
    for prefix in OTHER_PREFIXES:
        for n in range(1, counts[prefix] + 1):
            assets.append(make_asset(rng, today, prefix, n))

    return assets

def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def generate_procedures(assets):
    procedures = []
    for asset in assets:
        descriptions = proc_descriptions[asset['type']]
        for i, tag in enumerate(PROC_TAGS):
            procedures.append({
                'procedure_id': f"{asset['asset_id']}-{tag}",
                'asset_id': asset['asset_id'],
                'description': descriptions[i],
                'service_frequency': SLOT_FREQ[tag],
            })

    return procedures

def generate_service_history(rng, today, assets, procedures):
    commissioned = {a['asset_id']: datetime.strptime(a['commissioning_date'], DATE_FMT) for a in assets}
    history = []
    record_num = 1
    for proc in procedures:
        behavior = rng.choices(BEHAVIORS, weights=BEHAVIOR_WEIGHTS)[0]
        if behavior == 'never':
            continue
        interval = FREQ_DAYS[proc['service_frequency']]
        start = max(today - timedelta(days=HISTORY_DAYS), commissioned[proc['asset_id']])
        if behavior == 'overdue': end = today - timedelta(days=rng.randint(interval + 5, interval * 2 + 10))
        else: end = today
        current = start + timedelta(days=rng.randint(0, interval - 1))
        while current <= end:
            done = current + timedelta(days=rng.randint(-2, 2))
            done = min(max(done, start), today)
            history.append({
                'record_id': f'SH-{record_num:04d}', 
                'procedure_id': proc['procedure_id'], 
                'date_completed': done.strftime(DATE_FMT), 
                'notes': ''
            })
            record_num += 1
            current += timedelta(days=interval)

    return history

if __name__ == '__main__':
    rng = random.Random(42)
    today = datetime.now()
    assets = generate_assets(rng, today)
    write_csv(OUT_DIR / 'assets.csv', assets, fields)
    print(f'wrote {len(assets)} rows')
    procedures = generate_procedures(assets)
    write_csv(OUT_DIR / 'procedures.csv', procedures, proc_fields)
    print(f'wrote {len(procedures)} procedure rows')
    history = generate_service_history(rng, today, assets, procedures)
    write_csv(OUT_DIR / 'service_history.csv', history, serv_hist_fields)
    print(f'wrote {len(history)} history rows')
