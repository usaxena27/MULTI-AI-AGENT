import subprocess
import threading
import time
from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException             

logger=get_logger(__name__)

load_dotenv()

def run_backend():
    try:
        logger.info("Starting backend service..")
        subprocess.run(["uvicorn", "app.backend.api:app", "--host", "127.0.0.1", "--port", "9999"], check=True)
    except CustomException as e:
        logger.error(f"Error occurred while starting backend service")
        raise CustomException("Failed to start backend server", e)
    
def run_frontend():
    try:
        logger.info("Starting frontend service..")
        subprocess.run(["streamlit", "run", "app/frontend/ui.py"], check=True)
    except CustomException as e:
        logger.error(f"Error occurred while starting frontend service")
        raise CustomException("Failed to start frontend server", e)

if __name__=="__main__":
    try:
        threading.Thread(target=run_backend).start()
        time.sleep(2)
        run_frontend()

    except CustomException as e:
        logger.exception(f"CustomException occurred : {str(e)}")
        