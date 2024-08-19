from fastapi_manager.db import models, fields


class TestModelApp2(models.Model):
    name = fields.CharField(max_length=255)
    age = fields.IntField()
