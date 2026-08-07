# ElegooSlicer RPM

[![Build ElegooSlicer RPM](https://github.com/MidnightRAT/ElegooSlicer-rpm/actions/workflows/build-rpm.yml/badge.svg)](https://github.com/MidnightRAT/ElegooSlicer-rpm/actions/workflows/build-rpm.yml)
[![Latest Release](https://img.shields.io/github/v/release/MidnightRAT/ElegooSlicer-rpm)](https://github.com/MidnightRAT/ElegooSlicer-rpm/releases/latest)

RPM packaging for [ElegooSlicer](https://github.com/ELEGOO-3D/ElegooSlicer) — open-source FDM slicer for Elegoo printers (based on OrcaSlicer).

## Donate

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20me%20on%20Ko--fi-ff5e5b?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/redeyesnightrat)

## What is ElegooSlicer?

ElegooSlicer is an open-source slicer compatible with most FDM printers. Based on OrcaSlicer/PrusaSlicer, optimized for Elegoo printers (Centauri, Neptune series). Installed under `/opt/ElegooSlicer`.

## Dependency strategy

Where possible the package uses **system libraries** (OpenSSL, libcurl, expat, zlib-ng, libpng, JPEG, TBB, GLFW, GLEW, NLopt, CGAL, cereal, Eigen, GMP, MPFR, Qhull, Blosc, Draco, freetype, libjpeg-turbo, OpenCV). Incompatible or unavailable libraries are **bundled** via `deps/` (Boost, wxWidgets, OpenVDB, OCCT, OpenEXR, ixwebsocket, PahoMqttCpp, elegoolink, Sentry, libnoise, OpenCSG).

Two patches make this possible:

- `patches/0001-deps-system-openssl-curl.patch` — deps build detects system OpenSSL and libcurl (non-flatpak).
- `patches/0002-elegoolink-system-curl-algorithm.patch` — elegoolink uses system curl and adds missing `<algorithm>` include for GCC 16.

## Installation

### From COPR (Fedora, Recommended)

```bash
sudo dnf copr enable chirikrat/ElegooSlicer-rpm
sudo dnf install elegoo-slicer
```

### From GitHub Release

Download the latest `elegoo-slicer-*.x86_64.rpm` from [Releases](https://github.com/MidnightRAT/ElegooSlicer-rpm/releases) and install:

```bash
sudo dnf install elegoo-slicer-*.x86_64.rpm
```

### Build from Source

```bash
# Install build tools
sudo dnf install -y rpm-build rpmdevtools git git-lfs wget curl \
  cmake ninja-build gcc gcc-c++ make patch pkgconf \
  autoconf automake libtool m4 \
  perl-FindBin perl-IPC-Cmd \
  texinfo gettext python3 libquadmath-devel \
  dbus-devel gtk3-devel webkit2gtk4.1-devel \
  glew-devel glfw-devel mesa-libGLU-devel mesa-libGL-devel libglvnd-devel \
  libjpeg-turbo-devel libpng-devel \
  openssl-devel libcurl-devel \
  freetype-devel fontconfig-devel \
  eigen3-devel cereal-devel \
  gmp-devel mpfr-devel qhull-devel draco-devel draco-static \
  extra-cmake-modules eglexternalplatform-devel wayland-devel \
  gstreamer1-devel gstreamer1-plugins-good gstreamermm-devel \
  libX11-devel libXi-devel libXrandr-devel libXinerama-devel \
  libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel \
  libXtst-devel libXfixes-devel libXmu-devel \
  at-spi2-core-devel libepoxy-devel \
  libspnav-devel libsecret-devel libmspack-devel \
  desktop-file-utils \
  tbb-devel blosc-devel NLopt-devel opencv-devel \
  zlib-ng-compat-devel expat-devel openexr-devel

# Determine version and build RPM
VERSION=$(curl -sL https://api.github.com/repos/ELEGOO-3D/ElegooSlicer/releases/latest | grep tag_name | cut -d '"' -f 4 | sed 's/^v//')
rpmdev-setuptree
wget -q "https://github.com/elegoo-repo/ElegooSlicer/archive/refs/tags/v${VERSION}.tar.gz" \
  -O ~/rpmbuild/SOURCES/ElegooSlicer-${VERSION}.tar.gz
cp README.md ~/rpmbuild/SOURCES/
cp patches/0*.patch ~/rpmbuild/SOURCES/
sed -e "s/@VERSION@/${VERSION}/g" -e "s/@RELEASE@/4/g" \
  elegoo-slicer.spec > ~/rpmbuild/SPECS/elegoo-slicer.spec
rpmbuild -ba ~/rpmbuild/SPECS/elegoo-slicer.spec
```

> The `%prep`/`%build` for the bundled `deps/` and the main build requires a network connection and lots of RAM; building takes a long time.

## CI/CD

### GitHub Actions

Automatically:

1. Checks for new ElegooSlicer releases (weekly schedule)
2. Builds src.rpm and x86_64.rpm in Fedora container
3. Uploads artifacts to GitHub Releases

### COPR

Automatically builds for Fedora from the latest main branch:

- [COPR Project Page](https://copr.fedorainfracloud.org/projects/chirikrat/ElegooSlicer-rpm/)

**Note:** changes to `README.md` or `.copr/**` do not trigger the workflow.

## Project Structure

```
ElegooSlicer-rpm/
├── .copr/Makefile              # COPR SRPM build script
├── .github/workflows/          # GitHub Actions workflow
├── elegoo-slicer.spec          # RPM spec file
├── patches/
│   ├── 0001-deps-system-openssl-curl.patch
│   └── 0002-elegoolink-system-curl-algorithm.patch
└── README.md
```

## License

AGPL-3.0 (same as ElegooSlicer)