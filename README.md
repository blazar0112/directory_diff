# Directory Diff

- Python utility to compare directory with stored info of another directory.
    - Store directory info to a json file, can compare later directory or other PC's directory.
    - Use relative structure.

## How to use

- In power shell
- To see command help:
    ```
    python DirectoryDiff.py -h
    ```
- Generate directory info to `directory_info.json`:
    ```
    python DirectoryDiff.py dir_release -o directory_info.json
    ```
- Compare directory with existing info:
    ```
    python DirectoryDiff.py dir_client -i directory_info.json -s summary.json
    ```

## Relative structure

- Assume following directory structures:

- dir_release `D:\my_great_work`:
    ```
    D:\my_great_work\
        a\
            b.txt
        c.txt
        d\
    ```
- dir_client `E:\downloaded_work` (may not on same PC):
    ```
    E:\downloaded_work\
        a\
            b.txt (*modified)
        e.txt
        d
    ```

- Generated directory info of dir_release (human readable mode):
    ```json
    {
        "_metadata": {
            "directory": "D:\\my_great_work"
        },
        "info": {
            "D:\\my_great_work": {
                "a": {
                    "b.txt": "c4ca4238a0b923820dcc509a6f75849b"
                },
                "c.txt": "d41d8cd98f00b204e9800998ecf8427e",
                "d": {}
            }
        }
    }
    ```

- Client can get above Json file to verify if their directory content is same or not:
    ```
    python DirectoryDiff.py E:\downloaded_work -i directory_info.json -s summary.json
    File hash count: 1
    Compare TargetDirectory to DirectoryInfo file:
    TargetDirectory: E:\downloaded_work
    DirectoryInfo: directory_info.json
    Category [INPUT_EXTRA_ENTRY]: 1 entry(s).
    Category [TARGET_EXTRA_ENTRY]: 1 entry(s).
    Category [TARGET_FILE_INPUT_DIRECTORY]: 1 entry(s).
    Category [FILE_HASH_DIFF]: 1 entry(s).
    [compare_directory_info] time 0:00:00.001365.
    ```
- `summary.json` stores compare result by listing each diff category and it's entry in relative path:
    ```json
    {
        "FILE_HASH_DIFF": [
            "a\\b.txt"
        ],
        "INPUT_EXTRA_ENTRY": [
            "c.txt"
        ],
        "INPUT_FILE_TARGET_DIRECTORY": [],
        "TARGET_EXTRA_ENTRY": [
            "e.txt"
        ],
        "TARGET_FILE_INPUT_DIRECTORY": [
            "d"
        ]
    }
    ```
