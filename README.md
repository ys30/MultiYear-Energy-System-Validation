# Multi-Year Energy System Validation with PyPSA

**Research repository — initialization stage (not yet validated).**

This private research project develops a reproducible multi-year energy-system data harmonization and PyPSA validation workflow. It is separate from [the engineering v1.0 demonstration](https://github.com/ys30/lut-to-pypsa), which uses a source-traced **2020 five-continent annual LUT demand fixture**, synthetic hourly load shapes, and illustrative independent-region dispatch.

## Scientific boundary

No empirical multi-year model results, regional calibration, transmission adequacy estimates, or real-world reliability conclusions are claimed at this stage. The LUT five-continent fixture must not be relabeled as Western-US hourly electricity load.

## Research sequence

1. Audit candidate annual and hourly sources, licenses, temporal coverage, geography, physical units and missingness.
2. Define explicit data contracts and implement automated conservation, temporal alignment and provenance checks.
3. Build and calibrate PyPSA benchmarks only for supported regional datasets.
4. Evaluate held-out years, sensitivity, uncertainty, and solver diagnostics.
5. Prepare reproducible tables, figures and a manuscript only from verified runs.

## Reproducibility

Run `python -m pytest -q` after installing `pip install -e ".[test]"`. Initial tests validate the **schema and temporal accounting**, not empirical data.

## Status

- [x] Private research repository initialized
- [x] Validation contract and preliminary manuscript outline
- [ ] Dataset approval, licensing and ingestion
- [ ] Verified multi-year regional model
- [ ] Calibration and out-of-sample evaluation
- [ ] Research results and paper-ready figures

**Data governance:** do not commit unlicensed third-party workbooks, personal data, confidential inputs, or manuscripts intended to remain outside the repository.
