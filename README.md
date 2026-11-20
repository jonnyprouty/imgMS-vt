[![Documentation Status](https://readthedocs.org/projects/imgms/badge/?version=latest)](https://imgms.readthedocs.io/en/latest/?badge=latest)

# imgMS

## About this fork

This repository is a fork of [nikadilli/imgMS](https://github.com/nikadilli/imgMS), adapted to the specific needs and workflow of the **Virginia Tech Department of Geosciences LA-ICP-MS lab**. It is used by the lab fork of Ilaps, [jonnyprouty/Ilaps-v2-vt](https://github.com/jonnyprouty/Ilaps-v2-vt), which holds the lab procedure.

Install this version (instead of `pip install imgMS`, which installs the original):

```
pip install git+https://github.com/jonnyprouty/imgMS-vt.git
```

Changes from the original (0.2.12):

- Internal standard values are matched to peaks by name (one row per sample, any order), or by position when there is one row per peak in run order; a sheet that fits neither raises an error instead of applying values to the wrong peaks.
- The Agilent reader keeps the last data row (a fixed footer length dropped it).
- Works with pandas 2 (`DataFrame.append` and `ExcelWriter.save` replaced; also works with pandas 1.5).
- Report handles per-peak detection limits from drift correction.
- Built-in total-sum factors cover all common isotopes (Ca43 was missing); a Param file without total-sum factors falls back to them.
- Export and stats export accept file names without an extension (`.xlsx` is added).
- Tests: `python -m unittest discover tests`.

The original README follows.

## Introduction
LA-ICP-MS data require high level of manual processing to achieve results. Often the time needed for data evaluation by far exceeds the time necessary for data aquisition. During analysis, mass spectra are either written as a separate files, or as a continuous data stream into one single file. Both of these aproaches require a different workflow of processing steps. *imgMS* is a Python package which aims to provide an easy and intuitive way of working with LA-ICP-MS data acquired into single file.

*imgMS* automatically processes these steps of analysis:
1. bacground/signal identification
2. signal despiking
3. background substraction
4. total sum normalisation
5. internal standard normalisation
6. quantification to reference material
7. generation of elemental maps

## Motivation

As a Phd student in the field of analytical chemistry using LA-ICP-MS for rutine analysis as well as research tasks, I found it pretty difficult and time consuming to evaluate data without an appropriate software. Despite the fact, that there exists multiple free or open source software, I couldn't find any that would fit the workflow of our department. What started as a simple script for data reduction of LA-ICP-MS data, is now a complete python package.  

This package is intended to provide a quick, as well as (hopefully) easy to undestand, way of getting a results from bulk analysis or elemental imaging using LA-ICP-MS.

## Installation

*imgMS* is a python package registered at PyPI, and therefore can be installed with pip:

```
pip install imgMS
```

## Limitations

- So far there is only option to directly import data from 2 instruments (ThermoFisher Element2 and Agilent) in 3 formats (.csv, .xlsx, .asc). In the future there will be more options.

- imgMS only works with multiple analysis with reference analysis acquired in one file, unlike many other software aimed on LA-ICP-MS data reduction. 



