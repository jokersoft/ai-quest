from fastapi import FastAPI
from mangum import Mangum
from app.api.action import router as ActionRouter

app = FastAPI()

app.include_router(ActionRouter)

handler = Mangum(app)
