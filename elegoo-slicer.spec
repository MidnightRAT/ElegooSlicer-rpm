%global debug_package %{nil}

Name:           elegoo-slicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source slicer for FDM 3D printers
License:        AGPL-3.0
URL:            https://github.com/ELEGOO-3D/ElegooSlicer
Source0:        %{name}-%{version}-src.tar.gz

# Runtime deps
Requires:       gtk3
Requires:       webkit2gtk4.1
Requires:       mesa-libGL
Requires:       mesa-libEGL
Requires:       dbus-libs
Requires:       libX11
Requires:       pango
Requires:       fontconfig
Requires:       freetype

# Build deps
BuildRequires:  cmake >= 3.13
BuildRequires:  ninja-build
BuildRequires:  gcc gcc-c++
BuildRequires:  pkgconf
BuildRequires:  autoconf automake libtool m4
BuildRequires:  git wget curl unzip file
BuildRequires:  perl-FindBin perl-IPC-Cmd
BuildRequires:  libquadmath-devel
BuildRequires:  nasm
BuildRequires:  dbus-devel gtk3-devel webkit2gtk4.1-devel
BuildRequires:  glew-devel glfw-devel mesa-libGLU-devel mesa-libGL-devel
BuildRequires:  libjpeg-turbo-devel libpng-devel
BuildRequires:  openssl-devel libcurl-devel
BuildRequires:  freetype-devel fontconfig-devel pango-devel
BuildRequires:  eigen3-devel cereal-devel
BuildRequires:  extra-cmake-modules eglexternalplatform-devel
BuildRequires:  gstreamer1-devel gstreamer1-plugins-base-devel gstreamermm-devel
BuildRequires:  wayland-protocols-devel libxkbcommon-devel
BuildRequires:  libX11-devel libXi-devel libXrandr-devel libXinerama-devel
BuildRequires:  libXcursor-devel libXcomposite-devel libXdamage-devel libXext-devel
BuildRequires:  libXtst-devel libXfixes-devel libXmu-devel
BuildRequires:  at-spi2-core-devel libepoxy-devel
BuildRequires:  libspnav-devel libsecret-devel libmspack-devel
BuildRequires:  texinfo
BuildRequires:  chrpath
# System lib deps
BuildRequires:  tbb-devel
BuildRequires:  blosc-devel
BuildRequires:  NLopt-devel
BuildRequires:  opencv-devel
BuildRequires:  opencascade-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  expat-devel
BuildRequires:  openvdb-devel
BuildRequires:  mpfr-devel
BuildRequires:  CGAL-devel
BuildRequires:  imath-devel

%description
ElegooSlicer is an open-source slicer compatible with most FDM printers.
Based on OrcaSlicer/PrusaSlicer, supporting STL, OBJ, 3MF file formats.

%prep
%setup -n ElegooSlicer-%{version}

# Remove bundled nlohmann (conflicts with system nlohmann from opencv-devel on GCC 16)
rm -rf deps_src/nlohmann
sed -i '/add_subdirectory(nlohmann)/d' deps_src/CMakeLists.txt

# Patch FindOpenVDB.cmake for Fedora 44 (OpenEXR 3.x, Imath instead of IlmBase)
python3 << 'PYEOF'
with open('cmake/modules/FindOpenVDB.cmake', 'r') as f:
    c = f.read()
