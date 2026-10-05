#!/usr/bin/env bash
set -euo pipefail

# Ensure script is executed with root privileges
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] This deployment script must be run as root." >&2
    exit 1
fi

DATA_DIR="/var/lib/trust_shell"
TPM_CTX_FILE="${DATA_DIR}/tpm_hmac.ctx"
SERVICE_FILE="/etc/systemd/system/trust-shell.service"
APP_DIR="/opt/trust-shell"

echo "[1/5] Creating restricted directory structure..."
mkdir -p "${DATA_DIR}"
mkdir -p "${APP_DIR}"

# Restrict directory access strictly to root (u=rwx,g=,o=)
chown root:root "${DATA_DIR}"
chmod 700 "${DATA_DIR}"

echo "[2/5] Checking TPM 2.0 hardware interface..."
if [ -c /dev/tpmrm0 ]; then
    TPM_DEV="/dev/tpmrm0"
elif [ -c /dev/tpm0 ]; then
    TPM_DEV="/dev/tpm0"
else
    echo "[WARNING] No hardware TPM device found at /dev/tpmrm0 or /dev/tpm0."
    echo "          Trust-Shell will start in Software Fallback mode."
    TPM_DEV=""
fi

echo "[3/5] Initializing TPM 2.0 HMAC Key Context..."
if [ -n "${TPM_DEV}" ]; then
    # Install tpm2-tools if missing on Debian/Ubuntu/RHEL systems
    if ! command -v tpm2_createprimary &> /dev/null; then
        echo "[INFO] Installing tpm2-tools..."
        if command -v apt-get &> /dev/null; then
            apt-get update -qq && apt-get install -y -qq tpm2-tools
        elif command -v dnf &> /dev/null; then
            dnf install -y -q tpm2-tools
        fi
    fi

    if [ ! -f "${TPM_CTX_FILE}" ]; then
        echo "[INFO] Provisioning new persistent TPM key..."
        
        # Create Primary Key in Owner Hierarchy
        tpm2_createprimary -C o -g sha256 -G keyedhash -c /tmp/trust_primary.ctx
        
        # Create HMAC Key object
        tpm2_create -C /tmp/trust_primary.ctx -g sha256 -G hmac -c "${TPM_CTX_FILE}"
        
        # Clean up temporary primary context
        rm -f /tmp/trust_primary.ctx

        # Lock permissions on the context file
        chown root:root "${TPM_CTX_FILE}"
        chmod 600 "${TPM_CTX_FILE}"
        echo "[SUCCESS] TPM HMAC Key Context created at ${TPM_CTX_FILE}"
    else
        echo "[INFO] Existing TPM context found at ${TPM_CTX_FILE}. Skipping generation."
    fi
fi

echo "[4/5] Installing systemd service unit..."
cat <<'EOF' > "${SERVICE_FILE}"
[Unit]
Description=Trust-Shell Forensic Service & Offline Buffer
After=network.target local-fs.target
Wants=network-online.target
ConditionPathExists=/var/lib/trust_shell

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/trust-shell
ExecStartPre=/bin/bash -c '/usr/bin/test -d /var/lib/trust_shell && /usr/bin/test "$(/usr/bin/stat -c %%a /var/lib/trust_shell)" = "700"'
ExecStart=/usr/bin/node /opt/trust-shell/index.js
Restart=always
RestartSec=5s

# Process Environment & Directory Bounds
Environment=NODE_ENV=production
Environment=TRUST_SHELL_DB_PATH=/var/lib/trust_shell/trust_shell_queue.db
Environment=TRUST_SHELL_TPM_CTX=/var/lib/trust_shell/tpm_hmac.ctx

# Security Hardening Directives
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/trust_shell /opt/trust-shell
PrivateTmp=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
DeviceAllow=/dev/tpmrm0 rw
DeviceAllow=/dev/tpm0 rw

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "${SERVICE_FILE}"

echo "[5/5] Reloading systemd and enabling service..."
systemctl daemon-reload
systemctl enable trust-shell.service

echo "=========================================================="
echo " Deployment Complete."
echo " Directory: ${DATA_DIR} (Permissions: $(stat -c '%a %U:%G' ${DATA_DIR}))"
echo " Service:   systemctl start trust-shell"
echo "=========================================================="
