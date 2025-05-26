
# Project Citadel Deployment Scripts

This directory contains scripts for automating the deployment process of Project Citadel. These scripts handle backing up existing code, deploying new code, running tests, and providing rollback capabilities if needed.

## Prerequisites

- Bash shell environment
- rsync
- tar
- Python with pytest installed (for running tests)

## Directory Structure

- `/home/ubuntu/Citadel_Revisions/src/citadel/` - Source code directory
- `/home/ubuntu/Citadel_Revisions/tests/` - Test directory
- `/home/ubuntu/Citadel` - Production directory
- `/home/ubuntu/backups/` - Directory for storing backups
- `/home/ubuntu/Citadel_Revisions/deployment/logs/` - Directory for storing deployment logs

## Scripts Overview

### common.sh

Contains common configuration variables and utility functions used by all scripts.

### backup.sh

Creates a timestamped backup of the current production code.

**Usage:**
```bash
./backup.sh
```

**Output:**
- Returns the path to the created backup file
- Creates a backup file in `/home/ubuntu/backups/` with format `citadel_backup_YYYYMMDD_HHMMSS.tar.gz`

### test.sh

Runs the test suite for Project Citadel.

**Usage:**
```bash
./test.sh
```

**Output:**
- Returns 0 if tests pass, non-zero otherwise
- Logs test results to the deployment log

### rollback.sh

Restores the production code from a backup.

**Usage:**
```bash
./rollback.sh [backup_path]
```

**Parameters:**
- `backup_path` (optional): Path to the backup file to restore. If not provided, the most recent backup will be used.

### deploy.sh

Main deployment script that orchestrates the entire process:
1. Creates a backup of the current production code
2. Deploys the new code from the source directory
3. Runs tests to verify the deployment
4. Rolls back to the previous version if tests fail

**Usage:**
```bash
./deploy.sh
```

## Getting Started

1. Make the scripts executable:
   ```bash
   chmod +x /home/ubuntu/Citadel_Revisions/deployment/*.sh
   ```

2. Run the deployment:
   ```bash
   cd /home/ubuntu/Citadel_Revisions/deployment/
   ./deploy.sh
   ```

## Logs

All deployment actions are logged to `/home/ubuntu/Citadel_Revisions/deployment/logs/deployment_YYYYMMDD_HHMMSS.log`.

## Safety Tips

1. Always verify that a recent backup exists before making major changes.
2. You can manually create a backup at any time using `./backup.sh`.
3. If a deployment fails, the system will automatically roll back to the previous version.
4. You can manually roll back to a specific backup using `./rollback.sh [backup_path]`.
5. To roll back to the most recent backup, simply run `./rollback.sh` without parameters.

## Troubleshooting

- If scripts fail with permission errors, ensure they are executable using `chmod +x *.sh`.
- Check the log files in the logs directory for detailed error messages.
- Ensure all prerequisite tools (rsync, tar, python, pytest) are installed and available in the PATH.
