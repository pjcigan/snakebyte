## 📦 Installation

### Quick Install (Recommended)

Install SnakeByte system-wide with a single command:

```bash
curl -sSL https://raw.githubusercontent.com/pjcigan/snakebyte/main/install.sh | bash
```

Or download and review the script first:

```bash
wget https://raw.githubusercontent.com/pjcigan/snakebyte/main/install.sh
chmod +x install.sh
./install.sh
```

**What the installer does:**
- Downloads the latest `snakebyte.py` to `/usr/local/bin/snakebyte`
- Makes it executable and available from anywhere
- Requires `sudo` privileges for system-wide installation

**After installation, run from anywhere:**
```bash
snakebyte /path/to/your/file.bin
```

### Manual Installation

#### Option 1: Single-file download
```bash
# Download the script
wget https://github.com/pjcigan/snakebyte/releases/latest/download/snakebyte.py

# Make it executable
chmod +x snakebyte.py

# Run directly
./snakebyte.py your_file.bin
```

#### Option 2: Clone repository
```bash
git clone https://github.com/pjcigan/snakebyte.git
cd snakebyte
python snakebyte.py your_file.bin
```

#### Option 3: Manual system-wide install
```bash
# Download to system location
sudo wget -O /usr/local/bin/snakebyte https://github.com/pjcigan/snakebyte/releases/latest/download/snakebyte.py

# Make executable
sudo chmod +x /usr/local/bin/snakebyte

# Run from anywhere
snakebyte your_file.bin
```

### Requirements

- **Python 3.6 or later** (check with `python3 --version`)
- **No external dependencies** - uses only Python standard library
- **Cross-platform** - works on Linux, macOS, and Windows

### Verification

Test your installation:

```bash
# Check if snakebyte is in your PATH
which snakebyte

# Create a test file and view it
echo "Hello, SnakeByte!" > test.txt
snakebyte test.txt
```

### Uninstallation

**If installed via install script:**
```bash
sudo rm /usr/local/bin/snakebyte
```

**If manually downloaded:**
```bash
rm snakebyte.py  # or wherever you saved it
```

### Troubleshooting

**"Command not found" error:**
- Make sure `/usr/local/bin` is in your PATH
- Try running with full path: `/usr/local/bin/snakebyte`
- On some systems, you may need to restart your terminal

**Permission denied:**
- The installer needs sudo privileges to write to `/usr/local/bin`
- Alternatively, install to your home directory: `~/bin/snakebyte`

**Python not found:**
- Make sure Python 3.6+ is installed
- Try `python3 snakebyte.py` instead of just `snakebyte`
