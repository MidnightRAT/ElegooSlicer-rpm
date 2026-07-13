srpm:
	set -e; \
	\
	echo "=== Installing build tools ==="; \
	dnf -y install --skip-unavailable rpmdevtools wget curl unzip; \
	\
	echo "=== Fetching latest release version ==="; \
	VERSION=$$(curl -sf https://api.github.com/repos/ELEGOO-3D/ElegooSlicer/releases/latest \
	  | grep '"tag_name"' | cut -d '"' -f 4 | sed 's/^v//'); \
	if [ -z "$$VERSION" ]; then \
	  echo "ERROR: failed to determine latest version from GitHub API"; \
	  exit 1; \
	fi; \
	echo "Latest version: $${VERSION}"; \
	\
	echo "=== Downloading source tarball ==="; \
	wget -q "https://github.com/ELEGOO-3D/ElegooSlicer/archive/refs/tags/v$${VERSION}.tar.gz" \
	  -O "elegoo-slicer-$${VERSION}-src.tar.gz"; \
	ls -lh "elegoo-slicer-$${VERSION}-src.tar.gz"; \
	\
	echo "=== Preparing rpmbuild tree ==="; \
	rpmdev-setuptree; \
	mkdir -p "$$HOME/rpmbuild/SOURCES" "$$HOME/rpmbuild/SPECS"; \
	cp "elegoo-slicer-$${VERSION}-src.tar.gz" "$$HOME/rpmbuild/SOURCES/"; \
	\
	echo "=== Generating spec file from template ==="; \
	test -f elegoo-slicer.spec || { echo "ERROR: elegoo-slicer.spec not found in repo root"; exit 1; }; \
	sed -e "s/@VERSION@/$${VERSION}/g" \
	    -e "s/@RELEASE@/1/g" \
	    elegoo-slicer.spec > "$$HOME/rpmbuild/SPECS/elegoo-slicer.spec"; \
	\
	echo "=== Building SRPM ==="; \
	rpmbuild -bs \
	  --define "_sourcedir $$HOME/rpmbuild/SOURCES" \
	  --define "_srcrpmdir $(outdir)" \
	  "$$HOME/rpmbuild/SPECS/elegoo-slicer.spec"; \
	\
	echo "=== Done ==="; \
	ls -la "$(outdir)"
