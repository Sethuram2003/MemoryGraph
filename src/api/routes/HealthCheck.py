from fastapi import FastAPI, APIRouter
from fastapi.responses import JSONResponse

 
health_check_router = APIRouter(tags=["health_check"])

app = FastAPI()

@health_check_router.get("/health")
def health_check():
    return JSONResponse({'message': "Service is up and running"}, status_code=200)

