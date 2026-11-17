# ElegooSlicer RPM

[![Build ElegooSlicer RPM](https://github.com/MidnightRAT/ElegooSlicer-rpm/actions/workflows/build-rpm.yml/badge.svg)](https://github.com/MidnightRAT/ElegooSlicer-rpm/actions/workflows/build-rpm.yml)
[![Latest Release](https://img.shields.io/github/v/release/MidnightRAT/ElegooSlicer-rpm)](https://github.com/MidnightRAT/ElegooSlicer-rpm/releases/latest)

RPM packaging for [ElegooSlicer](https://github.com/ELEGOO-3D/ElegooSlicer) — open-source FDM slicer for Elegoo printers (based on OrcaSlicer).

## Donate

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/redeyesnightrat)

## What is ElegooSlicer?

ElegooSlicer is an open-source slicer compatible with most FDM printers. Based on OrcaSlicer/PrusaSlicer, optimized for Elegoo printers (Centauri, Neptune series). Installed under `/opt/ElegooSlicer`.

## Dependency strategy

Where possible the package uses **system libraries** (OpenSSL, libcurl, expat, zlib-ng, libpng, JPEG, TBB, GLFW, GLEW, NLopt, CGAL, cereal, Eigen, GMP, MPFR, Qhull, Blosc, Draco, freetype, libjpeg-turbo, OpenCV). Incompatible or unavailable libraries are **bundled** via `deps/` (Boost, wxWidgets, OpenVDB, OCCT, OpenEXR, ixwebsocket, PahoMqttCpp, elegoolink, Sentry, libnoise, OpenCSG).

Two patches make this possible:

- `patches/0001-deps-system-openssl-curl.patch` — deps build detects system OpenSSL and libcurl (non-flatpak).
- `patches/0002-elegoolink-system-curl-algorithm.patch` — elegoolink uses system curl and adds missing `<algorithm>` include for GCC 16.

A third patch is arch-specific:

- `patches/0003-aarch64-agora.patch` — on `aarch64` only, replaces the bundled
  x86_64 Agora RTM SDK (`.so` + headers) with an aarch64 build before
  `elegoo-link` is configured; on `x86_64` it does nothing. See
  [aarch64 support](#aarch64-support).

And one fixes a GCC 16 / arch bug:

- `patches/0004-blosc-c99.patch` — forces `CMAKE_C_STANDARD=99` for the bundled
  Blosc. Blosc only adds `-std=gnu99` on i386/x86_64, so on `aarch64` it fell
  back to GCC 16's `gnu23` default where `bool` is a keyword
  (`blosc/shuffle.c: typedef _Bool bool;`). On `x86_64` the flag is a
  duplicate of the one Blosc already passes, so nothing changes there.

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
sudo dnf install -y rpm-build rpmdevtools git git-lfs wget curl unzip \
  cmake ninja-build gcc gcc-c++ make patch pkgconf patchelf \
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
# NOTE: on aarch64 drop `libquadmath-devel` — Fedora 45 aarch64 does not ship it
# (and the build does not link against libquadmath).

# Determine version and build RPM
VERSION=$(curl -sL https://api.github.com/repos/ELEGOO-3D/ElegooSlicer/releases/latest | grep tag_name | cut -d '"' -f 4 | sed 's/^v//')
rpmdev-setuptree
wget -q "https://github.com/elegoo-repo/ElegooSlicer/archive/refs/tags/v${VERSION}.tar.gz" \
  -O ~/rpmbuild/SOURCES/ElegooSlicer-${VERSION}.tar.gz
cp README.md ~/rpmbuild/SOURCES/
cp patches/0*.patch ~/rpmbuild/SOURCES/
sed -e "s/@VERSION@/${VERSION}/g" -e "s/@RELEASE@/7/g" \
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

- [COPR Project Page](https://copr.fedorainfracloud.org/coprs/chirikrat/ElegooSlicer-rpm/)

Enabled chroots: `fedora-44-x86_64`, `fedora-45-x86_64`, `fedora-45-aarch64`

**Note:** changes to `README.md` or `.copr/**` do not trigger the workflow.

## aarch64 support

The bundled Agora RTM SDK in `elegoo-link` (`thirdparty/agora/linux/`) only
ships **x86_64** `.so` files, and cloud features cannot simply be switched off
(`ENABLE_CLOUD_FEATURES`): the slicer calls them unconditionally from ~23
files. There is also no official Agora C++ SDK for Linux aarch64.

On `aarch64` the spec therefore stages a replacement in `%prep` (SHA256-pinned
downloads) and patch `0003-aarch64-agora.patch` installs it into the cloned
`elegoo-link` before it is configured:

| | x86_64 | aarch64 |
|---|---|---|
| Libraries | bundled Agora C++ SDK 2.2.8 | Agora Java SDK 2.3.0 native libs ([`io.agora:rtm-java-aarch64`](https://repo1.maven.org/maven2/io/agora/rtm-java-aarch64/2.3.0/), Maven Central) |
| Headers | bundled 2.2.8 | official Agora C++ SDK 2.3.0 |
| SONAME `libagora_rtm_sdk.so` | present | added with `patchelf` (the Java SDK build has none, otherwise the binary would record an absolute build path as `DT_NEEDED`) |

The aarch64 `.so` from the Java SDK links against the same C++ core and
exports the same three symbols as the C++ SDK (`createAgoraRtmClient`,
`getErrorReason`, `getVersion`), so it is a drop-in replacement. Headers are
upgraded **together with** the libraries: 2.2.8 and 2.3.0 are not ABI
compatible (`RtmConfig` gained a member, `IRtmEventHandler` lost a virtual).

aarch64 RPMs are produced by COPR only (GitHub Actions runs on x86_64
runners).

Two further aarch64 adjustments live in the spec and in `patches/0004`:

- `libquadmath-devel` is build-required **only** on `x86_64`
  (`%ifnarch aarch64`): Fedora 45 aarch64 does not ship the package and
  nothing in the build links against `-lquadmath`.
- patch `0004-blosc-c99.patch` (see above) — Blosc's `-std=gnu99` is added
  only for x86 processors in its `CMakeLists.txt`.

## Project Structure

```
ElegooSlicer-rpm/
├── .copr/Makefile              # COPR SRPM build script
├── .github/workflows/          # GitHub Actions workflow
├── elegoo-slicer.spec          # RPM spec file
├── patches/
│   ├── 0001-deps-system-openssl-curl.patch
│   ├── 0002-elegoolink-system-curl-algorithm.patch
│   ├── 0003-aarch64-agora.patch
│   └── 0004-blosc-c99.patch
└── README.md
```

## License

AGPL-3.0 (same as ElegooSlicer)