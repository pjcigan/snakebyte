# SnakeByte

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![GitHub release](https://img.shields.io/github/release/pjcigan/snakebyte.svg)](https://github.com/pjcigan/snakebyte/releases)
[![GitHub downloads](https://img.shields.io/github/downloads/pjcigan/snakebyte/total.svg)](https://github.com/pjcigan/snakebyte/releases)
[![Sponsor](https://img.shields.io/badge/Sponsor-%F0%9F%A7%AA-blue?logo=github&style=flat)](https://github.com/sponsors/pjcigan)

A terminal-based hex viewer for binary file analysis with special features for examining complex binary structures and Fortran data files.

![SnakeByte Logo](./images/SnakeByte_4.png)

## Features

- **Intuitive Navigation**: Move through binary files with arrow keys, page up/down, and direct jumps
- **Multi-Format Search**: Find values whether they're stored as text, integers, or floating-point numbers
- **Structure Analysis**: Shift byte alignment to identify data structures in misaligned files
- **Endianness Control**: Toggle between little and big endian interpretation of values
- **Value Interpretation**: See data as 16/32-bit integers and IEEE floating-point numbers
- **Customizable Display**: Toggle features and adapt the view to your needs
- **Color Themes**: Multiple color schemes for light and dark terminal backgrounds
- **Encoding Support**: Switch between different character encodings


## Installation

No external dependencies required beyond the Python standard library.

```bash
# Clone the repository
git clone https://github.com/pjcigan/snakebyte.git

# Run as a standalone script:
python /path/to/snakebyte.py your_file.bin

# Or, make the script executable
cd snakebyte
chmod +x snakebyte.py

# Run directly
./snakebyte.py your_binary_file
```

Alternatively, install for use system-wide using the install bash script included in this repository:

```bash
chmod +x install_script.sh
./install_script.sh

# Make executable
sudo chmod +x /usr/local/bin/snakebyte

# Run from anywhere
snakebyte your_file.bin
```

## Basic Usage

```bash
python snakebyte.py <filename>
```

### Command Line Arguments

```
positional arguments:
  filename              Binary file to view

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Custom encodings configuration file
```

### Examples

```bash
# View a binary file
python snakebyte.py data.bin

# With custom encodings configuration
python snakebyte.py data.bin -c my_encodings.json
```

## Navigation and Controls

### Navigation

| Key           | Action                                |
|---------------|---------------------------------------|
| ↑, ↓, ←, →    | Move cursor up/down/left/right        |
| Page Up/Down  | Scroll one page up/down               |
| Home/End      | Jump to beginning/end of file         |
| j             | Jump to specific offset or percentage |

### Search

| Key           | Action                                |
|---------------|---------------------------------------|
| s             | Search for string or numeric value    |
| n             | Next search result                    |
| p             | Previous search result                |
| i             | Investigate current search result     |

### Display

| Key           | Action                                    |
|---------------|-------------------------------------------|
| [/]           | Shift display left/right by 1 byte        |
| {/}           | Shift display left/right by 4 bytes       |
| \\            | Reset display shift                       |
| </\>          | Toggle between little/big endian          |
| e             | Cycle through available encodings         |
| v             | Toggle value interpretation display       |
| c             | Cycle through color schemes               |
| h             | Show/hide help screen                     |
| q             | Quit                                      |

## Features in Detail

### Multi-format Search

The search functionality can find values in multiple formats:

- **String/ASCII**: Searches for the literal characters
- **Hexadecimal**: Prefix with '0x' to search for specific hex values
- **Numeric**: For numbers, it will find them regardless of storage format:
  - As text (ASCII representation)
  - As 16-bit integer (little or big endian)
  - As 32-bit integer (little or big endian)
  - As 32-bit float (little or big endian)

```
Examples:
  s 1234      # Find the value 1234 in any format
  s 0xDEADBEEF # Find this exact hex sequence
  s PARFL     # Find text string "PARFL"
```

### Search Result Investigation

When you've performed a search and found results, you can:

1. Press 'i' to activate investigation mode
2. View detailed information about how the match was found
3. See offset, match type, and interpreted value
4. Navigate between results with 'n' and 'p'

This is particularly useful for understanding how values are stored in your binary file.

### Byte Alignment Shifting

If you're examining files with non-standard structure alignment:

1. Use `[` and `]` to shift the display by 1 byte at a time
2. Look for patterns or specific markers
3. Use `{` and `}` for quicker shifting by 4 bytes
4. Reset with `\` when done

This is especially useful for analyzing complex binary formats or Fortran data files where values might not be aligned on standard boundaries.

### Custom Encodings

SnakeByte supports custom encodings through a JSON configuration file:

```json
{
    "encodings": [
        "shift_jis",
        "euc_jp",
        {
            "name": "custom_encoding",
            "module": "special_codec"
        }
    ]
}
```

Use the `-c` flag to specify a configuration file, or place it in:
- `~/.snakebyte_encodings.json`
- `./snakebyte_encodings.json`

## Add-on Modules

### SnakeByte CJK

For working with files containing CJK (Chinese, Japanese, Korean) characters, an extended version is available:

```bash
python snakebyte_cjk.py <filename> [--encoding ENCODING]
```

**Additional features:**
- Enhanced CJK character display
- Additional CJK encodings pre-configured
- Special highlighting for CJK characters
- Command-line option to set initial encoding

To enable this extension, simply use `snakebyte_cjk.py` instead of `snakebyte.py`.

## Use Cases

### Fortran Data File Analysis

SnakeByte is particularly useful for examining Fortran data files, which often have:

- Block markers like "SOCOM", "PARFL" with varying alignment
- Mixed integer and float data
- Varying endianness

The alignment shift and multi-format search features make it easy to locate and understand these structures.

### General Binary Analysis

You can use SnakeByte for:

- Inspecting file headers and formats
- Analyzing data structures in binary files
- Examining memory dumps or logs
- Reverse engineering file formats

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ☕ Support This Project

If something here made your life easier, saved you a headache, or helped you look cool in front of your coworkers — consider sponsoring.  Your support helps fund critical productivity infrastructure like coffee, snacks, and the occasional AI tool that pretends to be a rubber duck but actually answers back.  No pressure, this is totally optional. The code's free, the vibe's friendly. But if you're feeling generous, I will certainly wish many good karma cookies in your general direction.

[Sponsor me on GitHub](https://github.com/sponsors/pjcigan)

## License

This project is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License - see the [LICENSE](license.md) file for details.

## Acknowledgments

* Created by Phil Cigan (2025)
