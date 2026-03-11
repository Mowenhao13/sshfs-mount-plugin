#!/bin/bash
# SSHFS Mount Manager - Installation Script
# This script installs the SSHFS Mount Manager plugin for Claude Code

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$SCRIPT_DIR/.."
INSTALL_DIR="$HOME/.claude/skills/sshfs-mount"
CONFIG_DIR="$HOME/.config/sshfs-mounts"

echo "=============================================="
echo "SSHFS Mount Manager - Installation"
echo "=============================================="
echo ""

# Check for sshfs
if ! command -v sshfs &> /dev/null; then
    echo "Warning: sshfs is not installed."
    echo "Please install sshfs first:"
    echo "  macOS: brew install sshfs"
    echo "  Ubuntu: sudo apt-get install sshfs"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create directories
echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR/profiles"

# Copy files from new plugin structure
echo "Copying files..."
mkdir -p "$INSTALL_DIR/lib"
mkdir -p "$INSTALL_DIR/bin"

cp "$PLUGIN_DIR/lib/sshfs_mount.py" "$INSTALL_DIR/lib/"
cp "$PLUGIN_DIR/lib/sshfs_daemon.py" "$INSTALL_DIR/lib/"
cp "$PLUGIN_DIR/lib/generate_claude_md.py" "$INSTALL_DIR/lib/"
cp "$PLUGIN_DIR/bin/sshfs-mount" "$INSTALL_DIR/bin/"
cp "$PLUGIN_DIR/bin/sshfs-daemon" "$INSTALL_DIR/bin/"
cp "$PLUGIN_DIR/bin/sshfs" "$INSTALL_DIR/bin/"

# Make scripts executable
chmod +x "$INSTALL_DIR/lib/"*.py
chmod +x "$INSTALL_DIR/bin/"*

# Create wrapper script for easy access
WRAPPER_SCRIPT="$HOME/.local/bin/sshfs-mount"
mkdir -p "$(dirname "$WRAPPER_SCRIPT")"

cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
exec python3 "$HOME/.claude/skills/sshfs-mount/bin/sshfs-mount" "$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Create daemon wrapper
DAEMON_WRAPPER="$HOME/.local/bin/sshfs-daemon"
cat > "$DAEMON_WRAPPER" << 'EOF'
#!/bin/bash
exec python3 "$HOME/.claude/skills/sshfs-mount/bin/sshfs-daemon" "$@"
EOF

chmod +x "$DAEMON_WRAPPER"

echo ""
echo "=============================================="
echo "Installation Complete!"
echo "=============================================="
echo ""
echo "The SSHFS Mount Manager has been installed to:"
echo "  $INSTALL_DIR"
echo ""
echo "Command-line wrappers installed to:"
echo "  $WRAPPER_SCRIPT"
echo "  $DAEMON_WRAPPER"
echo ""
echo "To use with Claude Code:"
echo "  1. Restart Claude Code"
echo "  2. Run /sshfs-mount to see available commands"
echo ""
echo "To use from command line:"
echo "  sshfs-mount status"
echo "  sshfs-mount mount"
echo "  sshfs-mount unmount"
echo "  sshfs-mount init  (first-time setup)"
echo ""
echo "=============================================="
echo ""

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Note: $HOME/.local/bin is not in your PATH."

    # Offer to add it to shell config
    read -p "Add to ~/.zshrc automatically? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        echo '' >> ~/.zshrc
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        echo "✓ Added to ~/.zshrc"
        echo "  Run 'source ~/.zshrc' or restart terminal to apply."
    else
        echo "Add this to your ~/.zshrc or ~/.bashrc manually:"
        echo "  export PATH=\"$HOME/.local/bin:\$PATH\""
    fi
    echo ""
fi

# First-time setup prompt
if [[ ! -f "$CONFIG_DIR/config.yaml" ]] && [[ ! -f "$CONFIG_DIR/profiles/default.yaml" ]]; then
    echo "No configuration found. Run initialization?"
    read -p "Run setup wizard now? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
        python3 "$INSTALL_DIR/bin/sshfs-mount" init
    fi
fi
