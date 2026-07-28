# ElegooSlicer 1.5.2.2 — Library Dependencies

## Always built from source (deps/) — no system fallback

| Library | Version | Source |
|---------|---------|--------|
| **Boost** | 1.84.0 | deps/ (download) |
| **wxWidgets** | SoftFever fork | deps/ (git clone) |
| **OCCT** (OpenCASCADE) | 7.6.0 | deps/ (download) |
| **OpenCV** | 4.6.0 | deps/ (download) |
| **OpenVDB** | SoftFever fork (a68fd58) | deps/ (git) — system has incompatible cmake modules |
| **CGAL** | 5.4 | deps/ (download) — system 6.x has breaking API changes |
| **OpenEXR** | 2.5.5 | deps/ (download) — system 3.x lacks IlmBase::Half |
| **GLFW** | 3.3.7 | deps/ (download) |
| **OpenCSG** | 1.4.2 | deps/ (download) |
| **ixwebsocket** | 11.4.6 | deps/ (download) |
| **PahoMqttCpp** | 1.5.3 (tag) | deps/ (git clone) |
| **elegoolink** | Elegoo-specific | deps/ (git clone) |
| **Sentry** | 0.14.2 | deps/ (git) — optional, see patch 0005 |
| **libnoise** | 1.0 (SoftFever fork) | deps/ (git clone) |
| **NanoSVG** | SoftFever fork (863f6aa) | deps/ (git clone) |

## Embedded source (deps_src/) — compiled as part of the main project

### Header-only (INTERFACE)

| Library | Version | Path | Notes |
|---------|---------|------|-------|
| **nlohmann/json** | 3.10.4 | deps_src/nlohmann/ | Replaced by system `json-devel` (patch 0010) |
| **Eigen** | 3.3.7 | deps_src/eigen/ | Can use system `eigen3-devel` but disabled (version conflict) |
| **AGG** | 2.4 (svn r128) | deps_src/agg/ | |
| **ankerl::unordered_dense** | 4.5.0 | deps_src/ankerl/ | |
| **fast_float** | 2.0.0 | deps_src/fast_float/ | |
| **NanoSVG** | SoftFever fork | deps_src/nanosvg/ | Header-only copy; deps/ builds a separate library version |
| **spline** | — | deps_src/spline/ | Single header |
| **stb_dxt** | — | deps_src/stb_dxt/ | Single header |
| **libigl** | — | deps_src/libigl/ | Can use system `libigl` via `find_package(libigl QUIET)` |

### Static libraries

| Library | Version | Path |
|---------|---------|------|
| **ClipperLib** | 6.2.6 | deps_src/clipper/ |
| **Dear ImGui** | 1.83 | deps_src/imgui/ |
| **ImGuizmo** | 1.83 (WIP 1.84) | deps_src/imguizmo/ |
| **MCUT** | 1.2.0 | deps_src/mcut/ |
| **miniz** | 2.1.0 | deps_src/miniz/ |
| **minilzo** (LZO) | 2.10 | deps_src/minilzo/ |
| **Qhull** | 2015.2 | deps_src/qhull/ (can use system >=7.2) |
| **QOI** | commit 6c0831f | deps_src/qoi/ |
| **admesh** | — | deps_src/admesh/ |
| **Expat** | 2.2.0 (modified) | deps_src/expat/ |
| **HIDAPI** | 0.9.0 | deps_src/hidapi/ |
| **Shiny** (Profiler) | 2.6 RC1 | deps_src/Shiny/ |
| **glu-libtess** | Mesa GLU (Jun 2016) | deps_src/glu-libtess/ |
| **libnest2d** | — | deps_src/libnest2d/ |
| **hints** | — | deps_src/hints/ |
| **semver** | — | deps_src/semver/ |

## System packages (BuildRequires) that replace built/bundled deps

