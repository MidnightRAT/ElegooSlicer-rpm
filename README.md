# ElegooSlicer RPM

RPM packaging for [ElegooSlicer](https://github.com/ELEGOO-3D/ElegooSlicer) — open-source slicer for FDM 3D printers.

## What is ElegooSlicer?

ElegooSlicer is an open-source slicer compatible with most FDM printers. Based on OrcaSlicer/PrusaSlicer, supporting STL, OBJ, 3MF file formats.

## Installation

### From GitHub Release

Download the latest `elegoo-slicer-*.x86_64.rpm` from [Releases](https://github.com/chirik/ElegooSlicer-rpm/releases) and install:

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

GitHub Actions automatically:
1. Checks for new ElegooSlicer releases
2. Builds src.rpm and x86_64.rpm
3. Uploads artifacts to GitHub Releases

## License

AGPL-3.0 (same as ElegooSlicer)
