# ElegooSlicer RPM

[![Build ElegooSlicer RPM](https://github.com/MidnightRAT/ElegooSlicer-rpm/actions/workflows/build-rpm.yml/badge.svg)](https://github.com/MidnightRAT/ElegooSlicer-rpm/actions/workflows/build-rpm.yml)
[![Latest Release](https://img.shields.io/github/v/release/MidnightRAT/ElegooSlicer-rpm)](https://github.com/MidnightRAT/ElegooSlicer-rpm/releases/latest)

RPM packaging for [ElegooSlicer](https://github.com/ELEGOO-3D/ElegooSlicer) — open-source slicer for FDM 3D printers.

## Donate

[![Ko-fi](https://img.shields.io/badge/Ko--fi-Support%20me%20on%20Ko--fi-ff5e5b?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/redeyesnightrat)

## What is ElegooSlicer?

ElegooSlicer is an open-source slicer compatible with most FDM printers. Based on OrcaSlicer/PrusaSlicer, supporting STL, OBJ, 3MF file formats.

### File Associations

The RPM package registers MIME types (`model/stl`, `model/obj`, `model/3mf`) so that double-clicking `.stl`, `.obj`, or `.3mf` files opens them in ElegooSlicer.

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
# Install build dependencies
sudo dnf install -y rpm-build rpmdevtools git wget curl \
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
  texinfo chrpath

# Build RPM
rpmbuild -ba elegoo-slicer.spec
```

## CI/CD

### GitHub Actions

Automatically:

1. Checks for new ElegooSlicer releases (weekly schedule)
2. Builds src.rpm and x86_64.rpm in Fedora 44 container
3. Uploads artifacts to GitHub Releases

### COPR

Automatically builds for Fedora 43+ from the latest main branch:

- [COPR Project Page](https://copr.fedorainfracloud.org/projects/chirikrat/ElegooSlicer-rpm/)

**Note:** Workflows do not trigger on changes to CHANGELOG.md or README.md.

## Project Structure

```
ElegooSlicer-rpm/
├── .copr/Makefile         # COPR SRPM build script
├── .github/workflows/     # GitHub Actions workflow
├── elegoo-slicer.spec     # RPM spec file
├── patches/               # Source patches
├── CHANGELOG.md
└── README.md
```

## License

AGPL-3.0 (same as ElegooSlicer)
