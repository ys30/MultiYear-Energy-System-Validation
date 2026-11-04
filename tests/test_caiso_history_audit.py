from multiyear_energy_validation.caiso_history_audit import inspect_csv


def test_caiso_shape_comparison_detects_opposite_directions():
    header = "Time,Day ahead forecast,Hour ahead forecast,Current demand,Demand response"
    rows = [header]
    for hour, base in ((12, 24000), (13, 25500), (14, 27500)):
        for minute in range(0, 60, 5):
            rows.append(f"{hour:02d}:{minute:02d},,,{base + minute},")
    report = inspect_csv("\n".join(rows))
    assert report["hourly_shape_comparison"]["all_hours_complete"]
    assert report["hourly_shape_comparison"]["12:00_to_13:00"]["same_change_direction"] is False
    assert report["hourly_shape_comparison"]["13:00_to_14:00"]["same_change_direction"] is True
