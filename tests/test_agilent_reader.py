"""Tests for the Agilent reader (run: python -m unittest discover tests)."""
import os
import tempfile
import unittest

from imgMS.MSEval import DataReader

HEAD = ["C:\\Agilent\\DATA\\run.d,,,", "Intensity Vs Time,Counts,,,",
        "Acquired      : Oct 28 2026  02:07 PM using Batch x.b,,,", "Time [Sec],Na23,Si28,Ca43"]
ROWS = [f"{0.3 + i * 0.3:.4f},{100 + i},{2000 + i},{50 + i}" for i in range(20)]
FOOTERS = {
    "standard": [",,,", ",,,", "          Printed:Wed Oct 28 15:00:00 2026,,,"],
    "none": [],
    "printed only": ["          Printed:Wed Oct 28 15:00:00 2026,,,"],
    "four lines": [",,,", ",,,", ",,,", "          Printed:Wed Oct 28 15:00:00 2026,,,"],
}


def read(lines, ext="csv"):
    with tempfile.NamedTemporaryFile("w", suffix="." + ext, delete=False) as fh:
        fh.write("\n".join(lines) + "\n")
    try:
        return DataReader(filename=fh.name, filetype=ext, instrument="Agilent").data
    finally:
        os.remove(fh.name)


class AgilentReader(unittest.TestCase):

    def test_keeps_every_data_row_for_any_footer(self):
        for name, foot in FOOTERS.items():
            with self.subTest(footer=name):
                d = read(HEAD + ROWS + foot)
                self.assertEqual(len(d), len(ROWS))
                self.assertAlmostEqual(d.index[-1], float(ROWS[-1].split(",")[0]))
                self.assertEqual(d.iloc[-1].tolist(), [119.0, 2019.0, 69.0])

    def test_numeric_columns_and_index(self):
        d = read(HEAD + ROWS + FOOTERS["standard"])
        self.assertEqual(list(d.columns), ["Na23", "Si28", "Ca43"])
        self.assertTrue(all(str(t) == "float64" for t in d.dtypes))
        self.assertEqual(str(d.index.dtype), "float64")

    def test_txt_export(self):
        d = read(HEAD + ROWS + FOOTERS["standard"], ext="txt")
        self.assertEqual(len(d), len(ROWS))


if __name__ == "__main__":
    unittest.main()
