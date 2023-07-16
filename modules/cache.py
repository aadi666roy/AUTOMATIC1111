import json
import os.path
import threading

from modules.paths import data_path, script_path

cache_filename = os.path.join(data_path, "cache.json")
cache_data = None
cache_lock = threading.Lock()


def dump_cache():
    """
    Saves all cache data to a file.
    """

    with cache_lock:
        with open(cache_filename, "w", encoding="utf8") as file:
            json.dump(cache_data, file, indent=4)


def cache(subsection):
    """
    Retrieves or initializes a cache for a specific subsection.

    Parameters:
        subsection (str): The subsection identifier for the cache.

    Returns:
        dict: The cache data for the specified subsection.
    """

    global cache_data

    if cache_data is None:
        with cache_lock:
            if cache_data is None:
                if not os.path.isfile(cache_filename):
                    cache_data = {}
                else:
                    try:
                        with open(cache_filename, "r", encoding="utf8") as file:
                            cache_data = json.load(file)
                    except Exception:
                        os.replace(cache_filename, os.path.join(script_path, "tmp", "cache.json"))
                        print('[ERROR] issue occurred while trying to read cache.json, move current cache to tmp/cache.json and create new cache')
                        cache_data = {}

    s = cache_data.get(subsection, {})
    cache_data[subsection] = s

    return s


def cached_data_for_file(subsection, title, filename, func):
    """
    Retrieves or generates data for a specific file, using a caching mechanism.

    Parameters:
        subsection (str): The subsection of the cache to use.
        title (str): The title of the data entry in the subsection of the cache.
        filename (str): The path to the file to be checked for modifications.
        func (callable): A function that generates the data if it is not available in the cache.

    Returns:
        dict or None: The cached or generated data, or None if data generation fails.

    The `cached_data_for_file` function implements a caching mechanism for data stored in files.
    It checks if the data associated with the given `title` is present in the cache and compares the
    modification time of the file with the cached modification time. If the file has been modified,
    the cache is considered invalid and the data is regenerated using the provided `func`.
    Otherwise, the cached data is returned.

    If the data generation fails, None is returned to indicate the failure. Otherwise, the generated
    or cached data is returned as a dictionary.
    """

    existing_cache = cache(subsection)
    ondisk_mtime = os.path.getmtime(filename)

    entry = existing_cache.get(title)
    if entry:
        cached_mtime = existing_cache[title].get("mtime", 0)
        if ondisk_mtime > cached_mtime:
            entry = None

    if not entry:
        entry = func()
        if entry is None:
            return None

        entry['mtime'] = ondisk_mtime
        existing_cache[title] = entry

        dump_cache()

    return entry