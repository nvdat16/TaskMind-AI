from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scheduler_service import SchedulerService


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    monkeypatch.setattr(SchedulerService, "start", staticmethod(lambda: None))
    monkeypatch.setattr(SchedulerService, "shutdown", staticmethod(lambda: None))

    with TestClient(app) as test_client:
        yield test_client
