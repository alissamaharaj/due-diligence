import csv

def load_frequencies(path):
    fqs = dict()

    with open(path) as fh:
        fop = csv.DictReader(fh)

        for row in fop:
            freq = row['service_frequency']
            iv = int(row['service_interval_days'])

            fqs[freq] = iv
    return fqs