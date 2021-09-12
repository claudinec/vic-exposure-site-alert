# CHANGELOG

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Changed

- Update `re.search` for tram routes to match variations in data

## [0.3.0] - 2021-09-10

### Added

- Add scheduling
- Add command-line interface to choose scheduling frequency (closes [#7](https://github.com/claudinec/vic-exposure-site-alert/issues/7))

### Changed

- Change logger.info() to logger.debug()
- Look for data and logs directories in .local/share (fixes [#1](https://github.com/claudinec/vic-exposure-site-alert/issues/1))

## [0.2.2] - 2021-09-06

### Added

- Add changelog

### Changed

- Change comments to docstrings

### Fixed

- Fix public transport checks

## [0.2.1] - 2021-09-03

### Changed

- More tidying up

### Removed

- Remove personal `.vscode` settings

### Fixed

- Fix check for `pushcut_devices` in configuration

## [0.2.0] - 2021-09-03

- Add public transport checks

## [0.1.0] - 2021-09-02

- Minimal working version

<!-- Links -->
[keep a changelog]: https://keepachangelog.com/en/1.0.0/
[semantic versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: https://github.com/claudinec/vic-exposure-site-alert/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/claudinec/vic-exposure-site-alert/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/claudinec/vic-exposure-site-alert/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/claudinec/vic-exposure-site-alert/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/claudinec/vic-exposure-site-alert/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/claudinec/vic-exposure-site-alert/releases/tag/v0.1.0
