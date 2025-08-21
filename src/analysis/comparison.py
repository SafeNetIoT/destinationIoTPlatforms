from src.utils import *

logger = logging.getLogger(__name__)

def load_data(file_path):
    """
    Load data from a file (JSON or text format).

    Args:
        file_path (str): Path to the input file.

    Returns:
        data: Parsed data (set for text files, dict for JSON files).
    """
    try:
        if file_path.endswith(".json"):
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded JSON data from {file_path}")
            return data
        elif file_path.endswith(".txt"):
            with open(file_path, 'r') as f:
                data = set(line.strip() for line in f)
            logger.info(f"Loaded text data from {file_path}")
            return data
        else:
            raise ValueError("Unsupported file format. Use .json or .txt")
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return None

def compare_sets(set1, set2):
    """
    Compare two sets and return their differences and intersections.

    Args:
        set1 (set): First set.
        set2 (set): Second set.

    Returns:
        dict: Containing differences and intersections.
    """
    results = {
        "only_in_first": set1 - set2,
        "only_in_second": set2 - set1,
        "intersection": set1 & set2
    }
    logger.info("Comparison of sets completed.")
    return results

def compare_dicts(dict1, dict2):
    """
    Compare two dictionaries and return differences and intersections.

    Args:
        dict1 (dict): First dictionary.
        dict2 (dict): Second dictionary.

    Returns:
        dict: Containing keys only in the first, only in the second, and common keys with differing values.
    """
    only_in_first = {k: v for k, v in dict1.items() if k not in dict2}
    only_in_second = {k: v for k, v in dict2.items() if k not in dict1}
    differing_values = {
        k: {"first": dict1[k], "second": dict2[k]}
        for k in dict1.keys() & dict2.keys()
        if dict1[k] != dict2[k]
    }
    intersection = {
        k: dict1[k]
        for k in dict1.keys() & dict2.keys()
        if dict1[k] == dict2[k]
    }
    logger.info("Comparison of dictionaries completed.")
    return {
        "only_in_first": only_in_first,
        "only_in_second": only_in_second,
        "differing_values": differing_values,
        "intersection": intersection,
    }

def save_comparison_results(results, output_dir, file_prefix):
    """
    Save comparison results to files in JSON format.

    Args:
        results (dict): Comparison results.
        output_dir (str): Directory to save the results.
        file_prefix (str): Prefix for the output files.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{file_prefix}_comparison.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    logger.info(f"Comparison results saved to {output_file}")

def compare_domain_list(file1, file2, output_dir):
    """
    Compare two files and save the results.

    Args:
        file1 (str): Path to the first file.
        file2 (str): Path to the second file.
        output_dir (str): Directory to save the results.
    """
    data1 = load_data(file1)
    data2 = load_data(file2)

    if data1 is None or data2 is None:
        logger.error("One or both files could not be loaded.")
        return

    if isinstance(data1, set) and isinstance(data2, set):
        results = compare_sets(data1, data2)
    elif isinstance(data1, dict) and isinstance(data2, dict):
        results = compare_dicts(data1, data2)
    else:
        logger.error("Data types of the two files do not match or are unsupported.")
        return

    file_prefix = f"{os.path.splitext(os.path.basename(file1))[0]}_vs_{os.path.splitext(os.path.basename(file2))[0]}"
    save_comparison_results(results, output_dir, file_prefix)
