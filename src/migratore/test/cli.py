#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import shutil
import sys
import tempfile
import unittest

try:
    import unittest.mock as mock
except ImportError:
    mock = None

import migratore


class CLITest(unittest.TestCase):
    def test_command_resolution(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        from migratore import cli

        with mock.patch.object(cli, "run_help") as mock_help:
            original_argv = sys.argv
            try:
                sys.argv = ["migratore", "help"]
                cli.main()
                mock_help.assert_called_once()
            finally:
                sys.argv = original_argv

    def test_command_resolution_version(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        from migratore import cli

        with mock.patch.object(cli, "run_version") as mock_version:
            original_argv = sys.argv
            try:
                sys.argv = ["migratore", "version"]
                cli.main()
                mock_version.assert_called_once()
            finally:
                sys.argv = original_argv

    def test_command_resolution_with_args(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        from migratore import cli

        with mock.patch.object(cli, "run_touch") as mock_touch:
            original_argv = sys.argv
            try:
                sys.argv = ["migratore", "touch", "1391804600"]
                cli.main()
                mock_touch.assert_called_once_with("1391804600")
            finally:
                sys.argv = original_argv

    def test_invalid_command(self):
        from migratore import cli

        original_argv = sys.argv
        try:
            sys.argv = ["migratore", "invalid_command_xyz"]
            with self.assertRaises(RuntimeError) as context:
                cli.main()
            self.assertIn("Invalid command", str(context.exception))
        finally:
            sys.argv = original_argv

    def test_default_command_is_help(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        from migratore import cli

        with mock.patch.object(cli, "run_help") as mock_help:
            original_argv = sys.argv
            try:
                sys.argv = ["migratore"]
                cli.main()
                mock_help.assert_called_once()
            finally:
                sys.argv = original_argv

    def test_run_help_output(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        from migratore import cli

        with mock.patch("builtins.print") as mock_print:
            cli.run_help()

            calls = [str(call) for call in mock_print.call_args_list]
            output = " ".join(calls)

            self.assertIn("version", output)
            self.assertIn("environ", output)
            self.assertIn("list", output)
            self.assertIn("errors", output)
            self.assertIn("mark", output)
            self.assertIn("trace", output)
            self.assertIn("rebuild", output)
            self.assertIn("touch", output)
            self.assertIn("upgrade", output)
            self.assertIn("dry_upgrade", output)
            self.assertIn("skip", output)
            self.assertIn("generate", output)

    def test_run_version_output(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        from migratore import cli, info

        with mock.patch("builtins.print") as mock_print:
            cli.run_version()

            mock_print.assert_called_once()
            output = str(mock_print.call_args)
            self.assertIn(info.NAME, output)
            self.assertIn(info.VERSION, output)

    def test_generate_creates_file(self):
        temp_dir = tempfile.mkdtemp()
        try:
            output_path = os.path.join(temp_dir, "test_migration.py")
            migratore.Migration.generate(path=output_path)

            self.assertTrue(os.path.exists(output_path))

            with open(output_path, "rb") as file:
                content = file.read().decode("utf-8")

            self.assertIn("class Migration", content)
            self.assertIn("self.uuid", content)
            self.assertIn("self.timestamp", content)
            self.assertIn("self.description", content)
            self.assertIn("def run(self, db)", content)
        finally:
            shutil.rmtree(temp_dir)

    def test_generate_uses_timestamp_filename(self):
        temp_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            migratore.Migration.generate()

            files = [f for f in os.listdir(temp_dir) if f.endswith(".py")]
            self.assertEqual(len(files), 1)

            filename = files[0]
            timestamp_str = filename[:-3]
            self.assertTrue(timestamp_str.isdigit())
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(temp_dir)

    def test_touch_via_loader(self):
        temp_dir = tempfile.mkdtemp()
        try:
            old_timestamp = 1391804600
            migration_content = (
                """#!/usr/bin/python
# -*- coding: utf-8 -*-

class Migration:
    def __init__(self):
        self.uuid = "test-uuid"
        self.timestamp = %d
        self.description = "test migration"

    def run(self, db):
        pass

migration = Migration()
"""
                % old_timestamp
            )

            old_path = os.path.join(temp_dir, "%d.py" % old_timestamp)
            with open(old_path, "wb") as file:
                file.write(migration_content.encode("utf-8"))

            _loader = migratore.DirectoryLoader(temp_dir)
            _loader.touch(str(old_timestamp))

            self.assertFalse(os.path.exists(old_path))

            files = [file for file in os.listdir(temp_dir) if file.endswith(".py")]
            self.assertEqual(len(files), 1)

            new_filename = files[0]
            new_timestamp = int(new_filename[:-3])
            self.assertGreater(new_timestamp, old_timestamp)

            new_path = os.path.join(temp_dir, new_filename)
            with open(new_path, "rb") as file:
                new_content = file.read().decode("utf-8")

            match = re.search(r"self\.timestamp\s*=\s*(\d+)", new_content)
            self.assertIsNotNone(match)
            self.assertEqual(int(match.group(1)), new_timestamp)
        finally:
            shutil.rmtree(temp_dir)

    def test_touch_migration_not_found(self):
        temp_dir = tempfile.mkdtemp()
        try:
            _loader = migratore.DirectoryLoader(temp_dir)

            with self.assertRaises(RuntimeError) as context:
                _loader.touch("9999999999")

            self.assertIn("not found", str(context.exception))
        finally:
            shutil.rmtree(temp_dir)
