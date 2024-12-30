from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes.api import api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods="*",
    allow_headers=["*"],
)

app.include_router(router=api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Chat API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
