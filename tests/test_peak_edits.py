"""Manual peak edits (run: python -m unittest discover tests)."""
import json
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

from imgMS.MSData import MSData

BLANK, SIGNAL = 100.0, 10000.0
ON = [(40, 90), (130, 180), (220, 270)]
OFF = [(0, 40), (90, 130), (180, 220), (270, 318)]


def make(inclusion=True):
    """Three flat peaks; peak 2 (index 1) has a 5-reading inclusion and a high tail."""
    n = 320
    si = np.full(n, BLANK)
    for a, b in ON:
        si[a:b] = SIGNAL
    if inclusion:
        si[150:155] = 90000.0
    ca = si / 2
    t = 0.5 + 0.5 * np.arange(n)
    df = pd.DataFrame({'Si28': si, 'Ca43': ca}, index=pd.Index(t, name='Time [Sec]'))

    class Reader:
        filename = 'run.csv'

        def __call__(self):
            return df
    d = MSData(Reader())
    d.laser_on, d.laser_off = list(ON), list(OFF)
    d.starts, d.ends = [a for a, _ in ON], [b for _, b in ON]
    d.names = ['STD', 'A', 'B']
    d.srms = pd.DataFrame({'Si': [20000.0], 'Ca': [10000.0]}, index=['STD'])
    return d


def averages(d, **k):
    k = dict(despiked=False, bcgcor_method='all', method='intensity', **k)
    return d.average_isotopes(**k)['Si28'].values


class Windows(unittest.TestCase):

    def test_no_edits_uses_automatic_windows(self):
        d = make(False)
        self.assertIs(d.background_windows()[0], d.laser_on)
        self.assertIs(d.background_windows()[1], d.laser_off)
        self.assertEqual(d.signal_segments(1), [ON[1]])
        np.testing.assert_allclose(averages(d), SIGNAL - BLANK)

    def test_trimmed_readings_are_not_background(self):
        d = make(False)
        d.data.iloc[170:180, 0] = 60000.0
        for iso in d.isotopes.values():
            iso.data = d.data[iso.isotope_name].values
        d.set_peak_edit(1, end=170)
        res = averages(d)
        self.assertAlmostEqual(res[1], SIGNAL - BLANK)   # high tail in neither signal nor background
        self.assertAlmostEqual(res[0], SIGNAL - BLANK)   # other peaks unchanged
        self.assertAlmostEqual(res[2], SIGNAL - BLANK)

    def test_extended_window_leaves_the_blank(self):
        d = make(False)
        d.set_peak_edit(1, start=125)
        on, off = d.background_windows()
        self.assertEqual(on[1], (125, 180))
        self.assertEqual(off[1], (90, 125))

    def test_exclude_interval(self):
        d = make()
        before = averages(d)[1]
        self.assertGreater(before, SIGNAL)
        d.set_peak_edit(1, exclude=[(150, 155)])
        self.assertEqual(d.signal_segments(1), [(130, 150), (155, 180)])
        self.assertAlmostEqual(averages(d)[1], SIGNAL - BLANK)

    def test_exclusions_merge_and_clip(self):
        d = make(False)
        d.set_peak_edit(1, start=135, exclude=[(120, 140), (138, 145), (160, 162)])
        self.assertEqual(d.peak_edits[1]['exclude'], [(135, 145), (160, 162)])

    def test_invalid_edits(self):
        d = make(False)
        for kw in (dict(start=88), dict(end=218), dict(start=170, end=172),
                   dict(exclude=[(130, 179)])):
            with self.assertRaises(ValueError):
                d.set_peak_edit(1, **kw)
        self.assertEqual(d.peak_edits, {})

    def test_back_to_automatic_removes_the_edit(self):
        d = make(False)
        d.set_peak_edit(1, start=135)
        d.set_peak_edit(1, start=130)
        self.assertEqual(d.peak_edits, {})


class Results(unittest.TestCase):

    def test_edit_clears_results_and_quantify_needs_average(self):
        d = make()
        averages(d)
        d.quantify_isotopes(srm_name='STD', drift_correction=False)
        self.assertFalse(d.set_peak_edit(1, start=130))   # no change, results kept
        self.assertIsNotNone(d.quantified)
        d.set_peak_edit(1, exclude=[(150, 155)])
        self.assertIsNone(d.means)
        self.assertIsNone(d.quantified)
        with self.assertRaises(ValueError):
            d.quantify_isotopes(srm_name='STD', drift_correction=False)


class Files(unittest.TestCase):

    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.p = os.path.join(self.t.name, 'edits.json')

    def tearDown(self):
        self.t.cleanup()

    def test_round_trip(self):
        d = make()
        d.set_peak_edit(1, start=133, end=175, exclude=[(150, 155)])
        d.save_peak_edits(self.p)
        e = make()
        self.assertEqual(e.load_peak_edits(self.p), 1)
        self.assertEqual(e.peak_edits, d.peak_edits)

    def test_mismatch_changes_nothing(self):
        d = make()
        d.set_peak_edit(1, start=133)
        d.save_peak_edits(self.p)
        e = make()
        e.names = ['STD', 'X', 'B']
        e.set_peak_edit(2, start=225)
        averages(e)
        before = dict(e.peak_edits)
        with self.assertRaises(ValueError):
            e.load_peak_edits(self.p)
        self.assertEqual(e.peak_edits, before)
        self.assertIsNotNone(e.means)
        with open(self.p) as fh:
            x = json.load(fh)
        x['n_peaks'] = 9
        with open(self.p, 'w') as fh:
            json.dump(x, fh)
        with self.assertRaises(ValueError):
            make().load_peak_edits(self.p)

    def test_edits_recorded_in_exports(self):
        d = make()
        d.set_peak_edit(1, exclude=[(150, 155)])
        averages(d)
        d.quantify_isotopes(srm_name='STD', drift_correction=False)
        base = os.path.join(self.t.name, 'out')
        d.export(base)
        d.formated_export(base + '_stats', table='quantified')
        for f in ('out.xlsx', 'out_stats.xlsx'):
            sheet = pd.read_excel(os.path.join(self.t.name, f), sheet_name='peak_edits')
            self.assertEqual(sheet.loc[0, 'name'], 'A')
            self.assertEqual(sheet.loc[0, 'readings_used'], 45)
            self.assertEqual(sheet.loc[0, 'excluded_s'], '75.500-77.500')


if __name__ == '__main__':
    unittest.main()
