import os

from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI

from dao.connection_manager import ConnectionManager
from routers import pokemon_router, attack_router

# Import all conf variable from .env
load_dotenv()

# Create the db connection
ConnectionManager(os.getenv("HOST")
                  , os.getenv("PORT")
                  , os.getenv("DATABASE")
                  , os.getenv("USER")
                  , os.getenv("PASSWORD"))

app = FastAPI()

app.include_router(pokemon_router.router)
app.include_router(attack_router.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)