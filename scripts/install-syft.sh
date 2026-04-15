#!/usr/bin/env bash
# Install pinned Syft from GitHub release assets with SHA-256 verification (no curl|sh).
set -euo pipefail

SYFT_VERSION="${SYFT_VERSION:-1.16.0}"
INSTALL_DIR="${SYFT_INSTALL_DIR:-./bin}"
mkdir -p "${INSTALL_DIR}"

checksum_for() {
  local asset="$1"
  local h
  h="$(awk -v "a=${asset}" '$2==a {print $1; exit}' "${CHECKSUM_FILE}")"
  if [[ -z "${h}" ]]; then
    echo "install-syft: missing checksum for ${asset}" >&2
    exit 1
  fi
  echo "${h}"
}

verify_sha256() {
  local file="$1"
  local expected="$2"
  local actual
  if command -v sha256sum >/dev/null 2>&1; then
    actual="$(sha256sum "${file}" | awk '{print $1}')"
  else
    actual="$(shasum -a 256 "${file}" | awk '{print $1}')"
  fi
  if [[ "${actual}" != "${expected}" ]]; then
    echo "install-syft: checksum mismatch for ${file}" >&2
    exit 1
  fi
}

BASE="https://github.com/anchore/syft/releases/download/v${SYFT_VERSION}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKSUM_FILE="${SCRIPT_DIR}/syft-v${SYFT_VERSION}.checksums"

tmp="$(mktemp)"
cleanup() { rm -f "${tmp}"; }
trap cleanup EXIT

curl -fsSL "${BASE}/syft_${SYFT_VERSION}_checksums.txt" -o "${CHECKSUM_FILE}.dl"
mv "${CHECKSUM_FILE}.dl" "${CHECKSUM_FILE}"

os="$(uname -s)"
arch="$(uname -m)"
asset=""
case "${os}_${arch}" in
  Linux_x86_64) asset="syft_${SYFT_VERSION}_linux_amd64.tar.gz" ;;
  Linux_aarch64|Linux_arm64) asset="syft_${SYFT_VERSION}_linux_arm64.tar.gz" ;;
  Darwin_arm64) asset="syft_${SYFT_VERSION}_darwin_arm64.tar.gz" ;;
  Darwin_x86_64) asset="syft_${SYFT_VERSION}_darwin_amd64.tar.gz" ;;
  *)
    echo "install-syft: unsupported platform ${os} ${arch}" >&2
    exit 1
    ;;
esac

expected="$(checksum_for "${asset}")"
curl -fsSL "${BASE}/${asset}" -o "${tmp}"
verify_sha256 "${tmp}" "${expected}"
tar -xzf "${tmp}" -C "${INSTALL_DIR}" syft
chmod +x "${INSTALL_DIR}/syft"
echo "install-syft: installed syft v${SYFT_VERSION} to ${INSTALL_DIR}/syft"
