#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import uuid
import time
import datetime
import traceback

from . import base
from . import loader


class Migration(base.Console):

    SQUASHABLE_METHODS = ["run", "run_partial", "run_skip", "cleanup", "rollback"]
    """ Methods that can be squashed into a single migration """

    def __init__(self, uuid=None, timestamp=None, description=None):
        self.uuid = uuid
        self.timestamp = timestamp
        self.description = description

    def __cmp__(self, value):
        return self.timestamp.__cmp__(value.timestamp)

    def __lt__(self, value):
        return self.timestamp < value.timestamp

    def __gt__(self, value):
        return self.timestamp > value.timestamp

    def __eq__(self, value):
        return self.timestamp == value.timestamp

    def __le__(self, value):
        return self.timestamp <= value.timestamp

    def __ge__(self, value):
        return self.timestamp >= value.timestamp

    def __ne__(self, value):
        return self.timestamp != value.timestamp

    def __repr__(self):
        return "<Migration %s %s %s>" % (self.uuid, self.timestamp, self.description)

    @classmethod
    def environ(cls):
        args = list()
        kwargs = dict()
        base.Migratore._environ(args, kwargs)
        base.Migratore.echo_map(kwargs)

    @classmethod
    def list(cls):
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            executions = table.select(
                order_by=(("object_id", "asc"),), result="success"
            )

            is_first = True
            for execution in executions:
                if is_first:
                    is_first = False
                else:
                    base.Migratore.echo("")
                cls._execution(execution, is_first=is_first)

        finally:
            db.close()

    @classmethod
    def errors(cls):
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            executions = table.select(order_by=(("object_id", "asc"),), result="error")

            is_first = True
            for execution in executions:
                if is_first:
                    is_first = False
                else:
                    base.Migratore.echo("")
                cls._execution(execution, is_first=is_first)
                cls._error(execution, is_first=is_first)

        finally:
            db.close()

    @classmethod
    def mark(cls, *args, **kwargs):
        db = base.Migratore.get_db(*args, **kwargs)
        timestamp = db.timestamp()
        timestamp = timestamp or 0
        migration = MarkMigration()
        migration.start()

    @classmethod
    def trace(cls, id):
        object_id = int(id)
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            execution = table.get(object_id=object_id)
            traceback = execution["traceback"]
            base.Migratore.echo(traceback)
        finally:
            db.close()

    @classmethod
    def rebuild(cls, id, *args, **kwargs):
        path = "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.rebuild(id, *args, **kwargs)

    @classmethod
    def touch(cls, id, *args, **kwargs):
        path = "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.touch(id, *args, **kwargs)

    @classmethod
    def squash(cls, start, end, output=None, path=None):
        path = path or "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.squash(start, end, output=output)

    @classmethod
    def upgrade(cls, path=None, *args, **kwargs):
        path = path or "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.upgrade(*args, **kwargs)

    @classmethod
    def dry_upgrade(cls, path=None, *args, **kwargs):
        path = path or "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.dry_upgrade(*args, **kwargs)

    @classmethod
    def skip(cls, path=None, *args, **kwargs):
        path = path or "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.skip(*args, **kwargs)

    @classmethod
    def generate(cls, path=None):
        _uuid = uuid.uuid4()
        _uuid = str(_uuid)
        timestamp = time.time()
        timestamp = int(timestamp)
        description = "migration %s" % _uuid
        args = (_uuid, timestamp, description)
        path = path or str(timestamp) + ".py"

        file_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_path)
        templates_path = os.path.join(dir_path, "templates")
        template_path = os.path.join(templates_path, "migration.py.tpl")

        base.Migratore.echo("Generating migration '%s'..." % _uuid)
        data = cls.template(template_path, *args)
        file = open(path, "wb")
        try:
            file.write(data)
        finally:
            file.close()
        base.Migratore.echo("Migration file '%s' generated" % path)

    @classmethod
    def touch_file(cls, path):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise RuntimeError("Migration file '%s' does not exist" % path)

        new_timestamp = int(time.time())

        with open(path, "rb") as file:
            contents = file.read()
        contents_str = contents.decode("utf-8")

        pattern = r"(self\.timestamp\s*=\s*)\d+"
        if not re.search(pattern, contents_str):
            raise RuntimeError(
                "Could not find 'self.timestamp = ...' in migration file"
            )
        new_contents_str = re.sub(pattern, r"\g<1>%d" % new_timestamp, contents_str)

        with open(path, "wb") as file:
            file.write(new_contents_str.encode("utf-8"))

        dir_path = os.path.dirname(path)
        new_filename = "%d.py" % new_timestamp
        new_path = os.path.join(dir_path, new_filename)

        os.rename(path, new_path)

        base.Migratore.echo("Migration touched: '%s' -> '%s'" % (path, new_path))

    @classmethod
    def squash_files(cls, migrations, migrations_path, output=None):
        if not migrations:
            raise RuntimeError("No migrations found in the specified range")

        _uuid = uuid.uuid4()
        _uuid = str(_uuid)
        timestamp = time.time()
        timestamp = int(timestamp)

        descriptions = [
            migration.description for migration in migrations if migration.description
        ]
        description = "squashed migration: " + "; ".join(descriptions)
        if len(description) > 200:
            description = description[:197] + "..."

        method_bodies = dict()
        for method_name in cls.SQUASHABLE_METHODS:
            method_bodies[method_name] = []

        for migration in migrations:
            migration_path = migrations_path.get(migration.uuid)
            if not migration_path:
                migration_path = migrations_path.get(str(migration.timestamp))
            if migration_path:
                for method_name in cls.SQUASHABLE_METHODS:
                    result = cls._extract_method_body(migration_path, method_name)
                    if not result:
                        continue
                    body, start_line, end_line = result
                    method_bodies[method_name].append(
                        (
                            migration.uuid,
                            migration.timestamp,
                            method_name,
                            start_line,
                            end_line,
                            body,
                        )
                    )

        output = output or str(timestamp) + ".py"
        squashed_content = cls._generate_squashed_migration(
            _uuid, timestamp, description, method_bodies
        )

        file = open(output, "wb")
        try:
            file.write(squashed_content.encode("utf-8"))
        finally:
            file.close()

        base.Migratore.echo("Squashed migration file '%s' generated" % output)
        base.Migratore.echo("Squashed migrations:")
        for migration in migrations:
            base.Migratore.echo("  - %s (%s)" % (migration.uuid, migration.timestamp))

        squashed_methods = [
            method for method in cls.SQUASHABLE_METHODS if method_bodies[method]
        ]
        if squashed_methods:
            base.Migratore.echo("Squashed methods: %s" % ", ".join(squashed_methods))

    @classmethod
    def template(cls, path, *args, **kwargs):
        encoding = kwargs.get("encoding", "utf-8")

        file = open(path, "rb")
        try:
            contents = file.read()
        finally:
            file.close()

        contents = contents.decode(encoding)
        result = contents % args
        return result.encode(encoding)

    @classmethod
    def _time_s(cls, timestamp):
        date_time = datetime.datetime.utcfromtimestamp(timestamp)
        return date_time.strftime("%d %b %Y %H:%M:%S")

    @classmethod
    def _execution(cls, execution, is_first=True):
        object_id = execution["object_id"]
        _uuid = execution["uuid"]
        timestamp = execution["timestamp"]
        description = execution["description"]
        operation = execution["operation"]
        operator = execution["operator"]
        duration = execution["duration"]
        start_s = execution["start_s"]
        end_s = execution["end_s"]
        timestamp_s = cls._time_s(timestamp)

        duration_l = "second" if duration == 1 else "seconds"

        base.Migratore.echo("ID          : %s" % object_id)
        base.Migratore.echo("UUID        : %s" % _uuid)
        base.Migratore.echo("Timestamp   : %d (%s)" % (timestamp, timestamp_s))
        base.Migratore.echo("Description : %s" % description)
        base.Migratore.echo("Operation   : %s" % operation)
        base.Migratore.echo("Operator    : %s" % operator)
        base.Migratore.echo("Duration    : %d %s" % (duration, duration_l))
        base.Migratore.echo("Start time  : %s" % start_s)
        base.Migratore.echo("End time    : %s" % end_s)

    @classmethod
    def _error(cls, execution, is_first=True):
        error = execution["error"]

        base.Migratore.echo("Error       :  %s" % error)

    def start(self, operation="run", operator="Administrator"):
        db = base.Migratore.get_db()
        try:
            return self._start(db, operation, operator)
        finally:
            db.close()

    def run(self, db):
        self.echo("Running migration '%s'" % self.uuid)
        if self.description:
            self.echo("%s" % self.description)

    def run_partial(self, db):
        self.echo("Running partial '%s'" % self.uuid)
        if self.description:
            self.echo("%s" % self.description)

    def run_skip(self, db):
        self.echo("Skipping migration '%s'" % self.uuid)
        if self.description:
            self.echo("%s" % self.description)

    def cleanup(self, db):
        self.echo("Cleaning up...")

    def rollback(self, db):
        self.echo("Rolling back operation...")
        db.rollback()

    def _start(self, db, operation, operator):
        cls = self.__class__

        result = "success"
        error = None
        lines_s = None
        start = time.time()

        method = getattr(self, operation)
        try:
            method(db)
        except Exception as exception:
            if db.safe:
                db.rollback()
            else:
                self.rollback(db)
            lines = traceback.format_exc().splitlines()
            lines_s = "\n".join(lines)
            result = "error"
            error = str(exception)
            for line in lines:
                self.echo(line)
        else:
            db.commit()
        finally:
            self.cleanup(db)

        operation_s = operation.title().replace("_", " ")

        end = time.time()
        start = int(start)
        end = int(end)
        duration = end - start

        start_s = cls._time_s(start)
        end_s = cls._time_s(end)

        table = db.get_table("migratore")
        table.insert(
            uuid=self.uuid,
            timestamp=self.timestamp,
            description=self.description,
            result=result,
            error=error,
            traceback=lines_s,
            operation=operation_s,
            operator=operator,
            start=start,
            end=end,
            duration=duration,
            start_s=start_s,
            end_s=end_s,
        )
        db.commit()

        return result

    @classmethod
    def _extract_method_body(cls, file_path, method_name, encoding="utf-8"):
        with open(file_path, "rb") as file:
            contents = file.read()
        contents = contents.decode(encoding)

        pattern = r"def %s\s*\(\s*self\s*,\s*db\s*\)\s*:" % re.escape(method_name)
        match = re.search(pattern, contents)
        if not match:
            return None

        method_start_line = contents[: match.start()].count("\n") + 1

        after_method = contents[match.end() :]
        lines = after_method.split("\n")

        body_lines = []
        base_indent = None
        line_indices = []
        current_line_num = method_start_line

        for line in lines:
            current_line_num += 1

            if not line.strip() and base_indent == None:
                continue

            if base_indent == None and line.strip():
                stripped = line.lstrip()
                base_indent = len(line) - len(stripped)

            if line.strip():
                current_indent = len(line) - len(line.lstrip())
                if current_indent < base_indent:
                    break
                if line.strip().startswith("def ") or line.strip().startswith("class "):
                    break

            parent_call_patterns = [
                "Migration.%s(self, db)" % method_name,
                "migratore.Migration.%s(self, db)" % method_name,
            ]
            if any(pattern in line for pattern in parent_call_patterns):
                continue

            body_lines.append(line)
            line_indices.append(current_line_num)

        while body_lines and not body_lines[-1].strip():
            body_lines.pop()
            line_indices.pop()

        if not body_lines:
            return None

        start_line = line_indices[0] if line_indices else 0
        end_line = line_indices[-1] if line_indices else 0

        return ("\n".join(body_lines), start_line, end_line)

    @classmethod
    def _generate_squashed_migration(cls, _uuid, timestamp, description, method_bodies):
        description = description.replace('"', '\\"')

        lines = [
            "#!/usr/bin/python",
            "# -*- coding: utf-8 -*-",
            "",
            "import migratore",
            "",
            "",
            "class Migration(migratore.Migration):",
            "",
            "    def __init__(self):",
            "        migratore.Migration.__init__(self)",
            '        self.uuid = "%s"' % _uuid,
            "        self.timestamp = %d" % timestamp,
            '        self.description = "%s"' % description,
        ]

        for method_name in cls.SQUASHABLE_METHODS:
            bodies = method_bodies.get(method_name, [])

            if not bodies and method_name != "run":
                continue

            lines.append("")
            lines.append("    def %s(self, db):" % method_name)
            lines.append("        migratore.Migration.%s(self, db)" % method_name)

            if bodies:
                for (
                    migration_uuid,
                    timestamp,
                    orig_method,
                    start_line,
                    end_line,
                    body,
                ) in bodies:
                    lines.append("")
                    lines.append(
                        "        # -*- Migration %s (timestamp: %d) [%s():%d-%d] -*-"
                        % (migration_uuid, timestamp, orig_method, start_line, end_line)
                    )
                    lines.append(body)
            else:
                lines.append("")

        lines.append("")
        lines.append("migration = Migration()")
        lines.append("")

        return "\n".join(lines)


class MarkMigration(Migration):
    def __init__(self):
        Migration.__init__(self)
        self.uuid = "da023aab-736d-40a6-8e9b-c6175c1241f5"
        self.timestamp = int(time.time())
        self.description = "marks the initial stage of the data source"

    def start(cls, *args, **kwargs):
        db = base.Migratore.get_db()
        table = db.get_table("migratore")
        count = table.count(result="success")
        if count > 0:
            return
        return Migration.start(cls, *args, **kwargs)
