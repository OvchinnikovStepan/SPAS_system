from fastapi import FastAPI
from app.src.middleware import add_middlewares


app = FastAPI()
add_middlewares(app)


@app.get("/")
async def home():
   return {"data": "Hello World"}
