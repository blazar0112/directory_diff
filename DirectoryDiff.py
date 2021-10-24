import argparse
import datetime
from enum import Enum, auto
import functools
import hashlib
import json
import os
import timeit

class DiffCategory(Enum):
    INPUT_EXTRA_ENTRY = auto()
    TARGET_EXTRA_ENTRY = auto()
    INPUT_FILE_TARGET_DIRECTORY = auto()
    TARGET_FILE_INPUT_DIRECTORY = auto()
    FILE_HASH_DIFF = auto()

def generate_hash(filepath):
    blocksize = 64 * 1024
    hashfunc = hashlib.md5()

    with open(filepath, 'rb') as fp:
        while True:
            data = fp.read(blocksize)
            if not data:
                break
            hashfunc.update(data)

    hexstring = hashfunc.hexdigest()
    return hexstring

def timed_by_timeit(time_name=None):
    """Print the runtime of the decorated function"""
    def decorator(func):
        nonlocal time_name
        if time_name is None:
            time_name = func.__name__

        @functools.wraps(func)
        def wrapper_timed_by_timeit(*args, **kwargs):
            start = timeit.default_timer()
            value = func(*args, **kwargs)
            end = timeit.default_timer()
            elapsed = str(datetime.timedelta(seconds=end-start))
            print(f'{time_name} time {elapsed}.')
            return value
        return wrapper_timed_by_timeit
    return decorator

create_hash_count = 0

@timed_by_timeit('[create_directory_info]')
def create_directory_info(directory, output_filename, human_readable):
    data = {}
    data['_metadata'] = {}
    data['_metadata']['directory'] = directory
    data['info'] = {}

    generate_directory_info(directory, directory, data['info'])

    with open(output_filename, 'w', encoding='utf-8') as output_file:
        if human_readable:
            json.dump(data, output_file, indent=4, sort_keys=True, ensure_ascii=False)
        else:
            json.dump(data, output_file)

    print('File hash count:', create_hash_count)

def generate_directory_info(scan_path, scan_dirname, data):
    data.setdefault(scan_dirname, {})

    for entry in os.scandir(scan_path):
        fullpath = os.path.abspath(os.path.join(scan_path, entry.name))
        if not entry.name.startswith('.') and entry.is_file():
            data[scan_dirname][entry.name] = generate_hash(fullpath)
            global create_hash_count
            create_hash_count += 1
        else:
            generate_directory_info(fullpath, entry.name, data[scan_dirname])

compare_summary = {}
for category in DiffCategory:
    compare_summary[category.name] = []

compare_hash_count = 0

@timed_by_timeit('[compare_directory_info]')
def compare_directory_info(directory, info_filename, summary_filename):
    with open(info_filename, encoding='utf-8') as info_file:
        directory_info = json.load(info_file)

    input_directory = directory_info['_metadata']['directory']

    diff_directory_info(directory, input_directory, '', directory_info['info'][input_directory])
    print('File hash count:', compare_hash_count)
    print('Compare TargetDirectory to DirectoryInfo file:')
    print('TargetDirectory:', directory)
    print('DirectoryInfo:', info_filename)
    is_all_same = True
    for category, entry_list in compare_summary.items():
        if entry_list:
            is_all_same = False
            print('Category [', category, ']: ', len(entry_list), ' entry(s).', sep='')

    if is_all_same:
        print('Content is same.')

    if summary_filename and not is_all_same:
        with open(summary_filename, 'w', encoding='utf-8') as output_file:
            json.dump(compare_summary, output_file, indent=4, sort_keys=True, ensure_ascii=False)

def diff_directory_info(target_directory, input_directory, depth, info):
    target_entry_list = [entry for entry in os.scandir(target_directory)]
    for entry in target_entry_list:
        if entry.name not in info:
            compare_summary[DiffCategory.TARGET_EXTRA_ENTRY.name].append(os.path.join(depth, entry.name))
            continue

        target_path = os.path.abspath(os.path.join(target_directory, entry.name))
        input_path = os.path.abspath(os.path.join(input_directory, entry.name))
        if not entry.name.startswith('.') and entry.is_file():
            if isinstance(info[entry.name], dict):
                compare_summary[DiffCategory.TARGET_FILE_INPUT_DIRECTORY.name].append(os.path.join(depth, entry.name))
            else:
                target_hash = generate_hash(target_path)
                global compare_hash_count
                compare_hash_count += 1
                if target_hash!=info[entry.name]:
                    compare_summary[DiffCategory.FILE_HASH_DIFF.name].append(os.path.join(depth, entry.name))
        else:
            if not isinstance(info[entry.name], dict):
                compare_summary[DiffCategory.INPUT_FILE_TARGET_DIRECTORY.name].append(os.path.join(depth, entry.name))
            else:
                next_depth = os.path.join(depth, entry.name)
                diff_directory_info(target_path, input_path, next_depth, info[entry.name])

    target_entry_name_list = [entry.name for entry in target_entry_list]
    for entry_name in info.keys():
        if entry_name not in target_entry_name_list:
            compare_summary[DiffCategory.INPUT_EXTRA_ENTRY.name].append(os.path.join(depth, entry_name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare directory to generated directory info.')
    parser.add_argument('directory', help='Directory to generate info or compare.')
    parser.add_argument('-o', '--output_info_filename', help='Generate directory info json file to <output_info_filename>.')
    parser.add_argument('-u', '--human_readable', help='Generate info file as human readable, indent by 4.', action='store_true')
    parser.add_argument('-i', '--info_filename', help='Compare directory with <info_filename>.')
    parser.add_argument('-s', '--summary_filename', help='Output compare summary file to <summary_filename> if differs.')
    args = parser.parse_args()

    if args.output_info_filename is None and args.info_filename is None:
        print('Requires at least one of output_info_filename or info_filename.')
        raise Exception('invalid argument')

    if not os.path.isdir(args.directory):
        print('Directory', args.directory, 'is not ad directory.')
        raise Exception('invalid argument')

    if args.output_info_filename:
        human_readable = False
        if args.human_readable:
            human_readable = True
        create_directory_info(args.directory, args.output_info_filename, human_readable)

    if args.info_filename:
        compare_directory_info(args.directory, args.info_filename, args.summary_filename)
