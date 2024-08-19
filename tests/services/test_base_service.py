from fastapi_manager.apps import apps

apps.populate(["tests.services.test_app"])

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Request, HTTPException

from apps.registry import Apps
from .test_app.models import TestModel
from fastapi_manager.view.service import (
    BaseService,
    _MODEL,
)


@pytest.fixture(autouse=True)
def mock_apps():
    yield
    Apps._instance = None


@pytest.fixture
def mock_model():
    # Create a mock model class
    return AsyncMock(spec=TestModel)


@pytest.fixture
def base_service(mock_model):
    # Instantiate the service and set the model
    service = BaseService()
    service.model = mock_model
    return service


@pytest.fixture
def mock_request():
    # Create a mock request object
    return AsyncMock(spec=Request)


@pytest.mark.asyncio
async def test_list(base_service, mock_request, mock_model):
    # Arrange
    mock_request.path_params = {}
    mock_model.filter().return_value = []

    service = base_service
    # Act
    result = await service.list(mock_request)

    # Assert
    assert result == []
    mock_model.filter.assert_called_once_with(**mock_request.path_params)


@pytest.mark.asyncio
async def test_retrieve(base_service, mock_request, mock_model):
    # Arrange
    mock_request.path_params = {"id": 1}
    mock_model.filter().limit().first.return_value = {"id": 1, "name": "Test"}

    # Act
    result = await base_service.retrive(mock_request)

    # Assert
    assert result == {"id": 1, "name": "Test"}
    mock_model.filter.assert_called_once_with(**mock_request.path_params)


@pytest.mark.asyncio
async def test_create(base_service, mock_request, mock_model):
    # Arrange
    mock_request.query_params = {"name": "New Item"}
    mock_model.create.return_value = {"id": 1, "name": "New Item"}

    # Act
    result = await base_service.create(mock_request)

    # Assert
    assert result == {"id": 1, "name": "New Item"}
    mock_model.create.assert_called_once_with(**mock_request.query_params)


@pytest.mark.asyncio
async def test_update(base_service, mock_request, mock_model):
    # Arrange
    mock_request.path_params = {"id": 1}
    mock_request.query_params = {"name": "Updated Item"}
    mock_model.filter().limit().first.return_value = mock_model
    mock_model.update_from_dict.return_value = mock_model

    # Act
    result = await base_service.update(mock_request)

    # Assert
    assert result == mock_model
    mock_model.update_from_dict.assert_called_once_with(dict(mock_request.query_params))
    mock_model.save.assert_called_once()


@pytest.mark.asyncio
async def test_delete(base_service, mock_request, mock_model):
    # Arrange
    mock_request.path_params = {"id": 1}
    mock_model.filter().limit().first.return_value = mock_model

    # Act
    result = await base_service.delete(mock_request)

    # Assert
    assert result == mock_model
    mock_model.delete.assert_called_once()


@pytest.mark.asyncio
async def test_update_not_found(base_service, mock_request, mock_model):
    # Arrange
    mock_request.path_params = {"id": 1}
    mock_model.filter().limit().first.return_value = None

    # Act / Assert
    with pytest.raises(HTTPException) as excinfo:
        await base_service.update(mock_request)

    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_not_found(base_service, mock_request, mock_model):
    # Arrange
    mock_request.path_params = {"id": 1}
    mock_model.filter().limit().first.return_value = None

    # Act / Assert
    with pytest.raises(HTTPException) as excinfo:
        await base_service.delete(mock_request)

    assert excinfo.value.status_code == 404
