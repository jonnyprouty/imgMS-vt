"""Report with one LoD per isotope (no drift correction) and one per peak (drift correction)."""
import unittest

import pandas as pd

from imgMS.MSData import MSData


def make(lod, lod_spots=None):
    d = MSData.__new__(MSData)
    d.logger = None
    d.quantified = pd.DataFrame({'Si28': [5.0, 5.0, 5.0]}, index=['A', 'B', 'C'])
    d.corrected_IS = None
    d.corrected_TS = None
    d.lod = pd.Series({'Si28': lod}, name='lod')
    d.lod_spots = lod_spots
    return d


class ReportLoD(unittest.TestCase):

    def test_single_lod(self):
        d = make(6.0)
        d.report()
        self.assertEqual(list(d.quantified['Si28'][:3]), ['< LoD'] * 3)

    def test_per_spot_lod(self):
        d = make(5.0, pd.DataFrame({'Si28': [4.0, 6.0, 4.5]}))
        d.report()
        self.assertEqual(list(d.quantified['Si28'][:3]), [5.0, '< LoD', 5.0])
        self.assertEqual(list(d.quantified.index), ['A', 'B', 'C', 'lod'])


if __name__ == '__main__':
    unittest.main()
