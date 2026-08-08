# -*- rpm-spec -*-
#
# ElegooSlicer RPM spec
# Версія: @VERSION@ (базується на OrcaSlicer v2.4.2)
# Встановлення: /opt/ElegooSlicer
# Стратегія залежностей: системні бібліотеки де можливо,
#   бундловані через deps/ де версії несумісні або пакет відсутній.
#
# Patches:
#   0001 — deps/CMakeLists.txt: виявлення системних OpenSSL та CURL (поза FLATPAK)
#   0002 — elegoolink/elegoolink.cmake: системний CURL (${CURL_PKG}) +
#         PATCH_COMMAND додає #include <algorithm> для GCC 16
#

Name:           elegoo-slicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source FDM slicer for Elegoo printers (based on OrcaSlicer)
License:        AGPL-3.0-only
URL:            https://github.com/elegoo-repo/ElegooSlicer
Source0:        ElegooSlicer-%{version}.tar.gz
Source1:        README.md

# Патч 1: deps/CMakeLists.txt — виявляти системні OpenSSL+CURL
Patch1:         0001-deps-system-openssl-curl.patch
# Патч 2: elegoolink/elegoolink.cmake — системний CURL + #include <algorithm>
#         для elegoo-link (GCC 16), застосовується під час deps build
Patch2:         0002-elegoolink-system-curl-algorithm.patch

# Тестування та debug-пакунок не збираємо; бінарник не стрипуємо
%global debug_package %{nil}

# ────────────────────────────────────────────────────────────────────────────
# Build tools
# ────────────────────────────────────────────────────────────────────────────
BuildRequires:  cmake >= 3.13
BuildRequires:  ninja-build
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  git-lfs
BuildRequires:  make
BuildRequires:  patch
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  m4
BuildRequires:  texinfo
BuildRequires:  gettext
BuildRequires:  perl-FindBin
BuildRequires:  perl-IPC-Cmd
BuildRequires:  python3
BuildRequires:  wget

# ── Системні devel-пакети (сумісні версії) ──────────────────────────────────
# eigen3 5.0.1 = точне співпадіння
BuildRequires:  eigen3-devel >= 5.0.1
# TBB 2022.3.0 > бундл 2021.5.0 — сумісний
BuildRequires:  tbb-devel >= 2021.5
# GLFW 3.4 = точне співпадіння
BuildRequires:  glfw-devel >= 3.4
# GLEW 2.2.0 = точне співпадіння
BuildRequires:  glew-devel >= 2.2
# NLopt 2.10 > бундл 2.5 — сумісний
BuildRequires:  NLopt-devel >= 2.5
# CGAL 6.1.2 > бундл 5.6.3 — header-only, сумісний
BuildRequires:  CGAL-devel >= 5.6
# cereal 1.3.2 > бундл 1.3.0 — header-only, сумісний
BuildRequires:  cereal-devel >= 1.3
# GMP 6.3.0 > бундл 6.2.1 — сумісний
BuildRequires:  gmp-devel >= 6.2
# MPFR 4.2.2 = точне співпадіння
BuildRequires:  mpfr-devel >= 4.2
# Qhull 8.0.2 = точне співпадіння
BuildRequires:  qhull-devel >= 8.0
# Draco 1.5.7 = точне співпадіння
BuildRequires:  draco-devel >= 1.5.7
BuildRequires:  draco-static
# Blosc 1.21.6 > бундл 1.17.0 — сумісний
BuildRequires:  blosc-devel >= 1.17
# zlib-ng compat > bundled 1.2.13
BuildRequires:  zlib-ng-compat-devel
# libpng 1.6.58 > бундл 1.6.35 — сумісний
BuildRequires:  libpng-devel >= 1.6
BuildRequires:  expat-devel
# freetype 2.14 > бундл 2.12 — сумісний
BuildRequires:  freetype-devel >= 2.12
# libjpeg-turbo 3.1.3 > бундл 3.0.1 — сумісний
BuildRequires:  libjpeg-turbo-devel >= 3.0
# OpenSSL 3.5.7 > бундл 3.1.8 — сумісний; використовується system
BuildRequires:  openssl-devel >= 3.1
# libcurl — системний
BuildRequires:  libcurl-devel
# OpenCV 4.13.0 > бундл 4.6.0 — сумісний
BuildRequires:  opencv-devel >= 4.6
# OpenEXR — бундлюється (bundled 2.5.5 vs system OpenEXR 3.x несумісні)
BuildRequires:  openexr-devel

