import pytest

from multiyear_energy_validation.pypsa_asset_staging import (
    attach_observed_load_to_staged_assets,
)


def test_reject_missing_staged_network(tmp_path):
    pytest.importorskip("pypsa")
    with pytest.raises((FileNotFoundError, OSError, ValueError)):
        attach_observed_load_to_staged_assets(
            tmp_path / "missing.nc", tmp_path / "missing.csv", tmp_path / "out.nc"
        )
