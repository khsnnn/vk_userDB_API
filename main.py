import logging
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import DBHandler
from routes import register_routes

load_dotenv()

logging.basicConfig(level='INFO', format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

# Настройка CORS
allowed_origins = ["http://localhost:5173"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация базы данных
db_handler = DBHandler(
    connection_uri=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USER"),
    pwd=os.getenv("NEO4J_PASSWORD")
)

# Регистрация маршрутов
register_routes(app, db_handler)

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST"), port=int(os.getenv("PORT")))