# ── Системні GUI/graphics залежності ────────────────────────────────────────
BuildRequires:  dbus-devel
BuildRequires:  gtk3-devel
BuildRequires:  mesa-libGLU-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  libglvnd-devel
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  eglexternalplatform-devel
BuildRequires:  extra-cmake-modules
BuildRequires:  libsecret-devel
BuildRequires:  webkit2gtk4.1-devel
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-good
BuildRequires:  gstreamermm-devel
BuildRequires:  libspnav-devel
BuildRequires:  libmspack-devel
BuildRequires:  libquadmath-devel
BuildRequires:  desktop-file-utils

# ────────────────────────────────────────────────────────────────────────────
# Runtime Requires
# ────────────────────────────────────────────────────────────────────────────
Requires:       tbb >= 2021.5
Requires:       openssl-libs >= 3.1
Requires:       libcurl
Requires:       dbus-libs
Requires:       gtk3
Requires:       mesa-libGL
Requires:       mesa-libGLU
Requires:       libglvnd-glx
Requires:       gstreamer1
Requires:       gstreamer1-plugins-good
Requires:       libsecret
Requires:       NLopt
Requires:       opencv >= 4.6

%description
ElegooSlicer — відкритий FDM-слайсер на базі OrcaSlicer v2.4.2,
оптимізований для принтерів Elegoo (серії Centauri, Neptune та ін.).

Встановлення: /opt/ElegooSlicer

Особливості:
- Підтримка багатоматеріального друку
- Вбудовані інструменти калібрування
- Мережевий друк (LAN/WAN)
- Профілі для принтерів Elegoo

# ────────────────────────────────────────────────────────────────────────────
%prep
%setup -q -n ElegooSlicer-%{version}

# Оновлюємо дату збірки у version.inc
sed -i "s/+_UNKNOWN/_$(date '+%%F')/" version.inc

# Застосовуємо патчі
%patch -P1 -p1
%patch -P2 -p1
# Патч 2 містить PATCH_COMMAND, який виправляє event_system.h у cloned
# elegoo-link під час deps/build (додає <algorithm> для GCC 16).

# ────────────────────────────────────────────────────────────────────────────
%build
# Обмеження паралелізму до 2 потоків
export CMAKE_BUILD_PARALLEL_LEVEL=2
export CMAKE_POLICY_VERSION_MINIMUM=3.5

# ── Крок 1: залежності (deps/) ───────────────────────────────────────────────
# Бундлуємо: Boost 1.84, wxWidgets 3.3.2, OpenVDB (custom fork tamasmeszaros),
#            OCCT 7.6.0, OpenEXR 2.5.5, TBB 2021.5, ixwebsocket 11.4.6,
#            PahoMqttCpp 1.5.3, elegoolink (ELEGOO-3D/elegoo-link),
#            Sentry 0.14.2, libnoise, OpenCSG 1.4.2, GLEW (local src),
#            Draco (local build), Eigen (header-only), CGAL, cereal, NLopt.
# Системні: OpenSSL 3.5.7, libcurl 8.18.0, expat 2.8.1, zlib-ng, libpng, JPEG.

mkdir -p deps/build
cmake -S deps -B deps/build \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DDEP_WX_GTK3=ON \
    -DDESTDIR="%{_builddir}/ElegooSlicer-%{version}/deps/build/ElegooSlicer_dep"

cmake --build deps/build

# Звільняємо місце (GitHub runners невеликі): прибираємо сирці та проміжні кеші
# окремих dep_*-prefix (збережені libs/headers/usr/local залишаються),
# разом зі свжаченими з git збірками.
find deps/build -maxdepth 1 -type d -name 'dep_*-prefix' -print0 | \
while IFS= read -r -d '' d; do
    rm -rf "$d/src" "$d/stamp" 2>/dev/null || true
done
rm -rf deps/build/downloads

