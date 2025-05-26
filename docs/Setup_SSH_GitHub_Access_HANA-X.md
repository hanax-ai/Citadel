# ✅ Secure GitHub Access via SSH – HANA-X Lab Guide

This guide walks you through setting up SSH-based Git access for Ubuntu-based nodes in the HANA-X lab.

---

## 📂 Context

You are working in:

```bash
/home/ubuntu/Citadel_Revisions
```

The GitHub repository URL:

```bash
https://github.com/hanax-ai/Citadel.git
```

---

## 🔁 Step 1: Check the Current Git Remote

```bash
git remote -v
```

Expected output (before fix):

```
origin  https://github.com/hanax-ai/Citadel.git (fetch)
origin  https://github.com/hanax-ai/Citadel.git (push)
```

---

## 🔐 Step 2: Generate SSH Key (if not already created)

```bash
ssh-keygen -t ed25519 -C "jarvisr@hana-x.ai"
```

- Press Enter to accept the default location
- Optional: enter a passphrase or leave blank

---

## 📋 Step 3: Copy the SSH Public Key

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the full output string (starts with `ssh-ed25519`).

---

## 🌐 Step 4: Add the Key to GitHub

1. Go to: https://github.com/settings/keys
2. Click **"New SSH Key"**
3. **Title**: `Ubuntu Server SSH Key`
4. Paste the copied key into the key field
5. Click **Add SSH key**

---

## 🔁 Step 5: Switch Git Remote to Use SSH

```bash
cd /home/ubuntu/Citadel_Revisions
git remote set-url origin git@github.com:hanax-ai/Citadel.git
```

Verify:

```bash
git remote -v
```

Expected:

```
origin  git@github.com:hanax-ai/Citadel.git (fetch)
origin  git@github.com:hanax-ai/Citadel.git (push)
```

---

## 🧪 Step 6: Test SSH Push

```bash
git push origin main
```

If prompted with:

```
The authenticity of host 'github.com' can't be established...
Are you sure you want to continue connecting (yes/no)?
```

Type: `yes`

---

## 🖱️ How to Copy Text from xterm

- Highlight text with **left-click drag** → it’s automatically copied.
- **Middle-click** to paste (e.g., into browser or editor).
- Optional paste key: `Shift + Insert`

---

## ✅ Result

You now have:
- Passwordless push access to GitHub
- No PAT/token prompts
- Fully automated and secure Git flow

Ready for scripting or CI deployment in the HANA-X AI Lab.
