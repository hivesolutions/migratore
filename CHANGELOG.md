# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* New `is_applied` method in `Database` class that returns `True` only when the most recent successful entry for a migration UUID is not a `Rollback`

### Changed

* Loader operations (`upgrade`, `dry_upgrade`, `get_current_migration`, `get_last_migration`) now use `is_applied` instead of `exist_uuid` so migrations that were rolled back can be re-applied
* Dropped the `migration.timestamp > db.timestamp()` filter in loader operations in favor of the precise `is_applied` check
* `Database.timestamp` is now rollback-aware: returns the timestamp of the most recently applied migration whose latest operation is not a `Rollback`

### Fixed

*

## [0.7.0] - 2026-05-13

### Added

* New `downgrade` command that runs the `rollback` of the last applied migration, raising an error if `rollback` is not implemented
* New `dry_downgrade` command that prints the last applied migration without rolling it back

### Changed

* Improved `squash` command description format to use multiline strings with newlines for better readability

## [0.6.0] - 2026-01-07

### Added

* New `squash` command to combine multiple migrations into a single file, supporting all migration methods (`run`, `run_partial`, `run_skip`, `cleanup`, `rollback`)

## [0.5.9] - 2026-01-07

### Added

* New `exist_uuid` method in `Database` class to check if a migration UUID already exists
* Loader tests in `test/loader.py` for `dry_upgrade` and `exist_uuid` functionality

### Changed

* Improved `dry_upgrade` to also check UUID existence, not just timestamp

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
