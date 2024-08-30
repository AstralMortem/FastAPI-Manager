from fastapi_manager.db import models, fields


class TestModelApp1(models.Model):
    name = fields.CharField(max_length=255)
