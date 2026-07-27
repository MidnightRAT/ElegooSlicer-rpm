#!/usr/bin/env bash
#
# build-local.sh — Local SRPM + RPM builder for ElegooSlicer on Fedora 44+
#
# Reproduces the CI/COPR pipeline on a local machine:
#   1. Determine the version (from --version, $VERSION, or GitHub latest release)
#   2. Download the upstream source tarball
#   3. Populate ~/rpmbuild tree with tarball + patches
#   4. Render the spec template (@VERSION@ / @RELEASE@)
#   5. Build SRPM (and, unless --srpm-only, the binary RPM)
#
# NOTE: ElegooSlicer's %prep downloads web plugin bundles (elegoolink) from
# GitHub at build time, so a network connection is required during rpmbuild.
#
# Usage:
#   ./build-local.sh                   # latest release, SRPM + RPM
#   ./build-local.sh --version 1.5.2.2 # pin a version
#   ./build-local.sh --srpm-only       # only the source RPM
#   ./build-local.sh --install-deps    # dnf-install BuildRequires first (needs sudo)
#   ./build-local.sh --no-clean        # keep previous SOURCES/BUILD contents
#   ./build-local.sh --jobs 4          # override parallelism
#
# Env overrides: VERSION, RELEASE, RPMBUILD_DIR
set -euo pipefail

# ---- config ---------------------------------------------------------------
NAME="elegoo-slicer"
SPEC_TEMPLATE="elegoo-slicer.spec"
UPSTREAM_REPO="ELEGOO-3D/ElegooSlicer"
TARBALL_URL_TMPL="https://github.com/elegoo-repo/ElegooSlicer/archive/refs/tags/v%s.tar.gz"
DEFAULT_RELEASE="7"

# ---- args -----------------------------------------------------------------
VERSION="${VERSION:-}"
RELEASE="${RELEASE:-$DEFAULT_RELEASE}"
SRPM_ONLY=0
INSTALL_DEPS=0
NO_CLEAN=0
JOBS=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)      VERSION="$2"; shift 2;;
    --release)      RELEASE="$2"; shift 2;;
    --srpm-only)    SRPM_ONLY=1; shift;;
    --install-deps) INSTALL_DEPS=1; shift;;
    --no-clean)     NO_CLEAN=1; shift;;
    --jobs)         JOBS="$2"; shift 2;;
    -h|--help)      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0;;
    *) echo "Unknown option: $1" >&2; exit 2;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
RPMBUILD_DIR="${RPMBUILD_DIR:-$HOME/rpmbuild}"

log() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
err() { printf '\033[1;31mERROR:\033[0m %s\n' "$*" >&2; }

# ---- optional: install BuildRequires --------------------------------------
if [[ "$INSTALL_DEPS" -eq 1 ]]; then
  log "Installing build dependencies via dnf (sudo)…"
  sudo dnf install -y --skip-unavailable \
    rpm-build rpmdevtools git wget curl unzip \
    cmake ninja-build gcc gcc-c++ pkgconf \
    autoconf automake libtool m4 \
    perl-FindBin perl-IPC-Cmd \
    libquadmath-devel nasm \
    dbus-devel gtk3-devel webkit2gtk4.1-devel \
    glew-devel glfw-devel mesa-libGLU-devel mesa-libGL-devel \
    libjpeg-turbo-devel libpng-devel \
    openssl-devel libcurl-devel \
    freetype-devel fontconfig-devel pango-devel \
    eigen3-devel cereal-devel \
    extra-cmake-modules eglexternalplatform-devel \
    gstreamer1-devel gstreamer1-plugins-base-devel gstreamermm-devel \
    wayland-protocols-devel libxkbcommon-devel \
    libX11-devel libXi-devel libXrandr-devel libXinerama-devel \
    libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel \
    libXtst-devel libXfixes-devel libXmu-devel \
    at-spi2-core-devel libepoxy-devel \
    libspnav-devel libsecret-devel libmspack-devel \
    texinfo chrpath \
    tbb-devel blosc-devel NLopt-devel opencv-devel \
    opencascade-devel zlib-ng-compat-devel expat-devel \
    openvdb-devel mpfr-devel CGAL-devel openexr-devel imath-devel
