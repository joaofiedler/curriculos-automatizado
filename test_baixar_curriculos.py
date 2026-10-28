import unittest
import tempfile
from unittest.mock import patch

import baixar_curriculos


class ChooseMinIdTest(unittest.TestCase):
    def test_automatic_and_manual_modes(self):
        with patch("builtins.input", return_value="1"):
            self.assertEqual(baixar_curriculos.choose_min_id(4104), 4104)

        with patch("builtins.input", side_effect=["2", "4200"]):
            self.assertEqual(baixar_curriculos.choose_min_id(4104), 4200)

    def test_checkpoint(self):
        with tempfile.TemporaryDirectory() as output_dir:
            self.assertEqual(baixar_curriculos.load_min_id(output_dir), baixar_curriculos.MIN_ID)
            baixar_curriculos.save_min_id(output_dir, 4201)
            self.assertEqual(baixar_curriculos.load_min_id(output_dir), 4201)


if __name__ == "__main__":
    unittest.main()
