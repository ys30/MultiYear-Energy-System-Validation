import pytest

from multiyear_energy_validation.pypsa_asset_staging import (
    attach_observed_load_to_staged_assets,
)


def test_reject_invalid_load_schema(tmp_path):
    pypsa = pytest.importorskip("pypsa")
    network = pypsa.Network()
    network.add("Bus", "CISO")
    network.add("Generator", "sample", bus="CISO", p_nom=10, p_max_pu=0)
    source = tmp_path / "asset.nc"
    network.export_to_netcdf(source)
    load = tmp_path / "load.csv"
    load.write_text("bad_header,value\\n2024-01-01,100\\n".replace("\\\\n", "\\n"))
    with pytest.raises(ValueError, match="invalid observed load schema"):
        attach_observed_load_to_staged_assets(source, load, tmp_path / "combined.nc")
