#!/bin/bash
# HANA-X Lab GitHub SSH Setup Script
# This script configures SSH-based Git access for Ubuntu-based lab nodes

GITHUB_EMAIL="jarvisr@hana-x.ai"
GITHUB_USER="hanax-ai"
REPO_NAME="Citadel"
WORKDIR="/home/ubuntu/Citadel_Revisions"

echo "🚀 Generating SSH key..."
ssh-keygen -t ed25519 -C "$GITHUB_EMAIL" -f ~/.ssh/id_ed25519 -N ""

echo "🔑 Your public SSH key is:"
cat ~/.ssh/id_ed25519.pub

echo "📎 Copy the key above and add it to https://github.com/settings/keys"
read -p "⏳ Press Enter after adding the SSH key to GitHub..."

echo "📁 Switching to project directory: $WORKDIR"
cd "$WORKDIR" || { echo "❌ Directory not found: $WORKDIR"; exit 1; }

echo "🔁 Updating remote to use SSH..."
git remote set-url origin git@github.com:$GITHUB_USER/$REPO_NAME.git

echo "✅ Verifying updated Git remote:"
git remote -v

echo "🧪 Testing SSH connection to GitHub..."
ssh -T git@github.com

echo "🚀 Attempting to push to GitHub..."
git push origin main

echo "✅ Done. Your SSH access is now configured for GitHub."
