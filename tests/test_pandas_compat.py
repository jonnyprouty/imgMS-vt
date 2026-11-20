"""pandas 1.x / 2.x compatibility helpers (run: python -m unittest discover tests)."""
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

from imgMS.side_functions import append_row, formatted_export


class AppendRow(unittest.TestCase):

    def test_adds_named_row(self):
        df = pd.DataFrame({'Si28': [1.0, 2.0], 'Ca43': [3.0, 4.0]}, index=['A', 'B'])
        out = append_row(df, pd.Series({'Si28': 0.1, 'Ca43': 0.2}, name='lod'))
        self.assertEqual(list(out.index), ['A', 'B', 'lod'])
        self.assertEqual(out.loc['lod'].tolist(), [0.1, 0.2])

    def test_ignore_index(self):
        df = pd.DataFrame(columns=['sample', 'x'])
        out = append_row(df, pd.Series({'sample': 'LoD', 'x': 1.5}), ignore_index=True)
        self.assertEqual(out.iloc[0].tolist(), ['LoD', 1.5])


class FormattedExport(unittest.TestCase):

    def test_writes_outliers_and_stats(self):
        df = pd.DataFrame({'Si28': [1.0, 1.1, 0.9, 5.0, 5.2], 'Ca43': [2.0, 2.1, 1.9, 7.0, np.nan]},
                          index=['A', 'A', 'A', 'B', 'B'])
        df = append_row(df, pd.Series({'Si28': 0.01, 'Ca43': 0.02}, name='LoD'))
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, 'stats.xlsx')
            formatted_export(df, p)
            sheets = pd.read_excel(p, sheet_name=None)
        self.assertEqual(set(sheets), {'Outliers', 'Stats'})
        stats = sheets['Stats']
        mean_a = stats[(stats['sample'] == 'A') & (stats['stat'] == 'mean')]['Si28'].iloc[0]
        self.assertAlmostEqual(mean_a, 1.0)


if __name__ == '__main__':
    unittest.main()
