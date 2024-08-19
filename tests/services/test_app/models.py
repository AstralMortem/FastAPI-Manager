from fastapi_manager.db import models, fields


class TestModel(models.Model):
    name = fields.CharField(max_length=255)
