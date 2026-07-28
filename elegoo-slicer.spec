%global debug_package %{nil}

Name:           elegoo-slicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source slicer for FDM 3D printers
License:        AGPL-3.0
URL:            https://github.com/ELEGOO-3D/ElegooSlicer
Source0:        %{name}-%{version}-src.tar.gz
Source1:        CHANGELOG.md
Source2:        README.md
Source3:        DEPS.md
# Patches
Patch2:         0002-use-system-libs.patch
Patch3:         0003-remove-bundled-nlohmann.patch
Patch4:         0004-find-openvdb-imath-compat.patch
Patch5:         0005-make-sentry-optional.patch
Patch6:         0006-cmake4-compat-deps.patch
Patch7:         0007-add-fix-cmake4-sh.patch
Patch8:         0008-wxwidgets-patch-command.patch
Patch9:         0009-elegoolink-patch-command.patch
Patch10:        0010-use-system-nlohmann-json.patch

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
BuildRequires:  json-devel

%description
ElegooSlicer is an open-source slicer compatible with most FDM printers.
Based on OrcaSlicer/PrusaSlicer, supporting STL, OBJ, 3MF file formats.

%prep
%setup -n ElegooSlicer-%{version}

%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1
%patch -P7 -p1
%patch -P8 -p1
%patch -P9 -p1
%patch -P10 -p1

# Ensure fix-cmake4.sh is executable (patch may not preserve mode)
chmod +x deps/fix-cmake4.sh

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
NPROC_DEPS=2
NPROC_BUILD=2

# Optionally restore pre-built dependencies from a local cache (skips ~1.5h rebuild)
DEPS_CACHE="${DEPS_CACHE:-}"
if [ ! -d deps/build ] && [ -n "$DEPS_CACHE" ] && [ -d "$DEPS_CACHE" ]; then
  echo "=== Restoring dependencies from cache: $DEPS_CACHE ==="
  mkdir -p deps
  cp -a "$DEPS_CACHE" deps/build
  echo "=== Cache restored ==="
fi

# Build dependencies (skip if already pre-built in SRPM)
if [ ! -d deps/build ]; then
  echo "=== Building dependencies ==="
  mkdir -p deps/build
  cmake -S deps -B deps/build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DDEP_WX_GTK3=ON \
    -DUSE_SYSTEM_LIBS=ON \
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

# Documentation
install -Dm644 %{SOURCE1} %{buildroot}/opt/ElegooSlicer/CHANGELOG.md
install -Dm644 %{SOURCE2} %{buildroot}/opt/ElegooSlicer/README.md
install -Dm644 %{SOURCE3} %{buildroot}/opt/ElegooSlicer/DEPS.md

%files
/opt/ElegooSlicer
/usr/share/applications/elegoo-slicer.desktop
/usr/share/icons/hicolor/*/apps/elegoo-slicer.png
/usr/share/licenses/%{name}/LICENSE
/opt/ElegooSlicer/CHANGELOG.md
/opt/ElegooSlicer/README.md
/opt/ElegooSlicer/DEPS.md

%changelog
