import unittest

from validate import validate_source


class ValidateSourceTest(unittest.TestCase):
    def test_local_import_records_inventory_without_inventing_git_history(self):
        validate_source({"kind": "local-import", "name": "experiment", "inventory_sha256": "a" * 64,
                         "imported_on": "2026-10-13"})

    def test_missing_or_invalid_provenance_fails(self):
        for source in [{"commit": "main"}, {"kind": "local-import", "name": "experiment"},
                       {"kind": "local-import", "name": "experiment", "inventory_sha256": "a" * 64}]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                validate_source(source)


if __name__ == "__main__":
    unittest.main()
