from fastapi import APIRouter

router = APIRouter(prefix="/apps")


@router.get("/")
async def root():
    return {"message": "Hello World"}
