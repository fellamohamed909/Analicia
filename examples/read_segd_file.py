"""
Example script to read a SEGD file.

This script demonstrates how to use the SegDReader class to open
a SEGD file, parse its headers, and access its trace data.

Usage:
    python examples/read_segd_file.py <path_to_segd_file>
"""
import sys
import pprint
from segd.rev3.reader import SegDReader

def main():
    """
    Main function to read and print SEGD general headers.
    """
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path_to_segd_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, 'rb') as f:
            reader = SegDReader(stream=f)

            print("--- General Header Block #1 ---")
            gh1 = reader.read_general_header_1()
            pprint.pprint(gh1.__dict__)

            print("\n--- General Header Block #2 ---")
            gh2 = reader.read_general_header_2()
            pprint.pprint(gh2.__dict__)

            print("\n--- General Header Block #3 ---")
            gh3 = reader.read_general_header_3()
            pprint.pprint(gh3.__dict__)

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
