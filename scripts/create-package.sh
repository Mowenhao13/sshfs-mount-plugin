#!/bin/bash
# SSHFS Mount Manager - Create Distribution Package
# This script creates a tarball for easy distribution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$SCRIPT_DIR/.."
PACKAGE_NAME="sshfs-mount"
VERSION="2.0.0"

echo "Creating distribution package..."

# Create temp directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/$PACKAGE_NAME"

# Create package structure with new plugin layout
mkdir -p "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR/lib"
mkdir -p "$PACKAGE_DIR/bin"
mkdir -p "$PACKAGE_DIR/skills"
mkdir -p "$PACKAGE_DIR/commands"
mkdir -p "$PACKAGE_DIR/scripts"
mkdir -p "$PACKAGE_DIR/.claude-plugin"

# Copy files
cp "$PLUGIN_DIR/lib/"*.py "$PACKAGE_DIR/lib/"
cp "$PLUGIN_DIR/bin/"* "$PACKAGE_DIR/bin/"
cp "$PLUGIN_DIR/skills/"*.skill.md "$PACKAGE_DIR/skills/"
cp "$PLUGIN_DIR/commands/"*.md "$PACKAGE_DIR/commands/"
cp "$PLUGIN_DIR/scripts/"*.sh "$PACKAGE_DIR/scripts/"
cp "$PLUGIN_DIR/.claude-plugin/plugin.json" "$PACKAGE_DIR/.claude-plugin/"
cp "$PLUGIN_DIR/README.md" "$PACKAGE_DIR/"

# Make scripts executable
chmod +x "$PACKAGE_DIR/bin/"*
chmod +x "$PACKAGE_DIR/scripts/"*.sh

# Create tarball
cd "$TEMP_DIR"
tar -czf "$SCRIPT_DIR/${PACKAGE_NAME}-${VERSION}.tar.gz" "$PACKAGE_NAME"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "=============================================="
echo "Distribution package created:"
echo "  $SCRIPT_DIR/${PACKAGE_NAME}-${VERSION}.tar.gz"
echo "=============================================="
echo ""
echo "To install on another machine:"
echo "  1. Copy the tarball to the target machine"
echo "  2. Extract: tar -xzf ${PACKAGE_NAME}-${VERSION}.tar.gz"
echo "  3. Install: cd ${PACKAGE_NAME} && ./scripts/install.sh"
echo ""
