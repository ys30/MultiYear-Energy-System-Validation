import pytest
from multiyear_energy_validation.contracts import expected_hours, check_annual_energy

def test_leap_year():
    assert expected_hours(2020) == 8784
    assert expected_hours(2021) == 8760

def test_conservation():
    check_annual_energy([1.0, 2.0, 3.0], 6.0)

def test_reject_mismatch():
    with pytest.raises(ValueError, match="mismatch"):
        check_annual_energy([1.0, 2.0], 10.0)

def test_reject_negative():
    with pytest.raises(ValueError):
        check_annual_energy([-1.0], 0.0)
