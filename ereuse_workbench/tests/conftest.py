import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List
from unittest import mock
from unittest.mock import MagicMock

import pytest
from ereuse_utils import DeviceHubJSONEncoder

from ereuse_workbench.computer import Computer


def fixture(file_name: str):
    with Path(__file__).parent.joinpath('fixtures').joinpath(file_name).open() as file:
        return file.read()


def jsonf(file_name: str) -> dict:
    """Gets a json fixture and parses it to a dict."""
    with Path(__file__).parent.joinpath('fixtures').joinpath(file_name + '.json').open() as file:
        return json.load(file)


@pytest.fixture()
def lshw() -> MagicMock:
    """
    Mocks the call to LSHW from Computer.

    Set ``mocked.return_value.json`` with a JSON string, where
    ``mocked`` is the injected parameter you receive in your test.
    """

    class LSHW:
        def __init__(self) -> None:
            self.json = ''
            super().__init__()

        def communicate(self):
            return self.json, None

    with mock.patch('ereuse_workbench.computer.Popen') as Popen:
        Popen.return_value = LSHW()
        yield Popen


def computer(lshw: MagicMock, json_name: str) -> (dict, Dict[str, List[dict]]):
    """Given a LSHW output and a LSHW mock, runs Computer."""
    lshw.return_value.json = fixture(json_name + '.json')
    computer_getter = Computer()
    assert lshw.called
    pc, components = computer_getter.run()
    components = json.dumps(components, skipkeys=True, cls=DeviceHubJSONEncoder, indent=2)
    # Group components in a dictionary by their @type
    grouped = defaultdict(list)
    for component in json.loads(components):
        grouped[component['@type']].append(component)
    return pc, grouped


@pytest.fixture()
def subprocess_os_installer() -> MagicMock:
    with mock.patch('ereuse_workbench.os_installer.subprocess') as subprocess:
        subprocess.run = MagicMock()
        yield subprocess
