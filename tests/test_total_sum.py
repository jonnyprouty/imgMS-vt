"""Total sum correction factors (run: python -m unittest discover tests)."""
import os
import types
import unittest

import pandas as pd

from imgMS.MSData import MSData

# Si28 and Ca43 in ppm; with the built-in factors, SiO2 + CaO = 100 % after correction
QUANT = pd.DataFrame({'Si28': [200000.0], 'Ca43': [50000.0]}, index=['A'])


def make(param):
    d = MSData.__new__(MSData)
    d.logger = None
    d.quantified = QUANT
    d.param = param
    return d


def oxide_total(ts, coef):
    return sum(ts.loc['A', iso] / coef[iso] * 100 for iso in ts.columns)


class TotalSum(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), os.pardir, 'imgMS'))  # has default_sum_koef.xlsx

    def tearDown(self):
        os.chdir(self.cwd)

    def test_builtin_factors_include_ca43(self):
        ts = make(None).TS_correction(suma=1e6)
        self.assertAlmostEqual(oxide_total(ts, {'Si28': 46.75, 'Ca43': 71.469}), 1e6, places=3)

    def test_param_without_total_sum_sheet_falls_back(self):
        ts = make(types.SimpleNamespace(ts_coef={})).TS_correction(suma=1e6)
        self.assertAlmostEqual(oxide_total(ts, {'Si28': 46.75, 'Ca43': 71.469}), 1e6, places=3)

    def test_param_factors_used(self):
        coef = {'Si28': 50.0, 'Ca43': 70.0}
        ts = make(types.SimpleNamespace(ts_coef=coef)).TS_correction(suma=1e6)
        self.assertAlmostEqual(oxide_total(ts, coef), 1e6, places=3)

    def test_falls_back_to_package_copy(self):
        os.chdir(os.path.dirname(__file__))  # no default_sum_koef.xlsx here
        ts = make(None).TS_correction(suma=1e6)
        self.assertAlmostEqual(oxide_total(ts, {'Si28': 46.75, 'Ca43': 71.469}), 1e6, places=3)


if __name__ == '__main__':
    unittest.main()
