"""Poetry plugin use to tweak the dependencies of the project."""

import re
from typing import Any, Optional

import cleo.commands.command
import cleo.events.console_events
import cleo.io.io
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.event import Event
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.core.constraints.version import (
    Version,
    VersionConstraint,
    VersionRange,
    VersionRangeConstraint,
    parse_constraint,
)
from poetry.core.version.pep440 import Release
from poetry.plugins.application_plugin import ApplicationPlugin

_VERSION_RE = re.compile(r"^([1-9])+(\.([1-9])+(\.([1-9])+)?)?(.*)$")


class Plugin(ApplicationPlugin):
    """Poetry plugin use to tweak the dependencies of the project."""

    _application: Application
    _pyproject: dict[str, Any]
    _state: str

    def activate(self, application: Application) -> None:
        """Activate the plugin."""
        self._application = application
        self._pyproject = self._application.poetry.pyproject.data
        self._state = ""

        event_dispatcher = application.event_dispatcher
        assert event_dispatcher is not None
        event_dispatcher.add_listener(cleo.events.console_events.COMMAND, self._apply_version)
        event_dispatcher.add_listener(cleo.events.console_events.SIGNAL, self._revert_version)
        event_dispatcher.add_listener(cleo.events.console_events.TERMINATE, self._revert_version)
        event_dispatcher.add_listener(cleo.events.console_events.ERROR, self._revert_version)

    def _revert_version(self, event: Event, kind: str, dispatcher: EventDispatcher):
        del event, kind, dispatcher

        if self._state:
            self._application.poetry.package.python_versions = self._state

    def _zero(self, version_pice: Optional[int]):
        return None if version_pice is None else 0

    def _min(self, constraint, release_new):
        return Version.parse(release_new.text) if (release_new < constraint.min.release) else constraint.min

    def _apply_version(self, event: Event, kind: str, dispatcher: EventDispatcher):
        del kind, dispatcher
        assert isinstance(event, ConsoleCommandEvent)

        if event.command.name not in ("build",):
            return

        constraint = parse_constraint(self._application.poetry.package.python_versions)
        assert isinstance(constraint, VersionRangeConstraint)
        self._state = self._application.poetry.package.python_versions

        operator = ">=" if constraint.include_min else ">"
        self._application.poetry.package.python_versions = f"{operator}{constraint.min}"
