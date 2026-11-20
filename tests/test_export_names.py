"""Export file names (run: python -m unittest discover tests)."""
import os
import tempfile
import unittest

import pandas as pd

from imgMS.MSData import MSData
from imgMS.side_functions import excel_path


class ExcelPath(unittest.TestCase):

    def test_names(self):
        self.assertEqual(excel_path('/d/deleteme'), '/d/deleteme.xlsx')
        self.assertEqual(excel_path('/d/deleteme.xlsx'), '/d/deleteme.xlsx')
        self.assertEqual(excel_path('/d/deleteme.csv'), '/d/deleteme.xlsx')
        self.assertEqual(excel_path('/d/deleteme.XLS'), '/d/deleteme.xlsx')
        self.assertEqual(excel_path('/d/run.v2'), '/d/run.v2.xlsx')
        self.assertEqual(excel_path('/my.dir/deleteme'), '/my.dir/deleteme.xlsx')


class Exports(unittest.TestCase):

    def make(self):
        d = MSData.__new__(MSData)
        d.logger = None
        d.data = None
        d.means = None
        q = pd.DataFrame({'Si28': [1.0, 1.1, 0.9], 'Ca43': [2.0, 2.1, 1.9]}, index=['A', 'A', 'A'])
        d.quantified = q
        d.corrected_TS = q * 2
        d.corrected_IS = {'Si28': q * 3, 'Ca43': q * 4}
        return d

    def test_stats_and_export_without_extension(self):
        d = self.make()
        with tempfile.TemporaryDirectory() as t:
            base = os.path.join(t, 'deleteme')
            d.formated_export(base, table='IScorrected')
            d.formated_export(base + '.csv', table='quantified')
            d.formated_export(base, table='TScorrected')
            d.export(base + '_all')
            self.assertEqual(sorted(os.listdir(t)), ['deleteme.xlsx', 'deleteme_Ca43.xlsx', 'deleteme_Si28.xlsx',
                                                     'deleteme_all.xlsx'])


if __name__ == '__main__':
    unittest.main()
