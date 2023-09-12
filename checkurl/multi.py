import django
import time
import requests






def scan_DB(url, return_queue):
    django.setup()
    from checkurl.models import url_judge

    malicious = False
    type = "Null"
    for obj in url_judge.objects.all():
        if obj.url == url:
            malicious = obj.prediction_result
            type = obj.pri_url
            break

    ##white list scan 루틴 추가 필요

    result = (malicious, type)
    return_queue.put(result)
    return 0

"""
def AI(url, return_queue):  ##테스트용 AI함수
    time.sleep(5)
    result = (False, "phishing")
    return_queue.put(result)
    return 0
"""



def AI(url, return_queue):
    try:
        data = {"url": url}
        response = requests.post("http://3.34.52.88:8000/predict", json=data) ##유동ip
        response.raise_for_status()  # Raise an exception if the request fails
        result = response.json()
        malicious_result = False
        type_result = result['predict_result']
        if type_result != "benign":
            malicious_result = True
        result = (malicious_result, type_result)
        return_queue.put(result)
        return 0, "Success"
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return 0, "Error",
