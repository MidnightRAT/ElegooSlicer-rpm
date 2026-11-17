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
#   0003 — elegoolink/elegoolink.cmake: на aarch64 підміняє бандліновані
#         x86_64 бібліотеки Agora RTM SDK на aarch64 (див. %prep)
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
# Патч 3: elegoolink/elegoolink.cmake — лише aarch64: підміна Agora RTM SDK
#         (бандл містить лише x86_64 .so); нічого не робить без staged SDK
Patch3:         0003-aarch64-agora.patch

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

# ── aarch64: завантаження та підготовка Agora RTM SDK (див. %prep) ──────────
%ifarch aarch64
BuildRequires:  unzip
BuildRequires:  patchelf
%endif

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
# libquadmath-devel не існує в Fedora 45 aarch64 (GCC aarch64 не збирає
# libquadmath); у джерелах нічого не посилається на -lquadmath.
%ifnarch aarch64
BuildRequires:  libquadmath-devel
%endif
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
# Патч 3 додає до того самого PATCH_COMMAND підміну Agora RTM SDK — вона
# спрацьовує лише коли існує каталог, підготовлений нижче (тільки aarch64).
%patch -P3 -p1

# ── aarch64: Agora RTM SDK 2.3.0 ────────────────────────────────────────────
# thirdparty/agora/linux у elegoo-link містить лише x86_64 .so, а вимкнути
# клауд-функції (ENABLE_CLOUD_FEATURES) не можна — код слайсера використовує
# їх безумовно. Офіційного C++ SDK для Linux aarch64 не існує, тому беремо:
#   * нативні бібліотеки з aarch64-збірки Java SDK Agora RTM 2.3.0
#     (Maven Central) — вона збирається з того самого C++ ядра і експортує
#     ті самі три символи (createAgoraRtmClient, getErrorReason, getVersion);
#   * заголовки C++ SDK 2.3.0 — їх ОБОВ'ЯЗКОВО міняємо разом із .so:
#     2.2.8 і 2.3.0 несумісні за ABI (RtmConfig отримав поле, а
#     IRtmEventHandler втратив віртуальний метод).
# SHA256 підписані; на x86_64 цей блок не виконується.
%ifarch aarch64
AGORA_DIR=%{_builddir}/agora-aarch64
rm -rf "$AGORA_DIR" %{_builddir}/agora-aarch64.jar %{_builddir}/agora-cpp-sdk.zip
mkdir -p "$AGORA_DIR/include"

echo "=== Agora RTM SDK 2.3.0 for aarch64 ==="
wget -q "https://repo1.maven.org/maven2/io/agora/rtm-java-aarch64/2.3.0/rtm-java-aarch64-2.3.0.jar" \
    -O %{_builddir}/agora-aarch64.jar || exit 1
echo "b02805a5e157206bc03048779cf85ed4924264a0f6d2383a64dcaad653905ee4  %{_builddir}/agora-aarch64.jar" \
    | sha256sum -c - || exit 1
unzip -o -j -q %{_builddir}/agora-aarch64.jar \
    native/libagora-rtm-sdk.so native/libaosl.so -d "$AGORA_DIR" || exit 1
mv "$AGORA_DIR/libagora-rtm-sdk.so" "$AGORA_DIR/libagora_rtm_sdk.so"

wget -q "https://download.agora.io/rtm2/release/Agora_RTM_C%%2B%%2B_SDK_for_Linux_v2.3.0.zip" \
    -O %{_builddir}/agora-cpp-sdk.zip || exit 1
echo "2fcbc0305c945cc5126ee2843065678f1f7aa9b9816dbc3d152c13d7dc267c17  %{_builddir}/agora-cpp-sdk.zip" \
    | sha256sum -c - || exit 1
unzip -o -j -q %{_builddir}/agora-cpp-sdk.zip \
    'Agora_Native_SDK_for_Linux_MINI_RTM/rtm/sdk/high_level_api/include/*' \
    -d "$AGORA_DIR/include" || exit 1

echo "2.3.0" > "$AGORA_DIR/version.txt"
rm -f %{_builddir}/agora-aarch64.jar %{_builddir}/agora-cpp-sdk.zip
ls -l "$AGORA_DIR" "$AGORA_DIR/include"
%endif

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

# aarch64: каталог з Agora RTM SDK, підготовлений у %prep. Патч 0003 бачить
# цю змінну і підміняє x86_64-бібліотеки elegoo-link перед його збіркою;
# на x86_64 змінна порожня і патч нічого не робить.
AGORA_CMAKE_ARGS=""
%ifarch aarch64
AGORA_CMAKE_ARGS="-DRPM_AGORA_SRCDIR=%{_builddir}/agora-aarch64"
%endif

cmake -S deps -B deps/build \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DDEP_WX_GTK3=ON \
    $AGORA_CMAKE_ARGS \
    -DDESTDIR="%{_builddir}/ElegooSlicer-%{version}/deps/build/ElegooSlicer_dep"

cmake --build deps/build

cmake --build deps/build

# Звільняємо місце (GitHub runners невеликі): прибираємо сирці та проміжні
# кеші всіх dep_*-prefix КРІМ dep_elegoolink — його source/agora/*.so
# потрібен головній збірці при лінкуванні elegoo-slicer.
# Збережені libs/headers (ElegooSlicer_dep/usr/local) залишаються.
find deps/build -maxdepth 1 -type d -name 'dep_*-prefix' ! -name 'dep_elegoolink-prefix' -print0 | \
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

# Веб-ресурси plugin'а (elegoolink): static_web_server щукає їх за
# resources_dir()/plugins/elegoolink/web (див. ElegooLink::init),
# тоді як upstream кладе їх у resources/web/elegoolink. Дублюємо їх
# в очікуване місце, щоб сторінка пристрою відкривалась.
install -d %{buildroot}/opt/ElegooSlicer/resources/plugins/elegoolink/web
cp -R %{buildroot}/opt/ElegooSlicer/resources/web/elegoolink/. \
      %{buildroot}/opt/ElegooSlicer/resources/plugins/elegoolink/web/

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
* Tue Nov 17 2026 ElegooSlicer RPM Packager <rpm@elegoo.com> - @VERSION@-@RELEASE@
- Додано підтримку aarch64: клауд-функції (Agora RTM SDK) не можна вимкнути,
  а бандл elegoo-link містить лише x86_64 .so. Патч 0003 на aarch64
  підміняє їх aarch64-збіркою SDK 2.3.0 (Maven Central, io.agora) разом
  із заголовками C++ SDK 2.3.0, а libagora_rtm_sdk.so отримує SONAME
  через patchelf (інакше в бінарник потрапив би абсолютний build-шлях)
- Патч 0003 застосовується і на x86_64, але без staged SDK нічого не робить
- Release 5 → 6
* Sat Aug 08 2026 ElegooSlicer RPM Packager <rpm@elegoo.com> - @VERSION@-5
- Виправлено веб UI plugin'а elegoolink: файли копіюються в
  resources/plugins/elegoolink/web (очікуваний static_web_server шлях), а не
  лише у resources/web/elegoolink (виправлено "index.html: No such file")
- Видалено CHANGELOG.md, DEPS.md, build-local.sh із проєкту
- Замінено spec на версію з ElegooSlicer-rpm-all (системні OpenSSL+CURL)
- Додано патчі 0001 (deps: system OpenSSL/CURL) та 0002 (elegoolink CURL+GCC16)
- Інкремент реліза до 5
- README.md оновлено відповідно до нової структури