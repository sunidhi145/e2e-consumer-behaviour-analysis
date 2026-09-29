import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CustomerDropdownVisibilityTest(unittest.TestCase):
    def test_customer_id_dropdown_has_scoped_visibility_class(self):
        source = (ROOT / "pages" / "customer_explorer.py").read_text()

        self.assertIn('id="customer-id-input"', source)
        self.assertIn('className="dark-dropdown customer-id-dropdown"', source)

    def test_customer_id_dropdown_selected_text_is_black(self):
        css = (ROOT / "assets" / "styles.css").read_text()

        self.assertIn("#customer-id-input.customer-id-dropdown .Select-value-label", css)
        self.assertIn("#customer-id-input.customer-id-dropdown .Select-input input", css)
        self.assertIn("-webkit-text-fill-color: #000 !important;", css)


if __name__ == "__main__":
    unittest.main()
