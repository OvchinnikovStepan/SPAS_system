from fastapi import FastAPI
from app.src.middleware import add_middlewares
from app.src.api.detectors_router import router as detectors_router


app = FastAPI(title="SPAS analyzer")

add_middlewares(app)

app.include_router(router=detectors_router, prefix="/api")


@app.get("/")
async def root():
   return {"message": "SPAS timeseries analyzer"}