fi

# ---- version resolution ---------------------------------------------------
if [[ -z "$VERSION" ]]; then
  log "Resolving latest release of ${UPSTREAM_REPO}…"
  VERSION="$(curl -sfL "https://api.github.com/repos/${UPSTREAM_REPO}/releases/latest" \
    | grep '"tag_name"' | cut -d '"' -f 4 | sed 's/^v//')"
  [[ -z "$VERSION" ]] && { err "Could not determine latest version"; exit 1; }
fi
log "Version: ${VERSION}   Release: ${RELEASE}"

TARBALL="${NAME}-${VERSION}-src.tar.gz"
# shellcheck disable=SC2059
TARBALL_URL="$(printf "$TARBALL_URL_TMPL" "$VERSION")"

# ---- rpmbuild tree --------------------------------------------------------
log "Preparing rpmbuild tree at ${RPMBUILD_DIR}…"
command -v rpmdev-setuptree >/dev/null && rpmdev-setuptree || mkdir -p "${RPMBUILD_DIR}"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
mkdir -p "${RPMBUILD_DIR}"/{SOURCES,SPECS,SRPMS,RPMS,BUILD}

if [[ "$NO_CLEAN" -eq 0 ]]; then
  rm -f "${RPMBUILD_DIR}/SOURCES/${NAME}-"*-src.tar.gz
  rm -f "${RPMBUILD_DIR}/SOURCES/"*.patch
fi

# ---- source tarball -------------------------------------------------------
if [[ -f "$TARBALL" ]]; then
  log "Reusing existing tarball: $TARBALL"
else
  log "Downloading source: ${TARBALL_URL}"
  wget -q --show-progress "$TARBALL_URL" -O "$TARBALL"
fi
cp -f "$TARBALL" "${RPMBUILD_DIR}/SOURCES/"

# ---- patches --------------------------------------------------------------
log "Copying patches…"
shopt -s nullglob
for p in patches/*.patch; do
  cp -f "$p" "${RPMBUILD_DIR}/SOURCES/"
  echo "    $(basename "$p")"
done
shopt -u nullglob

# ---- spec render ----------------------------------------------------------
log "Rendering spec from ${SPEC_TEMPLATE}…"
[[ -f "$SPEC_TEMPLATE" ]] || { err "$SPEC_TEMPLATE not found"; exit 1; }
sed -e "s/@VERSION@/${VERSION}/g" \
    -e "s/@RELEASE@/${RELEASE}/g" \
    "$SPEC_TEMPLATE" > "${RPMBUILD_DIR}/SPECS/${SPEC_TEMPLATE}"

# ---- build ----------------------------------------------------------------
RPMBUILD_ARGS=()
[[ -n "$JOBS" ]] && RPMBUILD_ARGS+=(--define "_smp_mflags -j${JOBS}")

if [[ "$SRPM_ONLY" -eq 1 ]]; then
  log "Building SRPM only…"
  rpmbuild -bs "${RPMBUILD_ARGS[@]}" "${RPMBUILD_DIR}/SPECS/${SPEC_TEMPLATE}"
else
  log "Building SRPM + RPM (this can take a long time)…"
  rpmbuild -ba "${RPMBUILD_ARGS[@]}" "${RPMBUILD_DIR}/SPECS/${SPEC_TEMPLATE}"
fi

# ---- report ---------------------------------------------------------------
log "Build complete. Artifacts:"
find "${RPMBUILD_DIR}/SRPMS" -name "${NAME}-${VERSION}-*.src.rpm" -printf '    %p\n' 2>/dev/null || true
find "${RPMBUILD_DIR}/RPMS"  -name "${NAME}-${VERSION}-*.rpm"     -printf '    %p\n' 2>/dev/null || true
