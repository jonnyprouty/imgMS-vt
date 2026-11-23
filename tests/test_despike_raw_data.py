"""Despiking must not change the raw data (run: python -m unittest discover tests)."""
import unittest

import numpy as np
import pandas as pd

from imgMS.MSData import Isotope, MSData


class DespikeKeepsRawData(unittest.TestCase):

    def test_raw_data_unchanged(self):
        values = np.full(200, 100.0)
        values[100] = 1e6
        d = MSData()
        d.data = pd.DataFrame({'Si28': values.copy()}, index=np.arange(200) * 0.5)
        iso = Isotope('Si28', d)
        iso.despike()
        self.assertLess(iso.despiked[100], 1e6)     # the spike is removed from the despiked copy
        np.testing.assert_array_equal(iso.data, values)
        np.testing.assert_array_equal(d.data['Si28'].values, values)


if __name__ == '__main__':
    unittest.main()
