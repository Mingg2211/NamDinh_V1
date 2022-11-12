from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.api.utils import ranking_result
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    value: str

@app.post("/ranking-utter")
def ranking_utter(item: Item):
    result = ranking_result(item.value.lower().replace('thủ tục',''))
    return {"ranked_uter": result}
