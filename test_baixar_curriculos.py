import unittest
from unittest.mock import patch

import baixar_curriculos


class ChooseMinIdTest(unittest.TestCase):
    def test_automatic_and_manual_modes(self):
        with patch("builtins.input", return_value="1"):
            self.assertEqual(baixar_curriculos.choose_min_id(), baixar_curriculos.MIN_ID)

        with patch("builtins.input", side_effect=["2", "4200"]):
            self.assertEqual(baixar_curriculos.choose_min_id(), 4200)


if __name__ == "__main__":
    unittest.main()
