# SEGD Python Library

A Python library for reading and writing geophysical data in the SEGD (Society of Exploration Geophysicists Data) format.

This project provides a robust, well-tested, and easy-to-use tool for handling SEGD files, focusing on the SEGD Rev 3.0 standard. The library is designed with a modular architecture to facilitate future expansion.

## Features

*   **SEGD Rev 3 Parsing**: Parses the mandatory General Header blocks (#1, #2, #3).
*   **SEGD Rev 3 Writing**: Serializes and writes the mandatory General Header blocks.
*   **Stream-Based I/O**: Operates on file-like objects (streams), making it flexible for use with files, in-memory buffers, or network streams.
*   **Tape Drive Support**: Includes a `TapeDevice` handler for interacting with Linux tape devices (e.g., `/dev/st0`), abstracting block-based I/O and filemarks.
*   **Pure Python**: Built with no external dependencies for the core library.

## Installation

To install the library locally, clone the repository and run pip:

```bash
git clone <repository_url>
cd segd-project
pip install .
```

## Usage

The library is designed to work with stream objects. You are responsible for opening and closing the file or device stream.

### Reading a SEGD File

The `SegDReader` class is used to read data from a stream.

```python
from segd.readers.rev3.reader import SegDReader
import pprint

try:
    with open('path/to/your/file.segd', 'rb') as f:
        reader = SegDReader(stream=f)

        # Read the three mandatory general headers
        gh1 = reader.read_general_header_1()
        gh2 = reader.read_general_header_2()
        gh3 = reader.read_general_header_3()

        print("--- General Header 1 ---")
        pprint.pprint(gh1.__dict__)

except FileNotFoundError:
    print("File not found.")
except IOError as e:
    print(f"Error reading file: {e}")

```
See `examples/read_segd_file.py` for a complete example.

### Writing a SEGD File

The `SegDWriter` class is used to write data to a stream. You first create instances of the header dataclasses.

```python
from segd.readers.rev3.writer import SegDWriter
from segd.readers.rev3.definitions import GeneralHeader1, GeneralHeader2, GeneralHeader3

# 1. Create your header data objects
gh1 = GeneralHeader1(file_number=1, format_code=8058, ...)
gh2 = GeneralHeader2(extended_file_number=1, ...)
gh3 = GeneralHeader3(time_zero_us=123456, ...)

# 2. Open a writable stream and write the headers
try:
    with open('path/to/new_file.segd', 'wb') as f:
        writer = SegDWriter(stream=f)
        writer.write_general_header_1(gh1)
        writer.write_general_header_2(gh2)
        writer.write_general_header_3(gh3)
        print("SEGD file created successfully.")
except IOError as e:
    print(f"Error writing to file: {e}")
```
See `examples/create_segd_file.py` for a complete example.


## Development

To set up a development environment, create a virtual environment and install the package in editable mode with its test dependencies.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install in editable mode with test dependencies
pip install -e ".[test]"
```
The testing dependencies are defined in `pyproject.toml` and currently include `pytest`.

### Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

## Creating a Portable Executable

To create a single-file, portable executable for Linux, you can use `PyInstaller`.

1.  **Install PyInstaller** (if you haven't already):
    ```bash
    pip install pyinstaller
    ```

2.  **Build the Executable**:
    From the root of the project directory, run the following command:
    ```bash
    pyinstaller --name Analicia --onefile --windowed --add-data "segd:segd" segd_copier/main_gui.py
    ```
    *   `--name Analicia`: Sets the name of the output executable.
    *   `--onefile`: Packages everything into a single executable file.
    *   `--windowed`: Prevents a console window from appearing when the GUI is run.
    *   `--add-data "segd:segd"`: This is crucial. It tells PyInstaller to bundle the entire `segd` package with the executable, which is necessary for the application to find its core library.

3.  **Run the Application**:
    The final executable will be located in the `dist/` directory. You can run it directly:
    ```bash
    ./dist/Analicia
    ```