# ── Крок 2: основна збірка ───────────────────────────────────────────────────
mkdir -p build
cmake -S . -B build \
    -G "Ninja Multi-Config" \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_PREFIX_PATH="%{_builddir}/ElegooSlicer-%{version}/deps/build/ElegooSlicer_dep/usr/local" \
    -DCMAKE_INSTALL_PREFIX=/opt/ElegooSlicer \
    -DSLIC3R_STATIC=1 \
    -DSLIC3R_GTK=3 \
    -DBBL_RELEASE_TO_PUBLIC=1 \
    -DBBL_INTERNAL_TESTING=0 \
    -DELEGOO_INTERNAL_TESTING=0 \
    -DORCA_TOOLS=ON \
    -DSLIC3R_PCH=ON \
    -DBUILD_TESTS=OFF

cmake --build build --config Release --target ElegooSlicer
cmake --build build --config Release --target ElegooSlicer_profile_validator

# ────────────────────────────────────────────────────────────────────────────
%install
# cmake install з DESTDIR
DESTDIR=%{buildroot} cmake --install build --config Release

# Wrapper-скрипт в /usr/bin
# Додаємо DIR/bin до LD_LIBRARY_PATH, щоб були видимі вбудовані
# libagora_rtm_sdk.so і libaosl.so (Agora SDK від elegoo-link).
install -D -m 755 /dev/stdin %{buildroot}%{_bindir}/elegoo-slicer << 'LAUNCHER'
#!/usr/bin/bash
DIR="/opt/ElegooSlicer"
export LD_LIBRARY_PATH="$DIR/bin:$LD_LIBRARY_PATH"
exec "$DIR/bin/elegoo-slicer" "$@"
LAUNCHER

# .desktop у стандартне місце
install -D -m 644 \
    %{buildroot}/opt/ElegooSlicer/resources/applications/com.elegoo3d.elegoo-slicer.desktop \
    %{buildroot}%{_datadir}/applications/elegoo-slicer.desktop

# Додаємо model/obj у MimeType (підтримка OBJ-файлів)
sed -i 's|MimeType=|MimeType=model/obj;|' \
    %{buildroot}%{_datadir}/applications/elegoo-slicer.desktop

# Іконки з вбудованих ресурсів
for SIZE in 32 128 192; do
    install -D -m 644 \
        resources/images/ElegooSlicer_${SIZE}px.png \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/ElegooSlicer.png
done

# Документація (README)
install -D -m 644 %{SOURCE1} %{buildroot}%{_pkgdocdir}/README.md

# ────────────────────────────────────────────────────────────────────────────
%post
/usr/bin/update-desktop-database %{_datadir}/applications &>/dev/null ||:
/usr/bin/gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null ||:

%postun
/usr/bin/update-desktop-database %{_datadir}/applications &>/dev/null ||:
/usr/bin/gtk-update-icon-cache -f -t %{_datadir}/icons/hicolor &>/dev/null ||:

# ────────────────────────────────────────────────────────────────────────────
%files
%license LICENSE.txt
%dir /opt/ElegooSlicer
/opt/ElegooSlicer/LICENSE.txt
/opt/ElegooSlicer/bin/
/opt/ElegooSlicer/resources/
%{_bindir}/elegoo-slicer
%{_datadir}/applications/elegoo-slicer.desktop
%{_datadir}/icons/hicolor/32x32/apps/ElegooSlicer.png
%{_datadir}/icons/hicolor/128x128/apps/ElegooSlicer.png
%{_datadir}/icons/hicolor/192x192/apps/ElegooSlicer.png
%doc %{_pkgdocdir}/README.md

# ────────────────────────────────────────────────────────────────────────────
%changelog
* Sat Aug 08 2026 ElegooSlicer RPM Packager <rpm@elegoo.com> - @VERSION@-@RELEASE@
- Видалено CHANGELOG.md, DEPS.md, build-local.sh із проєкту
- Замінено spec на версію з ElegooSlicer-rpm-all (системні OpenSSL+CURL)
- Додано патчі 0001 (deps: system OpenSSL/CURL) та 0002 (elegoolink CURL+GCC16)
- Інкремент реліза до 4
- README.md оновлено відповідно до нової структури