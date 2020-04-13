import itertools
import os

ROOT_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..'))


def compress_ints(line_nums):
    """ Function to compress list of ints with dashes
    Ex. [1,2,3,8,9,12] -> 1-3, 8-9, 12

    :param line_nums: List of integers to compress to string format
    :type line_nums: list(int)

    :return: String in compressed format for the list of integers
    :rtype: str
    """
    seq = []
    final = []
    last = 0

    for index, val in enumerate(line_nums):
        if last + 1 == val or index == 0:
            seq.append(val)
            last = val
        else:
            if len(seq) > 1:
                final.append(str(seq[0]) + '-' + str(seq[len(seq) - 1]))
            else:
                final.append(str(seq[0]))
            seq = []
            seq.append(val)
            last = val

        if index == len(line_nums) - 1:
            if len(seq) > 1:
                final.append(str(seq[0]) + '-' + str(seq[len(seq) - 1]))
            else:
                final.append(str(seq[0]))

    final_str = ', '.join(map(str, final))
    return final_str


def expand_ints(s):
    """ Function to expand string of ints with dashes
    Ex. "1-3, 8-9, 12" -> [1,2,3,8,9,12]

    :param s: run numbers to expand with '-' to indicate range
    :type s: str

    :return: List of expanded integers
    :rtype: list(int)
    """
    spans = (el.partition('-')[::2] for el in s.split(','))
    ranges = (range(int(s), int(e) + 1 if e else int(s) + 1)
              for s, e in spans)
    all_nums = itertools.chain.from_iterable(ranges)
    return list(all_nums)


def one_and_only_one(iterable):
    """Determine if iterable (ie list) has one and only one `True` value

    :param iterable: The iterable to check
    :type iterable: list

    :return: If there is one and only one True
    :rtype: bool
    """
    try:
        iterator = iter(iterable)
        has_true = any(iterator)
        has_another_true = any(iterator)
        return has_true and not has_another_true
    except Exception as e:
        print(e)
        raise


def find_key_match_in_dict(keys, dictionary):
    """ Check if one and only one of the keys is in the dictionary
    and return its value

    :param key: Keys we will check for in dictionary
    :type key: str
    :param dictionary: Dictionary to check
    :type dictionary: dict

    :return: Either the value in dictionary for the key or None if not found
    :rtype: value in dict or None
    """
    # Get the boolean for each key if it exists in the dictionary
    keys_exist_in_dict = map(lambda key: key in dictionary, keys)

    # If only one exists, return the match, else raise exception
    if one_and_only_one(keys_exist_in_dict):
        for key in keys:
            if key in dictionary:
                return dictionary[key]

    # None of the keys in the dictionary, return None
    return None


def extract_key_match_from_dict(keys, dictionary):
    """ Convienence function for extraction of one key from dictionary

    :param keys: Keys to check against dictionary
    :type keys: list
    :param dictionary: Dictionary to check
    "type dictionary: dict

    :return: The exctracted value
    :rtype: any
    """
    out = find_key_match_in_dict(keys, dictionary)
    if out:
        return out
    else:
        e = "No matching key found. Valid keys are {}".format(keys)
        raise Exception(e)


def get_sample(config):
    """ Extract the sample section from JSON input

    :param config: JSON input for reduction
    :type config: dict

    :return: The exctracted value for sample in the input
    :rtype: any
    """
    keys = ["Sample"]
    out = extract_key_match_from_dict(keys, config)
    return out


def get_normalization(config):
    """ Extract the normalization section from JSON input

    :param config: JSON input for reduction
    :type config: dict

    :return: The exctracted value for normalization in the input
    :rtype: any
    """
    keys = ["Normalization", "Normalisation", "Vanadium"]
    out = extract_key_match_from_dict(keys, config)
    return out