c = c.replace(
"""find_package(IlmBase QUIET)
if(NOT IlmBase_FOUND)
  pkg_check_modules(IlmBase QUIET IlmBase)
endif()
if (IlmBase_FOUND AND NOT TARGET IlmBase::Half)
  message(STATUS "Falling back to IlmBase found by pkg-config...")

  find_library(IlmHalf_LIBRARY NAMES Half)
  if(IlmHalf_LIBRARY-NOTFOUND OR NOT IlmBase_INCLUDE_DIRS)
    just_fail("IlmBase::Half can not be found!")
  endif()
  
  add_library(IlmBase::Half UNKNOWN IMPORTED)
  set_target_properties(IlmBase::Half PROPERTIES
    IMPORTED_LOCATION "${IlmHalf_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${IlmBase_INCLUDE_DIRS}")
elseif(NOT IlmBase_FOUND)
  just_fail("IlmBase::Half can not be found!")
endif()""",
"""# Fedora 44: OpenEXR 3.x moved IlmBase to Imath
find_package(Imath QUIET)
if(Imath_FOUND AND NOT TARGET IlmBase::Half)
  message(STATUS "Creating IlmBase::Half from Imath::Imath (OpenEXR 3.x)")
  add_library(IlmBase::Half INTERFACE IMPORTED)
  set_target_properties(IlmBase::Half PROPERTIES
    INTERFACE_LINK_LIBRARIES "Imath::Imath")
else()
  find_package(IlmBase QUIET)
  if(NOT IlmBase_FOUND)
    pkg_check_modules(IlmBase QUIET IlmBase)
  endif()
  if (IlmBase_FOUND AND NOT TARGET IlmBase::Half)
    find_library(IlmHalf_LIBRARY NAMES Half)
    if(IlmHalf_LIBRARY-NOTFOUND OR NOT IlmBase_INCLUDE_DIRS)
      just_fail("IlmBase::Half can not be found!")
    endif()
    add_library(IlmBase::Half UNKNOWN IMPORTED)
    set_target_properties(IlmBase::Half PROPERTIES
      IMPORTED_LOCATION "${IlmHalf_LIBRARY}"
      INTERFACE_INCLUDE_DIRECTORIES "${IlmBase_INCLUDE_DIRS}")
  elseif(NOT IlmBase_FOUND)
    just_fail("IlmBase::Half can not be found!")
  endif()
endif()""")
c = c.replace(
    'if(OpenVDB_USES_BLOSC)\n  find_package(Blosc REQUIRED)\nendif()',
    '# Blosc already found by fallback search above')
with open('cmake/modules/FindOpenVDB.cmake', 'w') as f:
    f.write(c)
print('FindOpenVDB patched')
PYEOF

# Make sentry optional (no system sentry package on Fedora)
python3 << 'PYEOF'
with open('src/CMakeLists.txt', 'r') as f:
    c = f.read()
c = c.replace(
    'find_package(sentry CONFIG REQUIRED)',
    'find_package(sentry CONFIG QUIET)')
c = c.replace(
    'target_link_libraries(ElegooSlicer sentry::sentry)\n# Setup sentry crashpad_handler for all platforms\nelegooslicer_setup_sentry_handler(ElegooSlicer)',
    'if(sentry_FOUND)\n    target_link_libraries(ElegooSlicer sentry::sentry)\n    elegooslicer_setup_sentry_handler(ElegooSlicer)\nendif()')
with open('src/CMakeLists.txt', 'w') as f:
    f.write(c)
print('Sentry made optional')
PYEOF

# Patch deps/CMakeLists.txt: cmake 4 compat for ExternalProject sub-builds
sed -i '1i set(CMAKE_POLICY_VERSION_MINIMUM 3.5)' deps/CMakeLists.txt
python3 << 'PYEOF'
with open('deps/CMakeLists.txt') as f:
    c = f.read()
c = c.replace(
    '-DBUILD_SHARED_LIBS:BOOL=OFF\n            ${_cmake_osx_arch}\n            "${_configs_line}"\n            ${DEP_CMAKE_OPTS}\n            ${P_ARGS_CMAKE_ARGS}',
    '-DBUILD_SHARED_LIBS:BOOL=OFF\n            -DCMAKE_POLICY_VERSION_MINIMUM:STRING=3.5\n            ${_cmake_osx_arch}\n            "${_configs_line}"\n            ${DEP_CMAKE_OPTS}\n            ${P_ARGS_CMAKE_ARGS}')
