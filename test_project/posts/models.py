from fastapi_manager.db import models
from tortoise import fields


class Post(models.Model):
    id = fields.UUIDField(primary_key=True)
    title = fields.CharField(max_length=255)

    def __str__(self):
        return self.title
