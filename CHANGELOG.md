# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project attempts to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-05-17

### Added
- Initial release of SnakeByte interactive hex viewer
- Interactive hex and ASCII display with configurable bytes per line
- Support for multiple character encodings:
  - UTF-8, ASCII, Latin-1 (ISO-8859-1)
  - Windows encodings (CP1252, CP437)
  - Additional ISO encodings (ISO-8859-15, ISO-8859-2)
- Search functionality:
  - Hex pattern search (e.g., "48 65 6C 6C 6F")
  - ASCII text search
  - Case-sensitive and case-insensitive options
- Multiple color schemes:
  - Classic terminal (green on black)
  - Modern (blue/white)
  - High contrast
  - Monochrome
- Navigation controls:
  - Arrow keys for movement
  - Page Up/Down for fast scrolling
  - Home/End for file boundaries
  - Go-to address functionality
- Display modes:
  - Standard hex view with ASCII sidebar
  - Configurable bytes per line (8, 16, 32)
  - Address offset display
- Interactive help system (F1 key)
- Cross-platform compatibility (Windows, macOS, Linux)
- Single-file Python script - no external dependencies required

### Technical Details
- Requires Python 3.6 or later
- Uses only standard library modules
- Optimized for large file handling with efficient memory usage
- Supports files of any size through chunked reading

[1.0.0]: https://github.com/pjcigan/snakebyte/releases/tag/v1.0.0