with open('deps/CMakeLists.txt', 'w') as f:
    f.write(c)
print('deps/CMakeLists.txt patched')
PYEOF

# Create fix-cmake4.sh: patches cmake_minimum_required(VERSION 2.x) and missing includes
cat > deps/fix-cmake4.sh << 'FIXSCRIPT'
#!/bin/bash
find "$1" \( -name CMakeLists.txt -o -name "*.cmake" \) -exec grep -l "cmake_minimum_required(VERSION 2" {} + 2>/dev/null | while read f; do
  sed -i 's/cmake_minimum_required(VERSION 2/cmake_minimum_required(VERSION 3.5/g' "$f"
done
if [ -f "$1/include/events/event_system.h" ]; then
  head -1 "$1/include/events/event_system.h" | grep -q "algorithm" || \
    sed -i '1i #include <algorithm>' "$1/include/events/event_system.h"
fi
FIXSCRIPT
chmod +x deps/fix-cmake4.sh

# Patch wxWidgets: add PATCH_COMMAND to fix cmake_minimum_required before configure
python3 << 'PYEOF'
import os
with open('deps/wxWidgets/wxWidgets.cmake') as f:
    c = f.read()
script = os.path.abspath('deps/fix-cmake4.sh')
c = c.replace(
    '    FORCE_RELEASE_CONFIG  # wxWidgets doesn\'t support RelWithDebInfo configuration',
    f'    PATCH_COMMAND {script} <SOURCE_DIR>\n    FORCE_RELEASE_CONFIG  # wxWidgets doesn\'t support RelWithDebInfo configuration')
with open('deps/wxWidgets/wxWidgets.cmake', 'w') as f:
    f.write(c)
print('wxWidgets PATCH_COMMAND added')
PYEOF

# Patch elegoolink: add PATCH_COMMAND to fix cmake_minimum_required and missing includes
python3 << 'PYEOF'
import os
with open('deps/elegoolink/elegoolink.cmake') as f:
    c = f.read()
script = os.path.abspath('deps/fix-cmake4.sh')
c = c.replace(
    'elegooslicer_add_cmake_project(elegoolink',
    f'elegooslicer_add_cmake_project(elegoolink\n    PATCH_COMMAND {script} <SOURCE_DIR>')
with open('deps/elegoolink/elegoolink.cmake', 'w') as f:
    f.write(c)
print('elegoolink PATCH_COMMAND added')
PYEOF

# Download web dependencies (skip if already included in tarball)
mkdir -p resources/plugins/elegoolink/web
if [ ! -d resources/plugins/elegoolink/web/lan_service_web ]; then
  curl -sL "https://github.com/ELEGOO-3D/elegoo-fdm-web/releases/download/20260625/lan_service_web.zip" -o lan_service_web.zip
  unzip -oq lan_service_web.zip -d resources/plugins/elegoolink/web/lan_service_web
  rm lan_service_web.zip
fi
if [ ! -d resources/plugins/elegoolink/web/cloud_service_web ]; then
  curl -sL "https://github.com/ELEGOO-3D/elegoo-fdm-web/releases/download/20260625/cloud_service_web.zip" -o cloud_service_web.zip
  unzip -oq cloud_service_web.zip -d resources/plugins/elegoolink/web/cloud_service_web
  rm cloud_service_web.zip
fi

%build
export CMAKE_POLICY_VERSION_MINIMUM=3.5

# Fedora 44 GCC 16: suppress errors-as-errors warnings
export CXXFLAGS="${CXXFLAGS} -Wno-error=template-body -Wno-error=overloaded-virtual"

# Limit parallelism to avoid OOM on CI (GitHub Actions has ~7GB RAM)
NPROC_DEPS=8
NPROC_BUILD=8

