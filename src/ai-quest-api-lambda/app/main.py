from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.api.api_v1.api import router as api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # warning!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "root"}

app.include_router(api_router, prefix="/api/v1")

for route in app.routes:
    methods = ",".join(route.methods)
    print(f"Path: {route.path}, Method: {methods}")

# for AWS Lambda compatibility:
handler = Mangum(app)
