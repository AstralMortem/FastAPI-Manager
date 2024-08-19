from collections import defaultdict

from .base import View
from fastapi_class.routers import Method
from fastapi_manager.router import BaseRouter
from .service import _MODEL, BaseService
from typing import Generic
from fastapi import Request


def autofill_models(model):
    return {
        method: model
        for method in [name.lower() for name in dir(Method) if not name.startswith("_")]
    }


class BaseViewSet(View, Generic[_MODEL]):
    model: type[_MODEL]
    service = type[BaseService[_MODEL]] = BaseService[_MODEL]()
    RESPONSE_MODELS = autofill_models(_MODEL)
    INPUT_MODELS = autofill_models(_MODEL)

    def __init__(self, router=BaseRouter()):
        self.router = router
        super().__init__(router=router)

    def get(self, request: Request):
        input_model = self.INPUT_MODELS[request.method].model_validate(
            **request.query_params
        )
        obj = self.service.retrive(input_model.model_dump())
        self.RESPONSE_MODELS[request.method].model_validate(obj)
