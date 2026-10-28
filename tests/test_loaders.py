import unittest
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / 'src'
DATA_DIR = ROOT / 'data'

sys.path.append(str(SRC_DIR))

from loaders import load_frequencies , load_assets , load_procedures , load_service_history , DATE_FMT

class SharedSetup(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.frequencies = load_frequencies(DATA_DIR / 'frequencies.csv')
        self.good_assets, self.rejected_assets = load_assets(DATA_DIR / 'assets.csv')
        self.valid_asset_ids = {row['asset_id'] for line_num, row in self.good_assets}

class TestFrequencies(unittest.TestCase):

    def test_load_frequencies(self):
        result = load_frequencies(DATA_DIR/ 'frequencies.csv')
        self.assertEqual(result, {'weekly':7,'monthly':30,'quarterly':90,'annually':365})

class TestAssets(unittest.TestCase):

    def test_load_assets(self):
        good, rejected = load_assets(DATA_DIR/ 'assets.csv')

        self.assertEqual(len(good), 7)
        self.assertEqual(len(rejected), 8)
        rsns = {line_num: reason for line_num, reason, row in rejected}
        self.assertEqual(rsns, {9: 'blank location', 10: 'invalid commissioning_date', 11: 'duplicate asset_id', 12: 'invalid status', 13: 'linked asset not found', 14: 'type does not match id_type', 15: 'link must pair a motor and a pump', 16: 'link not reciprocated'})

class TestProcedures(SharedSetup):

    def test_load_procedures(self):
        good, rejected = load_procedures(DATA_DIR/ 'procedures.csv', self.valid_asset_ids, self.frequencies)

        self.assertEqual(len(good), 8)
        self.assertEqual(len(rejected), 7)
        rsns = {line_num: reason for line_num, reason, row in rejected}
        self.assertEqual(rsns, {10: 'invalid procedure tag', 11: 'procedure_id does not match asset_id', 12: 'asset not found', 13: 'unknown service_frequency', 14: 'frequency does not match tag', 15: 'duplicate procedure_id', 16: 'blank description'})

class TestServiceHistory(SharedSetup):

    def test_load_service_history(self):
        good_proc, rejected_proc = load_procedures(DATA_DIR/ 'procedures.csv', self.valid_asset_ids, self.frequencies)
        asset_dates = {row['asset_id']: datetime.strptime(row['commissioning_date'], DATE_FMT) for line_num, row in self.good_assets}
        procedure_commissioning = {row['procedure_id']: asset_dates[row['asset_id']] for line_num, row in good_proc}
        today = datetime(2026, 10, 21)
        good, rejected = load_service_history(DATA_DIR/ 'service_history.csv', procedure_commissioning, today)

        self.assertEqual(len(good), 10)
        self.assertEqual(len(rejected), 6)
        rsns = {line_num: reason for line_num, reason, row in rejected}
        self.assertEqual(rsns, {12: 'procedure not found', 13: 'invalid date_completed', 14: 'future date_completed', 15: 'duplicate record_id', 16: 'date_completed before commissioning', 17: 'blank date_completed'})


if __name__ == '__main__': unittest.main()
