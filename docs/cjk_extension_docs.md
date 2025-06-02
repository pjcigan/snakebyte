# SnakeByte CJK Extension

## Enhanced Binary File Viewing with CJK Support

This extension to SnakeByte adds comprehensive support for viewing binary files containing CJK (Chinese, Japanese, Korean) character encodings.

![SnakeByte CJK Screenshot](screenshot_cjk_placeholder.png)

## Additional Features

Beyond the standard SnakeByte functionality, this extension provides:

- **Enhanced CJK Character Display**: Special handling and visualization of CJK characters
- **CJK-Optimized Encodings**: Prioritized encodings commonly used for Japanese, Chinese, and Korean text
- **Visual Distinction**: Color-coded display of CJK characters for easy identification
- **Multi-byte Character Support**: Properly handles multi-byte character sets in various encodings

## Included Encodings

The CJK version comes pre-configured with these additional encodings:

- `shift_jis` (Japanese)
- `euc_jp` (Japanese)
- `gb2312` (Simplified Chinese)
- `big5` (Traditional Chinese)
- `cp949` (Korean)

## Installation

Same as the standard SnakeByte, but use the CJK version:

```bash
# Run the CJK version
python snakebyte_cjk.py your_binary_file
```

## Usage

```bash
python snakebyte_cjk.py <filename> [--encoding ENCODING]
```

### Command Line Arguments

```
positional arguments:
  filename              Binary file to view

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Custom encodings configuration file
  --encoding ENCODING, -e ENCODING
                        Initial encoding to use (default: ascii)
```

### Examples

```bash
# View a Japanese file with Shift-JIS encoding
python snakebyte_cjk.py japanese_text.bin --encoding shift_jis

# View a Chinese file with GB2312 encoding
python snakebyte_cjk.py chinese_text.bin --encoding gb2312
```

## Controls

All standard SnakeByte controls work, with these enhancements:

- **CJK highlighting**: CJK characters appear with distinct highlighting
- **Encoding cycling**: The `e` key cycles through encodings (CJK encodings come earlier in the cycle)

## Terminal Compatibility

The CJK version works best in terminals with:

1. UTF-8 support
2. A font that includes CJK glyphs

For optimal display:
- On Linux: Use a terminal with a font like Noto Sans Mono CJK
- On macOS: The default terminal fonts already support CJK

## Known Issues

- Some terminals may not correctly display certain CJK characters
- Certain combinations of terminal settings and encodings might cause display issues

## Terminal Testing

If you're having trouble displaying CJK characters, you can run the included test script:

```bash
# Test your terminal's CJK support
chmod +x terminal_cjk_test.sh
./terminal_cjk_test.sh
```

This script will help identify if your terminal has the necessary capabilities to display CJK characters properly.

## Dependencies

No additional dependencies beyond the standard Python library are required. However, for the best experience with CJK files, we recommend:

1. A terminal with UTF-8 support
2. A font that includes CJK character ranges
3. Proper locale settings (e.g., `LC_ALL=en_US.UTF-8`)
