import django
import requests


def scan_DB(url, return_queue):
    django.setup()
    from checkurl.models import url_judge
    from checkurl.models import white_list

    malicious = False
    ai_type = '' 

    ##white list scan
    for white_obj in white_list.objects.all():
        if white_obj.url == url or white_obj.url == url.lstrip("www."):
            malicious = False
            ai_type = "benign"
            result = (malicious,type)
            return_queue.put(result)
            #break
            return

    ## 검색기록 scan
    for obj in url_judge.objects.all():
        if obj.url == url or obj.url == url.lstrip("www."):
            malicious = obj.prediction_result
            type = obj.pri_url
            result = (malicious,type)
            return_queue.put(result)
            #break
            return

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
        response = requests.post("http://3.34.97.158:8000/predict", json=data) ##유동ip
        response.raise_for_status()  # Raise an exception if the request fails
        result = response.json()
        malicious_result = False
        type_result = result['predict_result']
        if type_result != "benign":
            malicious_result = True
        result = (malicious_result, type_result)
        return_queue.put(result)
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return 0
