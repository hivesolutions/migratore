# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

*

### Changed

*

### Fixed

*

## [0.5.8] - 2026-01-06

### Added

* New `touch` command to update a migration's timestamp to the current time
* CLI tests in `test/cli.py` for command resolution and various CLI operations

## [0.5.7] - 2025-11-28

### Added

* Support for rollback of the `Migration`
* Support for the `SAFE` configuration value (controls rollback)

## [0.5.6] - 2025-11-19

### Added

* Support for the `dry_upgrade` operation

## [0.5.5] - 2024-01-08

### Added

* Support for skip of current migration - [#4](https://github.com/hivesolutions/migratore/issues/4)

## [0.5.4] - 2024-01-08

### Changed

* Improved handling of the `environ` CLI command

## [0.5.3] - 2024-01-06

### Fixed

* Condition of the `DB_URL` processing

## [0.5.2] - 2024-01-06

### Changed

* Improved `DB_URL` processing with the `override` flag

## [0.5.1] - 2024-01-06

### Changed

* Propagated `_env` calls and processing

## [0.5.0] - 2024-01-06

### Added

* Ability to load `.env` files
* Support for `DB_URL` environment variable - [#2](https://github.com/hivesolutions/migratore/issues/2)

## [0.4.2] - 2023-01-02

### Changed

* Prints migration description to the STDOUT

## [0.4.1] - 2022-11-27

### Added

* Support for `README.md` file in the `long_description`

## [0.4.0] - 2022-11-27

### Added

* Support for `UNIX_SOCKET` connection

### Changed

* Major release in a while 🎉
* CI/CD model now uses GitHub Actions
