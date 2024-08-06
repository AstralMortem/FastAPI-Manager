from typing import Any
from fastapi import HTTPException, status


#
# DB Exception
#


class RecordDoesNotExist(HTTPException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, msg="Item does not exists"):
        self.detail = {"message": msg}


#
# Core Exception
#
