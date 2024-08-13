from fastapi_manager.db import models
from tortoise import fields


class Penises(models.Model):
    penis_name = fields.CharField(max_length=255)
    length = fields.IntField(default=1, null=False)

    def __str__(self):
        return self.penis_name
