# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [1.0.1] - 2026-07-08

### Added
- GitHub Actions workflow for automated RPM builds
- Automated upload of src.rpm and x86_64.rpm to GitHub Releases
- CHANGELOG.md
- README.md with CI/release badges and donate button

### Changed
- Limit build parallelism to 2 jobs to avoid OOM on CI

### Removed
- Unused files: result.json, elegoo-slicer-full.spec

### Fixed
- RPATH issue: use chrpath to strip build-time paths from binary
- GCC 16 compatibility: add `#include <algorithm>` patch for elegoolink
- Fix MIME type for 3MF files: use registered `model/3mf` instead of non-standard `application/x-3mf`

## [1.0.0] - 2026-07-03

### Added
- Initial RPM packaging for ElegooSlicer
- Spec file for building on Fedora 44
- Support for x86_64 architecture
