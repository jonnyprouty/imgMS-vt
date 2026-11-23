"""Background is recalculated when its inputs change (run: python -m unittest discover tests)."""
import unittest

import numpy as np
import pandas as pd

from imgMS.MSData import MSData


def make():
    values = np.full(200, 100.0)
    values[60:120] = 10000.0
    values[90] = 5e6
    df = pd.DataFrame({'Si28': values}, index=0.5 + 0.5 * np.arange(200))

    class Reader:
        filename = 'run.csv'

        def __call__(self):
            return df

    d = MSData(Reader())
    d.laser_on, d.laser_off = [(60, 120)], [(0, 60), (120, 198)]
    d.names = ['A']
    return d


class BackgroundCache(unittest.TestCase):

    def test_despiking_setting_takes_effect_on_later_average(self):
        d = make()
        with_spike = d.average_isotopes(despiked=False)['Si28'].values[0]
        despiked = d.average_isotopes(despiked=True)['Si28'].values[0]
        self.assertLess(despiked, with_spike)
        self.assertEqual(d.average_isotopes(despiked=False)['Si28'].values[0], with_spike)

    def test_new_selection_recalculates_background(self):
        d = make()
        first = d.average_isotopes(despiked=False)['Si28'].values[0]
        # a wider window that used to reuse the background of the first selection
        d.laser_on, d.laser_off = [(50, 130)], [(0, 50), (130, 198)]
        d.selection_version += 1
        d.average_isotopes(despiked=False)
        iso = d.isotopes['Si28']
        np.testing.assert_allclose(iso.bcg.bcg_interp[50:130], 100.0)
        self.assertNotEqual(d.means['Si28'].values[0], first)


if __name__ == '__main__':
    unittest.main()