| RPM Package | Replaces | Mechanism |
|-------------|----------|-----------|
| **openssl-devel** | dep_OpenSSL | `find_package(OpenSSL 1.1...<3.2)` before build |
| **libcurl-devel** | dep_CURL | `find_package(CURL)` before build |
| **tbb-devel** | dep_TBB | Patched: `find_package(TBB)` when `USE_SYSTEM_LIBS=ON` |
| **blosc-devel** | dep_Blosc | Patched: `pkg_check_modules(BLOSC blosc)` when `USE_SYSTEM_LIBS=ON` |
| **NLopt-devel** | dep_NLopt | Patched: `find_package(NLopt)` when `USE_SYSTEM_LIBS=ON` |
| **cereal-devel** | dep_Cereal | Patched: `find_package(cereal)` when `USE_SYSTEM_LIBS=ON` |
| **glew-devel** | dep_GLEW | Patched: `find_package(GLEW)` when `USE_SYSTEM_LIBS=ON` |
| **libjpeg-turbo-devel** | dep_JPEG | `find_package(JPEG)` before build |
| **libpng-devel** | dep_PNG | `find_package(PNG QUIET)` before build |
| **freetype-devel** | dep_FREETYPE | `find_package(Freetype)` before build |
| **expat-devel** | dep_EXPAT | `find_package(EXPAT)` before build |
| **zlib-ng-compat-devel** | dep_ZLIB | `find_package(ZLIB)` before build |
| **mpfr-devel** | dep_MPFR | Used when `USE_SYSTEM_LIBS=ON` |
| **json-devel** | deps_src/nlohmann/ | Patch 0010 rewrites includes to `<nlohmann/json.hpp>` |
| **eigen3-devel** | deps_src/eigen/ | Available but disabled — system version conflicts with libigl |
| **imath-devel** | OpenEXR 3.x Imath compat | Patch 0004 — bridges Imath-3 with OpenVDB |

## System packages that do NOT replace built deps

| RPM Package | Notes |
|-------------|-------|
| **opencv-devel** | OpenCV always built from source in deps/ |
| **opencascade-devel** | OCCT always built from source in deps/ |
| **openvdb-devel** | System cmake module incompatible |
| **CGAL-devel** | System 6.x API breaks bundled code |

## System-only dependencies (never bundled)

| RPM Package | Purpose |
|-------------|---------|
| cmake >= 3.13, ninja-build | Build system |
| gcc gcc-c++ | Compiler |
| pkgconf, autoconf, automake, libtool, m4 | Build tools |
| git, wget, curl, unzip, file | Download/extraction |
| perl-FindBin, perl-IPC-Cmd | Perl build scripts |
| libquadmath-devel, nasm | Compiler support |
| dbus-devel, gtk3-devel, webkit2gtk4.1-devel | Desktop GUI |
| mesa-libGLU-devel, mesa-libGL-devel | OpenGL |
| fontconfig-devel, pango-devel | Fonts/rendering |
| extra-cmake-modules, eglexternalplatform-devel | CMake/EGL |
| gstreamer1-devel, gstreamer1-plugins-base-devel, gstreamermm-devel | Media |
| wayland-protocols-devel, libxkbcommon-devel | Wayland |
| libX11-devel, libXi-devel, libXrandr-devel, libXinerama-devel, libXcursor-devel, libXcomposite-devel, libXdamage-devel, libXext-devel, libXtst-devel, libXfixes-devel, libXmu-devel | X11 |
| at-spi2-core-devel, libepoxy-devel | Accessibility/GL |
| libspnav-devel, libsecret-devel, libmspack-devel | Misc |
| texinfo, chrpath | Build utilities |
| glfw-devel | Available but GLFW always built from source |

## Libraries with fallback mechanism (system OR bundled)

These try `find_package()` / `pkg_check_modules()` first, then fall back to building:

**OpenSSL**, **cURL**, **ZLIB**, **PNG**, **JPEG**, **FreeType**, **Expat**, **TBB**, **NLopt**, **Cereal**, **GLEW**, **GMP**, **Blosc**, **nlohmann/json** (via include path), **Eigen**, **libigl**, **Qhull** (deps_src), **Sentry** (optional)
