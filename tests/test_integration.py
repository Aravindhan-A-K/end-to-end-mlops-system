import requests
import time



def test_mlflow():
    assert wait_for_api("http://mlflow:5000")
    response = requests.get("http://mlflow:5000")
    assert response.status_code == 200

def test_app():
    assert wait_for_api("http://app:8000")
    response = requests.get("http://app:8000")
    assert response.status_code == 200


def wait_for_api(url, timeout=60):
    for _ in range(timeout):
        try:
            if requests.get(url=url).status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False
