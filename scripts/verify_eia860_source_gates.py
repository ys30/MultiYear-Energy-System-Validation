"""Check archived EIA-860 source provenance and preserve fail-closed gates."""
import argparse
import json
import zipfile

EXPECTED = {
  2024: ("0aaae04812cd4ab87a3e346bdf93848a3cc15053fd4dc2a4cf82d2aeac95f12b", 22100342),
  2025: ("2b27929d26cc1da9ad6a530da1cac6718cd8496098ee560c4d47cfffd96d08ba", 23622347),
}
FLAGS = ("generation_fleet_validated", "balancing_authority_mapping_validated", "dispatch_model_approved")
REQUIRED = ("2___Plant_", "3_1_Generator_", "3_4_Energy_Storage_", "LayoutY")

def verify(artifact):
    result = {"source_metadata_verified": True, "full_fleet_validated": False,
              "ba_mapping_validated": False, "empirical_dispatch_approved": False, "years": {}}
    with zipfile.ZipFile(artifact) as archive:
        for year, (sha, size) in EXPECTED.items():
            record = json.loads(archive.read(f"{year}/source_inventory.json"))
            assert record["year"] == year
            assert record["sha256"] == sha
            assert record["archive_bytes"] == size
            entries = record["entries"]
            assert entries and all(isinstance(e["bytes"], int) and e["bytes"] > 0 for e in entries)
            names = {e["name"] for e in entries}
            assert len(names) == len(entries)
            assert all(any(n.startswith(prefix) for n in names) for prefix in REQUIRED)
            assert record["workbook_layouts_recorded"]
            assert all(record[flag] is False for flag in FLAGS)
            result["years"][str(year)] = {
                "source_sha256": sha, "archive_bytes": size, "workbook_entries": len(entries),
                "validation_flags": {flag: record[flag] for flag in FLAGS}}
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.artifact), indent=2))
