from fastapi import APIRouter, BackgroundTasks, Depends, Request
from app.api.schemas import RequestModel, ResponseModel
from app.services.prediction_service import predict_service
from app.services.load import get_model

router = APIRouter()

@router.get('/')
async def health_check():
    return {"Status": 'Ok'}

@router.post('/predict', response_model=ResponseModel)
def predict(request: Request, data: RequestModel, background_tasks: BackgroundTasks, model=Depends(get_model)):
    return predict_service(request, data, background_tasks, model)