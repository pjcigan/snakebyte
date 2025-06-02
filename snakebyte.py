#!/usr/bin/env python3
"""
SnakeByte - Advanced Terminal-based Binary File Viewer

A powerful terminal-based hex viewer specifically designed for analyzing binary files,
with special features for examining Fortran data files and complex binary structures.

Copyright (c) 2025 Phil Cigan
License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
https://creativecommons.org/licenses/by-sa/4.0/

You are free to:
- Share: copy and redistribute the material in any medium or format
- Adapt: remix, transform, and build upon the material for any purpose, even commercially
  
Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, 
  and indicate if changes were made.
- ShareAlike: If you remix, transform, or build upon the material, you must 
  distribute your contributions under the same license as the original.
"""

__version__ = 1.0

import os
import sys
import string
import curses
import struct
import argparse
import json

class BinaryFileViewer:
    """
    A terminal-based hex viewer with advanced navigation, search, and analysis features.
    Designed for examining binary file structures, particularly Fortran data files.
    """
    
    def __init__(self, filename):
        """Initialize with the path to a binary file"""
        self.filename = filename
        self.file_size = os.path.getsize(filename)
        self.bytes_per_line = 16
        self.current_offset = 0
        self.display_shift = 0  # Number of bytes to shift the display (for alignment)
        self.search_pattern = None
        self.search_results = []
        self.search_result_types = []  # Store how each match was found
        self.current_search_idx = -1
        
        # Encoding support
        self.encodings = [
            'ascii',
            'utf-8',
            'latin-1',  # ISO-8859-1
            'cp1252',   # Windows-1252
            'utf-16-le',
            'utf-16-be',
            'utf-32-le',
            'utf-32-be'
        ]
        self.encoding_idx = 0  # Start with ascii
        self.encoding = self.encodings[self.encoding_idx]
        
        self.endian = 'little'   # Default endianness (little or big)
        self.show_values = True  # Whether to show numeric interpretations
        self.color_scheme = 0    # Color scheme (0=default, 1=light theme, 2=dark theme)
        
        # Pre-load the entire file for performance
        with open(filename, 'rb') as f:
            self.file_content = f.read()
    
    def load_custom_encodings(self, config_file=None):
        """Load custom encodings from config file"""
        if config_file is None:
            # Look for default config in user home or current directory
            default_paths = [
                os.path.expanduser("~/.snakebyte_encodings.json"),
                "snakebyte_encodings.json"
            ]
            for path in default_paths:
                if os.path.exists(path):
                    config_file = path
                    break
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                if 'encodings' in config:
                    for enc in config['encodings']:
                        if isinstance(enc, str):
                            # Simple encoding name
                            if enc not in self.encodings:
                                self.encodings.append(enc)
                        elif isinstance(enc, dict) and 'name' in enc:
                            # Complex encoding with potential module dependency
                            name = enc['name']
                            if 'module' in enc:
                                try:
                                    # Try to import required module
                                    __import__(enc['module'])
                                    if name not in self.encodings:
                                        self.encodings.append(name)
                                except ImportError:
                                    print(f"Warning: Couldn't load module {enc['module']} for encoding {name}")
                return True
            except Exception as e:
                print(f"Error loading custom encodings: {str(e)}")
                return False
        return False
    
    def cycle_encoding(self):
        """Cycle to the next available encoding"""
        self.encoding_idx = (self.encoding_idx + 1) % len(self.encodings)
        self.encoding = self.encodings[self.encoding_idx]
        return self.encoding
    
    def display_printable(self, char_byte):
        """
        Convert a byte to a printable character or a dot if not printable
        Returns (character, is_error) tuple
        """
        try:
            char = char_byte.decode(self.encoding)
            if char in string.printable and char not in '\t\n\r\v\f':
                return char, False  # No encoding error
            return '.', False  # Not printable, but not an encoding error
        except (UnicodeDecodeError, LookupError):
            # UnicodeDecodeError: if byte can't be decoded with current encoding
            # LookupError: if encoding isn't recognized
            return '?', True  # Indicate encoding error
    
    def format_line(self, offset, data):
        """
        Format a line of binary data with offset, hex and char representation
        Returns (line_string, error_positions) tuple
        """
        # Address column
        line = f"{offset:08x}: "
        
        # Apply display shift for the visual representation only
        if self.display_shift != 0:
            # Get shifted data (moving the viewing "window" by self.display_shift bytes)
            shift_start = max(0, offset - self.display_shift)
            shift_end = min(self.file_size, shift_start + self.bytes_per_line)
            display_data = self.file_content[shift_start:shift_end]
            
            # Add padding if needed when near the beginning of the file
            if offset < self.display_shift:
                display_data = b'\x00' * (self.display_shift - offset) + display_data
                display_data = display_data[:self.bytes_per_line]
                
            # Use the shifted data for display, but keep original offset
        else:
            display_data = data
        
        # Hex values
        hex_section = ""
        for i, byte in enumerate(display_data):
            hex_section += f"{byte:02x} "
            if i == 7:  # Add extra space in the middle for readability
                hex_section += " "
        
        # Pad hex section if incomplete line
        hex_section = hex_section.ljust(3 * self.bytes_per_line + 2)
        line += hex_section
        
        # Character representation
        char_section = "│"
        error_positions = []  # Track positions with encoding errors
        
        for i, byte in enumerate(display_data):
            char, is_error = self.display_printable(bytes([byte]))
            char_section += char
            if is_error:
                error_positions.append(i)  # Store position of encoding error
                
        char_section += "│"
        
        result = line + " " + char_section
        
        # Add interpreted values if enabled
        if self.show_values and len(display_data) >= 4:
            try:
                # Integer interpretations (16-bit and 32-bit)
                if len(display_data) >= 2:
                    int16_val = int.from_bytes(display_data[:2], byteorder=self.endian)
                    result += f" int16: {int16_val}"
                
                if len(display_data) >= 4:
                    int32_val = int.from_bytes(display_data[:4], byteorder=self.endian)
                    result += f" int32: {int32_val}"
                
                # Float interpretation (32-bit)
                if len(display_data) >= 4:
                    # Convert to float (assuming IEEE 754 format)
                    fmt = '<f' if self.endian == 'little' else '>f'
                    float_val = struct.unpack(fmt, display_data[:4])[0]
                    result += f" float: {float_val:.6g}"
            except Exception:
                # Skip value interpretations if there's an error
                pass
                
        return result, error_positions
    
    def search(self, pattern, from_offset=0):
        """
        Search for a pattern in the file (can be string, bytes, or numeric value)
        
        Supports multiple search modes:
        - Text string (searched as ASCII)
        - Hexadecimal string (if prefixed with '0x')
        - Numeric values (searched in multiple formats)
        
        Returns a list of tuples: (offset, match_type)
        where match_type is 'ascii', 'int16le', 'int16be', 'int32le', 'int32be', 'hex', etc.
        """
        self.search_pattern = pattern
        self.search_results = []
        self.search_result_types = []  # Store how each match was found
        self.current_search_idx = -1
        
        # Check if it's a hex pattern
        if isinstance(pattern, str) and pattern.lower().startswith('0x'):
            try:
                # Convert hex string to bytes
                hex_val = pattern[2:]  # Remove '0x'
                # Pad to even length if necessary
                if len(hex_val) % 2 != 0:
                    hex_val = '0' + hex_val
                search_bytes = bytes.fromhex(hex_val)
                self._append_search_results(search_bytes, from_offset, 'hex')
                
                if self.search_results:
                    self.current_search_idx = 0
                    self.current_offset = self.search_results[0]
                    return True
                return False
            except ValueError:
                return False
        # Check if it's a numeric pattern
        elif isinstance(pattern, str) and pattern.isdigit():
            # Try to find it as a string first
            search_bytes_ascii = pattern.encode(self.encoding)
            
            # Also try to find it as a 16-bit integer (little and big endian)
            try:
                num_val = int(pattern)
                search_bytes_int16_le = num_val.to_bytes(2, byteorder='little')
                search_bytes_int16_be = num_val.to_bytes(2, byteorder='big')
                search_bytes_int32_le = num_val.to_bytes(4, byteorder='little')
                search_bytes_int32_be = num_val.to_bytes(4, byteorder='big')
                
                # Search for all formats
                self._append_search_results(search_bytes_ascii, from_offset, 'ascii')
                self._append_search_results(search_bytes_int16_le, from_offset, 'int16le')
                self._append_search_results(search_bytes_int16_be, from_offset, 'int16be')
                self._append_search_results(search_bytes_int32_le, from_offset, 'int32le')
                self._append_search_results(search_bytes_int32_be, from_offset, 'int32be')
                
                # Also try as float if it could be interpreted as one
                try:
                    float_val = float(pattern)
                    float_bytes_le = struct.pack('<f', float_val)
                    float_bytes_be = struct.pack('>f', float_val)
                    self._append_search_results(float_bytes_le, from_offset, 'float32le')
                    self._append_search_results(float_bytes_be, from_offset, 'float32be')
                except (ValueError, struct.error):
                    pass  # Skip if not a valid float
                
                if self.search_results:
                    self.current_search_idx = 0
                    self.current_offset = self.search_results[0]
                    return True
                return False
            except (ValueError, OverflowError):
                # If it's too big for 16/32 bits, just search as ASCII
                self._append_search_results(search_bytes_ascii, from_offset, 'ascii')
        else:
            # Regular string search
            if isinstance(pattern, str):
                search_bytes = pattern.encode(self.encoding)
            else:
                search_bytes = pattern
            self._append_search_results(search_bytes, from_offset, 'ascii')
        
        if self.search_results:
            self.current_search_idx = 0
            self.current_offset = self.search_results[0]
            return True
        return False
    
    def _append_search_results(self, pattern, from_offset=0, match_type='unknown'):
        """Helper method to find all occurrences of a pattern and add them to results"""
        start = from_offset
        while start < self.file_size:
            pos = self.file_content.find(pattern, start)
            if pos == -1:
                break
            self.search_results.append(pos)
            self.search_result_types.append(match_type)
            start = pos + 1
    
    def next_search_result(self):
        """Jump to the next search result"""
        if not self.search_results:
            return False
        
        self.current_search_idx = (self.current_search_idx + 1) % len(self.search_results)
        self.current_offset = self.search_results[self.current_search_idx]
        return True
    
    def prev_search_result(self):
        """Jump to the previous search result"""
        if not self.search_results:
            return False
        
        self.current_search_idx = (self.current_search_idx - 1) % len(self.search_results)
        self.current_offset = self.search_results[self.current_search_idx]
        return True
        
    def run(self, stdscr=None):
        """Run the viewer in the terminal using curses"""
        if stdscr is None:
            return curses.wrapper(self.run)
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        stdscr.clear()
        stdscr.refresh()
        
        # Initialize colors if terminal supports them
        self.has_colors = False
        try:
            if curses.has_colors():
                self.has_colors = True
                curses.start_color()
                curses.use_default_colors()
                
                # Define color pairs that work well in both light and dark themes
                # For light themes
                if self.color_scheme == 1:
                    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)      # Current line
                    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Current position
                    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)       # Search hit
                    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Info line
                    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)       # Encoding error
                # For dark themes
                elif self.color_scheme == 2:
                    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Current line
                    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Current position
                    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)    # Search hit
                    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Info line
                    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)       # Encoding error
                # Default - high contrast that works in most terminals
                else:
                    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Current line
                    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Current position
                    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_MAGENTA)   # Search hit
                    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)     # Info line
                    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)       # Encoding error
        except Exception:
            self.has_colors = False
        
        # Get terminal dimensions
        max_y, max_x = stdscr.getmaxyx()
        content_height = max_y - 4  # Reserve last three lines for status and one for help/info
        
        # Feature toggle states
        show_help = False
        show_investigate = False
        
        # Main loop
        running = True
        while running:
            try:
                stdscr.clear()
                
                # Display file content
                line_offset = self.current_offset - (self.current_offset % self.bytes_per_line)
                
                # Calculate which byte in the line is the current position
                current_pos_in_line = self.current_offset % self.bytes_per_line
                
                # Check if any search result is on the current page
                search_positions = {}
                if self.search_results:
                    for i, pos in enumerate(self.search_results):
                        # Get the line offset and position in line for this search result
                        result_line_offset = pos - (pos % self.bytes_per_line)
                        pos_in_line = pos % self.bytes_per_line
                        
                        # Check if this result is on the current page
                        if (line_offset <= result_line_offset < 
                            line_offset + content_height * self.bytes_per_line):
                            # Calculate line index on screen
                            line_idx = (result_line_offset - line_offset) // self.bytes_per_line
                            search_positions[(line_idx, pos_in_line)] = i  # Store result index
                
                for i in range(content_height):
                    offset = line_offset + i * self.bytes_per_line
                    if offset >= self.file_size:
                        break
                    
                    end_offset = min(offset + self.bytes_per_line, self.file_size)
                    data = self.file_content[offset:end_offset]
                    
                    line, error_positions = self.format_line(offset, data)
                    
                    # Determine if this line contains the current position or search results
                    is_current_line = (offset <= self.current_offset < offset + self.bytes_per_line)
                    
                    # Base formatting for the line
                    if is_current_line:
                        if self.has_colors:
                            attr = curses.color_pair(1)  # Highlight current line
                        else:
                            attr = curses.A_REVERSE
                    else:
                        attr = curses.A_NORMAL
                    
                    try:
                        # Display the line with appropriate highlighting
                        stdscr.addstr(i, 0, line, attr)
                    except curses.error:
                        # Handle overflows
                        try:
                            stdscr.addstr(i, 0, line[:max_x-1], attr)
                        except:
                            pass
                    
                    # Highlight the current position with a different color/attribute if it's on this line
                    if is_current_line:
                        try:
                            # Calculate position of current byte in the displayed line
                            hex_start = 10  # Offset of the hex values start (after the address)
                            byte_pos = hex_start + current_pos_in_line * 3  # Each byte takes 3 chars (2 hex + 1 space)
                            if current_pos_in_line > 7:
                                byte_pos += 1  # Account for extra space in the middle
                            
                            # Highlight the hex value of the current byte
                            if self.has_colors:
                                stdscr.addstr(i, byte_pos, f"{self.file_content[self.current_offset]:02x}", 
                                             curses.color_pair(2) | curses.A_BOLD)
                            else:
                                stdscr.addstr(i, byte_pos, f"{self.file_content[self.current_offset]:02x}", 
                                             curses.A_BOLD | curses.A_UNDERLINE)
                            
                            # Highlight the character representation
                            char_start = hex_start + 3 * self.bytes_per_line + 3  # Start of character section
                            char_pos = char_start + current_pos_in_line + 1  # +1 for the | character
                            
                            # Check if we're within file boundaries
                            if self.current_offset < self.file_size:
                                char, is_error = self.display_printable(bytes([self.file_content[self.current_offset]]))
                                if self.has_colors:
                                    stdscr.addstr(i, char_pos, char, curses.color_pair(2) | curses.A_BOLD)
                                else:
                                    stdscr.addstr(i, char_pos, char, curses.A_BOLD | curses.A_UNDERLINE)
                        except curses.error:
                            pass
                    
                    # Highlight any search results on this line
                    for j in range(min(self.bytes_per_line, len(data))):
                        if (i, j) in search_positions:
                            try:
                                # Similar calculations as above for byte and char positions
                                hex_start = 10
                                byte_pos = hex_start + j * 3
                                if j > 7:
                                    byte_pos += 1
                                
                                char_start = hex_start + 3 * self.bytes_per_line + 3
                                char_pos = char_start + j + 1
                                
                                # Highlight the hex value
                                if self.has_colors:
                                    stdscr.addstr(i, byte_pos, f"{data[j]:02x}", 
                                                 curses.color_pair(3) | curses.A_BOLD)
                                else:
                                    stdscr.addstr(i, byte_pos, f"{data[j]:02x}", 
                                                 curses.A_REVERSE | curses.A_UNDERLINE)
                                
                                # Highlight the character representation
                                char, is_error = self.display_printable(bytes([data[j]]))
                                if self.has_colors:
                                    stdscr.addstr(i, char_pos, char, curses.color_pair(3) | curses.A_BOLD)
                                else:
                                    stdscr.addstr(i, char_pos, char, curses.A_REVERSE | curses.A_UNDERLINE)
                            except curses.error:
                                pass
                    
                    # Highlight encoding errors
                    for j in error_positions:
                        if j < len(data):
                            try:
                                # Calculate position in the character representation section
                                char_start = hex_start + 3 * self.bytes_per_line + 3
                                char_pos = char_start + j + 1  # +1 for the | character
                                
                                # Highlight with the error color
                                if self.has_colors:
                                    stdscr.addstr(i, char_pos, "?", curses.color_pair(5) | curses.A_BOLD)
                                else:
                                    stdscr.addstr(i, char_pos, "?", curses.A_REVERSE | curses.A_BLINK)
                            except curses.error:
                                pass
                
                # File info status line (top status line)
                file_status = f" File: {self.filename} | Size: {self.file_size:,} bytes | "
                file_status += f"Offset: {self.current_offset:,}/{self.file_size:,} ({self.current_offset/self.file_size:.1%}) | "
                
                if self.display_shift != 0:
                    file_status += f"Shift: {self.display_shift} bytes | "
                
                # Show endianness and encoding
                file_status += f"Endian: {self.endian} | "
                file_status += f"Encoding: {self.encoding}"
                
                # Command menu status line (middle status line)
                if show_help:
                    command_status = " Navigation: Arrows=Move | Home/End=Start/End | PgUp/PgDown=Page | j=Jump | [/]=Shift ±1byte | {/}=Shift ±4bytes"
                    command_status2 = " Commands: q=Quit | s=Search | n/p=Next/Prev | </>=Endian | e=Encoding | v=Values | i=Investigate | c=Color | h=Help"
                else:
                    command_status = " h=Help | q=Quit | j=Jump | s=Search | n/p=Next/Prev | i=Investigate | e=Encoding | c=Color | v=Values"
                    if self.search_results:
                        command_status2 = f" Search: Result {self.current_search_idx + 1}/{len(self.search_results)}"
                    else:
                        command_status2 = ""
                
                # Display file info status line
                try:
                    if self.has_colors:
                        stdscr.addstr(max_y - 4, 0, file_status[:max_x-1], curses.color_pair(1))
                    else:
                        stdscr.addstr(max_y - 4, 0, file_status[:max_x-1], curses.A_REVERSE)
                except curses.error:
                    try:
                        stdscr.addstr(max_y - 4, 0, file_status[:max_x-1])
                    except:
                        pass
                
                # Display command menu status line
                try:
                    if self.has_colors:
                        stdscr.addstr(max_y - 3, 0, command_status[:max_x-1], curses.color_pair(1))
                        if command_status2:
                            stdscr.addstr(max_y - 2, 0, command_status2[:max_x-1], curses.color_pair(1))
                    else:
                        stdscr.addstr(max_y - 3, 0, command_status[:max_x-1], curses.A_REVERSE)
                        if command_status2:
                            stdscr.addstr(max_y - 2, 0, command_status2[:max_x-1], curses.A_REVERSE)
                except curses.error:
                    try:
                        stdscr.addstr(max_y - 3, 0, command_status[:max_x-1])
                        if command_status2:
                            stdscr.addstr(max_y - 2, 0, command_status2[:max_x-1])
                    except:
                        pass
                
                # Show investigation info on bottom line
                if show_investigate and self.search_results and self.current_search_idx >= 0:
                    try:
                        curr_pos = self.search_results[self.current_search_idx]
                        curr_type = self.search_result_types[self.current_search_idx]
                        investigate_info = f" Search hit: offset 0x{curr_pos:x} ({curr_pos}) | "
                        investigate_info += f"Found as: {curr_type} | "
                        
                        # Extract the matching bytes to show the actual value
                        pattern_length = 0
                        if "int16" in curr_type:
                            pattern_length = 2
                        elif "int32" in curr_type or "float" in curr_type:
                            pattern_length = 4
                        elif curr_type == 'ascii':
                            pattern_length = len(str(self.search_pattern).encode(self.encoding))
                        
                        if pattern_length > 0 and curr_pos + pattern_length <= self.file_size:
                            match_bytes = self.file_content[curr_pos:curr_pos+pattern_length]
                            investigate_info += f"Bytes: {match_bytes.hex()} | "
                            
                            # Interpret as the found type
                            if "int16" in curr_type:
                                endian = 'little' if 'le' in curr_type else 'big'
                                value = int.from_bytes(match_bytes, byteorder=endian)
                                investigate_info += f"Value: {value} | "
                            elif "int32" in curr_type:
                                endian = 'little' if 'le' in curr_type else 'big'
                                value = int.from_bytes(match_bytes, byteorder=endian)
                                investigate_info += f"Value: {value} | "
                            elif "float" in curr_type:
                                fmt = '<f' if 'le' in curr_type else '>f'
                                try:
                                    value = struct.unpack(fmt, match_bytes)[0]
                                    investigate_info += f"Value: {value:.6g} | "
                                except struct.error:
                                    pass
                        
                        # Display investigation info
                        if self.has_colors:
                            stdscr.addstr(max_y - 1, 0, investigate_info[:max_x-1], curses.color_pair(4))
                        else:
                            stdscr.addstr(max_y - 1, 0, investigate_info[:max_x-1], curses.A_REVERSE)
                    except Exception:
                        pass
                elif show_help:
                    # Show detailed help
                    try:
                        help_info = (
                            "[ ] Shift by 1 byte | { } Shift by 4 bytes | \\ Reset shift | v Toggle values | " +
                            "Use Space for details | To exit help: press h again"
                        )
                        if self.has_colors:
                            stdscr.addstr(max_y - 1, 0, help_info[:max_x-1], curses.color_pair(4))
                        else:
                            stdscr.addstr(max_y - 1, 0, help_info[:max_x-1], curses.A_NORMAL)
                    except curses.error:
                        pass
                else:
                    # Clear bottom line when not showing special info
                    try:
                        stdscr.addstr(max_y - 1, 0, " " * (max_x - 1))
                    except curses.error:
                        pass
                
                # Handle keyboard input
                try:
                    key = stdscr.getch()
                
                    if key == ord('q'):
                        running = False
                    
                    elif key == curses.KEY_UP:
                        self.current_offset = max(0, self.current_offset - self.bytes_per_line)
                    
                    elif key == curses.KEY_DOWN:
                        self.current_offset = min(self.file_size - 1, self.current_offset + self.bytes_per_line)
                    
                    elif key == curses.KEY_LEFT:
                        self.current_offset = max(0, self.current_offset - 1)
                    
                    elif key == curses.KEY_RIGHT:
                        self.current_offset = min(self.file_size - 1, self.current_offset + 1)
                    
                    elif key == curses.KEY_PPAGE:  # Page Up
                        self.current_offset = max(0, self.current_offset - content_height * self.bytes_per_line)
                    
                    elif key == curses.KEY_NPAGE:  # Page Down
                        self.current_offset = min(self.file_size - 1, 
                                                self.current_offset + content_height * self.bytes_per_line)
                    
                    elif key == curses.KEY_HOME:
                        self.current_offset = 0
                    
                    elif key == curses.KEY_END:
                        self.current_offset = self.file_size - 1
                    
                    elif key == ord('e'):
                        # Cycle to next encoding
                        new_encoding = self.cycle_encoding()
                        # Show a temporary message
                        try:
                            msg = f"Encoding changed to: {new_encoding}"
                            stdscr.addstr(max_y - 1, 0, msg)
                            stdscr.refresh()
                            curses.napms(1000)  # Show message for 1 second
                        except curses.error:
                            pass
                    
                    elif key == ord('s'):
                        # Search functionality
                        prompt = "Search (string): "
                        try:
                            stdscr.addstr(max_y - 1, 0, prompt)
                            stdscr.clrtoeol()  # Clear to end of line
                            curses.echo()
                            curses.curs_set(1)
                            
                            search_str = ""
                            ch = stdscr.getch()
                            while ch != ord('\n') and ch != 27:  # Enter or Escape
                                search_str += chr(ch)
                                stdscr.addstr(max_y - 1, len(prompt), search_str)
                                ch = stdscr.getch()
                            
                            curses.noecho()
                            curses.curs_set(0)
                            
                            if search_str and ch != 27:  # Not escape
                                self.search(search_str, self.current_offset)
                        except curses.error:
                            pass
                        
                        curses.noecho()
                        curses.curs_set(0)
                    
                    elif key == ord('n'):
                        self.next_search_result()
                    
                    elif key == ord('p'):
                        self.prev_search_result()
                    
                    elif key == ord('j'):
                        # Jump to offset functionality
                        prompt = "Jump to offset (decimal or 0xHEX): "
                        try:
                            stdscr.addstr(max_y - 1, 0, prompt)
                            stdscr.clrtoeol()  # Clear to end of line
                            curses.echo()
                            curses.curs_set(1)
                            
                            jump_str = ""
                            ch = stdscr.getch()
                            while ch != ord('\n') and ch != 27:  # Enter or Escape
                                jump_str += chr(ch)
                                stdscr.addstr(max_y - 1, len(prompt), jump_str)
                                ch = stdscr.getch()
                            
                            curses.noecho()
                            curses.curs_set(0)
                            
                            if jump_str and ch != 27:  # Not escape
                                try:
                                    # Handle hex input
                                    if jump_str.lower().startswith('0x'):
                                        jump_offset = int(jump_str, 16)
                                    # Handle percentage
                                    elif jump_str.endswith('%'):
                                        percentage = float(jump_str[:-1])
                                        jump_offset = int((percentage / 100) * self.file_size)
                                    # Handle decimal
                                    else:
                                        jump_offset = int(jump_str)
                                    
                                    # Validate offset
                                    jump_offset = max(0, min(jump_offset, self.file_size - 1))
                                    self.current_offset = jump_offset
                                except ValueError:
                                    try:
                                        error_msg = "Invalid offset format. Use decimal, 0xHEX, or percentage%"
                                        stdscr.addstr(max_y - 1, 0, error_msg[:max_x-1])
                                        stdscr.refresh()
                                        curses.napms(1500)  # Show error for 1.5 seconds
                                    except:
                                        pass
                        except curses.error:
                            pass
                        
                        curses.noecho()
                        curses.curs_set(0)
                    
                    elif key == ord('['):
                        # Shift display left by 1 byte
                        self.display_shift = max(0, self.display_shift - 1)
                    
                    elif key == ord(']'):
                        # Shift display right by 1 byte
                        self.display_shift += 1
                    
                    elif key == ord('{'):
                        # Shift display left by 4 bytes
                        self.display_shift = max(0, self.display_shift - 4)
                    
                    elif key == ord('}'):
                        # Shift display right by 4 bytes
                        self.display_shift += 4
                    
                    elif key == ord('\\'):
                        # Reset shift
                        self.display_shift = 0
                    
                    elif key == ord('<'):
                        # Toggle to little endian
                        self.endian = 'little'
                    
                    elif key == ord('>'):
                        # Toggle to big endian
                        self.endian = 'big'
                    
                    elif key == ord('v'):
                        # Toggle value display
                        self.show_values = not self.show_values
                    
                    elif key == ord('h'):
                        # Toggle help display
                        show_help = not show_help
                    
                    elif key == ord('i'):
                        # Toggle investigate mode
                        show_investigate = not show_investigate
                        
                        # If turning on investigate and we're not on a search result, find nearest
                        if show_investigate and self.search_results:
                            if self.current_offset not in self.search_results:
                                # Find nearest search result
                                distances = [(abs(pos - self.current_offset), i) 
                                          for i, pos in enumerate(self.search_results)]
                                nearest_idx = min(distances, key=lambda x: x[0])[1]
                                self.current_search_idx = nearest_idx
                                self.current_offset = self.search_results[nearest_idx]
                    
                    elif key == ord('c'):
                        # Cycle through color schemes
                        if self.has_colors:
                            self.color_scheme = (self.color_scheme + 1) % 3
                            
                            # Reinitialize color pairs
                            if self.color_scheme == 1:  # Light theme
                                curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)      # Current line
                                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Current position
                                curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)       # Search hit
                                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Info line
                                curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)       # Encoding error
                            elif self.color_scheme == 2:  # Dark theme
                                curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Current line
                                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Current position
                                curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)    # Search hit
                                curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)     # Info line
                                curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)       # Encoding error
                            else:  # Default - high contrast for most terminals
                                curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)      # Current line
                                curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)     # Current position
                                curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_MAGENTA)   # Search hit
                                curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)     # Info line
                                curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_RED)       # Encoding error
                except Exception as e:
                    try:
                        error_msg = f"Error handling input: {str(e)}"
                        stdscr.addstr(max_y - 1, 0, error_msg[:max_x-1])
                        stdscr.refresh()
                        curses.napms(1500)  # Show error briefly
                    except:
                        pass
                
                # Refresh the screen
                stdscr.refresh()
                
            except Exception as e:
                try:
                    stdscr.addstr(0, 0, f"ERROR: {str(e)}")
                    stdscr.refresh()
                    stdscr.getch()  # Wait for any key
                except:
                    pass
                break
        
        return self.current_offset


def main():
    """Main entry point for SnakeByte"""
    parser = argparse.ArgumentParser(description="SnakeByte - Advanced Binary File Viewer")
    parser.add_argument("filename", help="Binary file to view")
    parser.add_argument("--config", "-c", help="Custom encodings configuration file")
    
    args = parser.parse_args()
    
    try:
        viewer = BinaryFileViewer(args.filename)
        if args.config:
            viewer.load_custom_encodings(args.config)
        else:
            viewer.load_custom_encodings()  # Try to load from default locations
        viewer.run()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
