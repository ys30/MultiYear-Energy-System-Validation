import pytest
from multiyear_energy_validation.air_density_diagnostic import dry_air_density


def test_standard_atmosphere():
    assert dry_air_density(101325, 15) == pytest.approx(1.225, rel=0.001)


@pytest.mark.parametrize("pressure,temp", [(0,20),(150000,20),(101325,-100),(101325,100)])
def test_unphysical_inputs_rejected(pressure,temp):
    with pytest.raises(ValueError):
        dry_air_density(pressure,temp)