# Build dependencies (skip if already pre-built in SRPM)
if [ ! -d deps/build ]; then
  echo "=== Building dependencies ==="
  mkdir -p deps/build
  cmake -S deps -B deps/build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DDEP_WX_GTK3=ON \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5
  cmake --build deps/build -j${NPROC_DEPS}
else
  echo "=== Dependencies already built, skipping ==="
fi

# Build main app
mkdir -p build
cmake -S . -B build -G "Ninja Multi-Config" \
  -DCMAKE_PREFIX_PATH="$(pwd)/deps/build/destdir/usr/local" \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
  -DSLIC3R_STATIC=1 \
  -DSLIC3R_STATIC_EXCLUDE_GLEW=ON \
  -DSLIC3R_GTK=3 \
  -DBBL_RELEASE_TO_PUBLIC=1 \
  -DBBL_INTERNAL_TESTING=0 \
  -DELEGOO_INTERNAL_TESTING=0 \
  -DSLIC3R_PCH=OFF
cmake --build build --config Release --target ElegooSlicer -j${NPROC_BUILD}

# Generate localization
./scripts/run_gettext.sh || true

%install
# Create installation directories
mkdir -p %{buildroot}/opt/ElegooSlicer/bin/crashpad
mkdir -p %{buildroot}/opt/ElegooSlicer/resources

# Install binary
cp build/src/Release/elegoo-slicer %{buildroot}/opt/ElegooSlicer/bin/
chmod 755 %{buildroot}/opt/ElegooSlicer/bin/elegoo-slicer
# Fix RPATHs - remove build-time paths
chrpath -d %{buildroot}/opt/ElegooSlicer/bin/elegoo-slicer 2>/dev/null || true

# Install bundled shared libraries
cp -f build/src/Release/libaosl.so %{buildroot}/opt/ElegooSlicer/bin/ 2>/dev/null || true
cp -f build/src/Release/libagora_rtm_sdk.so %{buildroot}/opt/ElegooSlicer/bin/ 2>/dev/null || true

# Install crashpad handler
cp -f build/src/Release/crashpad/crashpad_handler %{buildroot}/opt/ElegooSlicer/bin/crashpad/ 2>/dev/null || true

# Install resources
cp -R resources/* %{buildroot}/opt/ElegooSlicer/resources/

# Create launcher script
printf '#!/usr/bin/bash\nDIR=$(dirname "$(readlink -f "$0")")\nexport LD_LIBRARY_PATH="$DIR/bin:$LD_LIBRARY_PATH"\nexec "$DIR/bin/elegoo-slicer" "$@"\n' > %{buildroot}/opt/ElegooSlicer/elegoo-slicer.sh
chmod 755 %{buildroot}/opt/ElegooSlicer/elegoo-slicer.sh

# Desktop integration
mkdir -p %{buildroot}/usr/share/applications
cat > %{buildroot}/usr/share/applications/elegoo-slicer.desktop << 'DESKTOP'
[Desktop Entry]
Name=ElegooSlicer
Comment=Open-source slicer for FDM 3D printers
Exec=/opt/ElegooSlicer/elegoo-slicer.sh %f
Icon=elegoo-slicer
Terminal=false
Type=Application
Categories=Utility;Engineering;
MimeType=model/stl;model/obj;model/3mf;
DESKTOP

# Install icons
for size in 32 64 128 192; do
  mkdir -p %{buildroot}/usr/share/icons/hicolor/${size}x${size}/apps
  cp resources/images/ElegooSlicer_${size}px.png \
     %{buildroot}/usr/share/icons/hicolor/${size}x${size}/apps/elegoo-slicer.png 2>/dev/null || true
done

# License
install -Dm644 LICENSE.txt %{buildroot}/usr/share/licenses/%{name}/LICENSE

%files
/opt/ElegooSlicer
/usr/share/applications/elegoo-slicer.desktop
/usr/share/icons/hicolor/*/apps/elegoo-slicer.png
/usr/share/licenses/%{name}/LICENSE

%changelog
