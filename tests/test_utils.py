import unittest
from total_scattering import utils


class TestUtilsForReduction(unittest.TestCase):

    def setUp(self):
        pass

    def test_compress_ints_compression_needed_ends_with_range(self):
        """ Test for compressing list of integers to string;
        compression needed;
        ends on a range (i.e. ..., N-M)
        """
        line_nums = [1, 2, 3, 8, 9]
        target = "1-3, 8-9"
        self.assertEqual(utils.compress_ints(line_nums), target)

    def test_compress_ints_compression_needed_ends_with_single_int(self):
        """ Test for compressing list of integers to string;
        compression needed;
        ends on a single integer (i.e ..., N)
        """
        line_nums = [1, 2, 3, 8, 9, 12]
        target = "1-3, 8-9, 12"
        self.assertEqual(utils.compress_ints(line_nums), target)

    def test_compress_ints_no_compression_needed(self):
        """ Test for compressing list of integers to string;
        no compression needed;
        """
        line_nums = [1, 6]
        target = "1, 6"
        self.assertEqual(utils.compress_ints(line_nums), target)

    def test_expand_ints(self):
        """ Test for expanding str to list of integers function
        """
        s = "1-3, 8-9, 12"
        target = [1, 2, 3, 8, 9, 12]
        self.assertEqual(utils.expand_ints(s), target)

    def test_one_and_only_one(self):
        """ Test for the one and only one true value utility function
        """
        inputList = [True, False, False]
        output = utils.one_and_only_one(inputList)
        self.assertTrue(output)

    def test_find_key_match_in_dict(self):
        """ Test for using list of keys to get back value of
        one and only one matching key from dict
        """
        keys = ["Vanadium", "Normalization", "Normalisation"]
        dictionary = {"Normalization": True}
        match_value = utils.find_key_match_in_dict(keys, dictionary)
        self.assertTrue(match_value)

    def test_extract_key_match_from_dict_for_match(self):
        """ Test for using list of keys to get back value of
        one and only one matching key from dict with error handling wrapper
        """
        keys = ["Vanadium", "Normalization", "Normalisation"]
        dictionary = {"Normalization": True}
        match_value = utils.extract_key_match_from_dict(keys, dictionary)
        self.assertTrue(match_value)

    def test_extract_key_match_from_dict_raise_error_when_no_match(self):
        """ Test that we raise an error when no keys found in dict
        """
        keys = ["Vanadium", "Normalization", "Normalisation"]
        dictionary = {"Sample": True}
        with self.assertRaises(Exception):
            utils.extract_key_match_from_dict(keys, dictionary)

    def test_get_sample_when_match(self):
        """ Test extracting sample info from config
        """
        config = {"Sample": {"Runs": "10-20"}}
        sample_value = utils.get_sample(config)
        self.assertEqual(config["Sample"], sample_value)

    def test_get_sample_raise_error_when_no_match(self):
        """ Test that we raise an error when no Sample key found
        """
        config = {"BadKey": {"Runs": "10-20"}}
        with self.assertRaises(Exception):
            utils.get_sample(config)

    def test_get_normalization_when_match_for_vanadium(self):
        """ Test extracting vanadium info from config
        """
        config = {"Vanadium": {"Runs": "10-20"}}
        norm_value = utils.get_normalization(config)
        self.assertEqual(config["Vanadium"], norm_value)

    def test_get_normalization_when_match_for_normalization(self):
        """ Test extracting normalization info from config
        """
        config = {"Normalization": {"Runs": "10-20"}}
        norm_value = utils.get_normalization(config)
        self.assertEqual(config["Normalization"], norm_value)

    def test_get_normalization_when_match_for_normalisation(self):
        """ Test extracting normalisation info from config
        """
        config = {"Normalisation": {"Runs": "10-20"}}
        norm_value = utils.get_normalization(config)
        self.assertEqual(config["Normalisation"], norm_value)

    def test_get_normalization_raise_error_when_no_match(self):
        """ Test that we raise an error when no normalization keys found
        """
        config = {"BadKey": {"Runs": "10-20"}}
        with self.assertRaises(Exception):
            utils.get_normalization(config)
