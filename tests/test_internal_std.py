"""Tests for internal standard correction (run: python -m unittest discover tests)."""
import types
import unittest

import numpy as np
import pandas as pd

from imgMS.MSData import MSData
from imgMS.side_functions import correction, match_internal_std

# quantified data: calibrant (BCR-2) peaks already removed, run order kept
NAMES = ['SDC-1', 'VG-A1', 'VG-A1', 'VG-A2', 'SDC-1']
QUANT = pd.DataFrame({'Si28': [300000.0, 200000.0, 210000.0, 180000.0, 310000.0],
                      'Ca43': [10000.0, 50000.0, 52000.0, 40000.0, 10500.0]}, index=NAMES)


def old_correction(data, elem, internal_std):
    """Behaviour before the fix: values applied by position."""
    ratio = data[elem].div(list(internal_std[elem]))
    return data.apply(lambda x: x / ratio)


class MatchInternalStd(unittest.TestCase):

    def test_one_row_per_peak_in_run_order_is_unchanged(self):
        # per-spot values (VG-A1 differs between its spots): only possible by position
        sheet = pd.DataFrame({'Si28': [307573.4, 187000.0, 188000.0, 180000.0, 307573.4]}, index=NAMES)
        new = correction(QUANT, 'Si28', sheet)
        pd.testing.assert_frame_equal(new, old_correction(QUANT, 'Si28', sheet))
        np.testing.assert_allclose(new['Si28'], sheet['Si28'])

    def test_one_row_per_sample_any_order_with_calibrant(self):
        sheet = pd.DataFrame({'Si28': [180000.0, 307573.4, 252000.0, 187000.0]},
                             index=['VG-A2', 'SDC-1', 'BCR-2', 'VG-A1'])
        out = correction(QUANT, 'Si28', sheet)
        self.assertEqual(list(out.index), NAMES)
        np.testing.assert_allclose(out['Si28'], [307573.4, 187000.0, 187000.0, 180000.0, 307573.4])
        # other isotopes scale by the same per-spot factor
        np.testing.assert_allclose(out['Ca43'], QUANT['Ca43'] * out['Si28'] / QUANT['Si28'])

    def test_wrong_order_with_per_spot_values_raises(self):
        # same rows as the positional case but shuffled: matching by name is ambiguous
        sheet = pd.DataFrame({'Si28': [187000.0, 307573.4, 188000.0, 180000.0, 307573.4]},
                             index=['VG-A1', 'SDC-1', 'VG-A1', 'VG-A2', 'SDC-1'])
        with self.assertRaises(ValueError) as cm:
            match_internal_std(NAMES, sheet)
        msg = str(cm.exception)
        self.assertIn('not the peak names in run order', msg)
        self.assertIn('VG-A1', msg)

    def test_missing_sample_raises(self):
        sheet = pd.DataFrame({'Si28': [307573.4, 187000.0]}, index=['SDC-1', 'VG-A1'])
        with self.assertRaises(ValueError) as cm:
            match_internal_std(NAMES, sheet)
        self.assertIn('No row for: VG-A2', str(cm.exception))

    def test_row_count_off_by_one_raises_instead_of_shifting(self):
        # positional sheet that wrongly keeps one calibrant row at the top
        sheet = pd.DataFrame({'Si28': [252000.0, 307573.4, 187000.0, 188000.0, 180000.0, 307573.4]},
                             index=['BCR-2'] + NAMES)
        with self.assertRaises(ValueError) as cm:
            match_internal_std(NAMES, sheet)
        self.assertIn('6 rows for 5 peaks', str(cm.exception))

    def test_blank_value_raises(self):
        sheet = pd.DataFrame({'Si28': [307573.4, np.nan, 180000.0]}, index=['SDC-1', 'VG-A1', 'VG-A2'])
        with self.assertRaises(ValueError) as cm:
            match_internal_std(NAMES, sheet)
        self.assertIn('missing for: VG-A1 (Si28)', str(cm.exception))

    def test_numeric_and_padded_names(self):
        q = pd.DataFrame({'Si28': [1.0, 2.0]}, index=['1', 'A '])
        sheet = pd.DataFrame({'Si28': [10.0, 20.0]}, index=[1, 'A'])
        self.assertEqual(list(match_internal_std(list(q.index), sheet)['Si28']), [10.0, 20.0])


class ISCorrection(unittest.TestCase):

    def make(self, sheet):
        d = MSData.__new__(MSData)
        d.logger = None
        d.quantified = QUANT
        d.isotope_names = list(QUANT.columns)
        d.param = types.SimpleNamespace(is_coef=sheet)
        d.corrected_IS = None
        return d

    def test_corrects_by_name(self):
        sheet = pd.DataFrame({'Si28': [307573.4, 187000.0, 180000.0]}, index=['SDC-1', 'VG-A1', 'VG-A2'])
        out = self.make(sheet).IS_correction()
        np.testing.assert_allclose(out['Si28']['Si28'], [307573.4, 187000.0, 187000.0, 180000.0, 307573.4])

    def test_mismatch_raises_and_leaves_no_result(self):
        d = self.make(pd.DataFrame({'Si28': [307573.4]}, index=['SDC-1']))
        with self.assertRaises(ValueError):
            d.IS_correction()
        self.assertIsNone(d.corrected_IS)

    def test_missing_param_or_values_raise(self):
        d = self.make(pd.DataFrame())
        with self.assertRaises(ValueError):
            d.IS_correction()
        d.param = None
        with self.assertRaises(ValueError):
            d.IS_correction()


if __name__ == '__main__':
    unittest.main()
