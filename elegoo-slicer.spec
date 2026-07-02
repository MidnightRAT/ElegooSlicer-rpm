%global debug_package %{nil}

Name:           elegoo-slicer
Version:        @VERSION@
Release:        @RELEASE@%{?dist}
Summary:        Open-source slicer for FDM 3D printers
License:        AGPL-3.0
URL:            https://github.com/ELEGOO-3D/ElegooSlicer
Source0:        %{name}-%{version}.tar.gz

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

%description
ElegooSlicer is an open-source slicer compatible with most FDM printers.
Based on OrcaSlicer/PrusaSlicer, supporting STL, OBJ, 3MF file formats.

%prep
%autosetup -n elegoo-slicer-extracted

%build
# Nothing to build - pre-built AppImage

%install
# Create installation directory
mkdir -p %{buildroot}/opt/ElegooSlicer

# Copy extracted AppImage contents
cp -R * %{buildroot}/opt/ElegooSlicer/

# Create launcher script
cat > %{buildroot}/opt/ElegooSlicer/elegoo-slicer.sh << 'LAUNCHER'
#!/usr/bin/bash
DIR=$(dirname "$(readlink -f "$0")")
export LD_LIBRARY_PATH="$DIR/usr/lib:$LD_LIBRARY_PATH"
exec "$DIR/usr/bin/elegoo-slicer" "$@"
LAUNCHER
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
MimeType=model/stl;model/obj;application/x-3mf;
DESKTOP

# Install icons
for size in 32 64 128 192; do
  mkdir -p %{buildroot}/usr/share/icons/hicolor/${size}x${size}/apps
  cp usr/share/icons/hicolor/${size}x${size}/apps/elegoo-slicer.png \
     %{buildroot}/usr/share/icons/hicolor/${size}x${size}/apps/elegoo-slicer.png 2>/dev/null || true
done

%files
/opt/ElegooSlicer
/usr/share/applications/elegoo-slicer.desktop
/usr/share/icons/hicolor/*/apps/elegoo-slicer.png

%changelog
