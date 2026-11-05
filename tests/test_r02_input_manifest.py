from multiyear_energy_validation.r02_input_manifest import (
    REQUIRED_INPUTS, audit_input_manifest,
)


def test_missing_inputs_never_approve_dispatch():
    report = audit_input_manifest({})
    assert not report["all_metadata_complete"]
    assert not report["all_empirically_verified"]
    assert not report["dispatch_approved"]
    assert set(report["checks"]) == set(REQUIRED_INPUTS)


def test_complete_metadata_without_evidence_not_verified():
    manifest = {
        key: {field: "candidate" for field in fields}
        for key, fields in REQUIRED_INPUTS.items()
    }
    report = audit_input_manifest(manifest)
    assert report["all_metadata_complete"]
    assert not report["all_empirically_verified"]
    assert not report["dispatch_approved"]


def test_even_self_attested_evidence_does_not_approve_dispatch():
    manifest = {
        key: {**{field: "candidate" for field in fields},
              "empirically_verified": True}
        for key, fields in REQUIRED_INPUTS.items()
    }
    report = audit_input_manifest(manifest)
    assert report["all_empirically_verified"]
    assert not report["dispatch_approved"]
