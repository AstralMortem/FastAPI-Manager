from collections import defaultdict

from fastapi import Request, HTTPException, Depends
from fastapi_manager.db.models import Model
from typing import TypeVar, Generic, Annotated
from fastapi_manager.router import BaseRouter
from fastapi_class import View

_MODEL = TypeVar("_MODEL", bound=Model)


class BaseService(Generic[_MODEL]):
    model: type[_MODEL]

    async def list(self, *args, **kwargs):
        obj = await self.model.filter(*args, **kwargs)
        return obj

    async def retrive(self, *args, **kwargs):
        obj = await self.model.filter(*args, **kwargs).limit(1).first()
        return obj

    async def create(self, *args, **kwargs):
        obj = await self.model.create(*args, **kwargs)
        return obj

    async def update(self, *args, **kwargs):
        obj = await self.retrive(*args, **kwargs)
        if obj is not None:
            obj = obj.update_from_dict(*args, **kwargs)
            await obj.save()
            return obj
        raise HTTPException(status_code=404, detail="Not found")

    async def delete(self, *args, **kwargs):
        obj = await self.retrive(*args, **kwargs)
        if obj is not None:
            return await obj.delete()
        raise HTTPException(status_code=404, detail="Not found")
