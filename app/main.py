from fastapi import FastAPI
from app.services.load import set_model
from app.core.middleware import Middleware
from app.api.routes import router
from app.core.exception_handler import register_exception

app = FastAPI(title="MlOps app")

@app.on_event('startup')
async def start():
    set_model()

app.add_middleware(Middleware)

app.include_router(router=router)

register_exception(app=app)
