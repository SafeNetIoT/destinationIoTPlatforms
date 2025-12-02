#!/usr/bin/env bash
set -euo pipefail

###
# CONFIG – CHANGE THESE PER DEVICE / DATASET
###

# Device name (matches folder under /data/disk1/traffic/by-name/)
DEVICE_NAME="sonos_speaker"      # e.g. "tplink_plug", "camera1", etc.

# Years you want to process (space-separated)
YEARS="2023 2024 2025"

# Where the PCAPs live for this device
PCAP_ROOT="/data/disk1/traffic/by-name/${DEVICE_NAME}/ctrl2"

# Where to store longitudinal analysis for this device
MAC_BASE="analysis_longitudinal/${DEVICE_NAME}"

# Where to store per-month input lists
INPUT_BASE="inputs/${DEVICE_NAME}_longitudinal"

###
# END CONFIG
###

mkdir -p "${MAC_BASE}"
mkdir -p "${INPUT_BASE}"

for YEAR in ${YEARS}; do
  for MONTH_NUM in 01 02 03 04 05 06 07 08 09 10 11 12; do

    # Month folder name e.g. Jan_2025, Jul_2024
    MONTH_NAME=$(date -d "${YEAR}-${MONTH_NUM}-01" +%b)
    MONTH_FOLDER="${MONTH_NAME}_${YEAR}"

    OUT_DIR="${MAC_BASE}/${YEAR}/${MONTH_FOLDER}"
    mkdir -p "${OUT_DIR}"

    # Per-month PCAP list (pattern matches: YYYY-MM-*.pcap)
    LIST_FILE="${INPUT_BASE}/${YEAR}-${MONTH_NUM}.txt"
    find "${PCAP_ROOT}" -type f -name "${YEAR}-${MONTH_NUM}-*.pcap" > "${LIST_FILE}"

    # If no PCAPs, skip this month
    if [ ! -s "${LIST_FILE}" ]; then
      echo "[${DEVICE_NAME}] No PCAPs for ${YEAR}-${MONTH_NUM}, skipping"
      continue
    fi

    echo "============================================"
    echo "[${DEVICE_NAME}] Processing ${MONTH_FOLDER}"
    echo "  PCAP list : ${LIST_FILE}"
    echo "  Output dir: ${OUT_DIR}"
    echo "============================================"

    # 1. Domains (DNS/TLS → domain_list/)
    python3 destination_analysis.py domains \
      --input_file "${LIST_FILE}" \
      --output_dir "${OUT_DIR}" \
      --exp "${DEVICE_NAME}_${YEAR}_${MONTH_NUM}_domains"

    # 2. IPs (PCAPs → ip_list/ + IP→domain mapping)
    python3 destination_analysis.py map_ips \
      --input_file "${LIST_FILE}" \
      --output_dir "${OUT_DIR}" \
      --exp "${DEVICE_NAME}_${YEAR}_${MONTH_NUM}_ips"

  done
done
