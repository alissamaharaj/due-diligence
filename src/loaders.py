import csv
from datetime import datetime

def load_frequencies(path):
    fqs = dict()

    with open(path) as fh:
        fop = csv.DictReader(fh)

        for row in fop:
            freq = row['service_frequency']
            iv = int(row['service_interval_days'])

            fqs[freq] = iv
    return fqs

DATE_FMT = '%Y-%m-%d'
VALID_STATUS = ['active','under repair','decommissioned']
VALID_TYPE = {'MTR':'motor','PMP':'pump','GEN':'generator','TRN':'transformer','BLR':'boiler','HVC':'hvac'}
fields = ['asset_id','type','description','location','commissioning_date','status']

def load_assets(path):
    asset_ids = set()
    good = list()
    rejected = list()

    with open(path) as fh:
        fop = csv.DictReader(fh)

        for row in fop:
            line_num = fop.line_num
            reason = None
            row_good = True

            for col in fields:
                if row[col].strip() == '': 
                    row_good = False 
                    reason = f'blank {col}'
                    break
            if row_good:
                try: datetime.strptime(row['commissioning_date'], DATE_FMT)
                except ValueError:
                    row_good = False
                    reason = 'invalid commissioning_date'
            if row_good:
                if row['status'].strip() not in VALID_STATUS:
                    row_good = False
                    reason = 'invalid status'
            if row_good:
                id_type = row['asset_id'].split('-')[0]
                if VALID_TYPE.get(id_type) != row['type'].strip():
                    row_good = False
                    reason = 'type does not match id_type' 
            if row_good:
                if row['asset_id'] in asset_ids:
                    row_good = False
                    reason = 'duplicate asset_id'
                else: asset_ids.add(row['asset_id'])

            if row_good: good.append([line_num,row])
            else: rejected.append([line_num,reason,row]) 

    id_row = dict()
    surv_good = list() 

    for line_num,row in good:
        id_row[row['asset_id']] = row

    for line_num,row in good:
        if row['linked_asset_id'].strip() == '':
            row['linked_asset_id'] = None
            surv_good.append([line_num,row])
        elif row['linked_asset_id'] not in id_row:
            rejected.append([line_num,'linked asset not found',row])
        else:
            target = id_row[row['linked_asset_id']]

            if {row['type'], target['type']} != {'motor','pump'}:
                rejected.append([line_num,'link must pair a motor and a pump',row])
            elif target['linked_asset_id'] != row['asset_id']:
                rejected.append([line_num,'link not reciprocated',row])
            else: surv_good.append([line_num,row])

    rejected.sort()
    return surv_good, rejected