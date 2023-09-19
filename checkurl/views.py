
from django.http import HttpResponse
from django.shortcuts import render
import multiprocessing
import csv
import socket
import requests

from checkurl import multi
from checkurl.models import url_judge
from checkurl.models import URLManager
from checkurl.models import white_list



"""
def make_white_DB():
    num = 1
    with open('top500Domains.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            root_domain = row[1]
            new_white = white_list(num, root_domain)
            new_white.save()
            num += 1

def asdf():
    new1 = URLManager(1, "Benign", "악의적인 목적이나 위협을 갖지 않는 일반적인 웹 페이지 주소입니다.", False)
    new2 = URLManager(2, "Defacement", "웹 사이트나 웹 페이지의 외관을 공격자가 변경하여 피해자나 방문자에게 악의적인 메시지나 그래픽을 노출하는 URL입니다.", True)
    new3 = URLManager(3, "Phishing", "피해자를 속여 개인 정보나 금융 정보를 탈취하려는 악의적인 목적으로 설계된 URL입니다.", True)
    new4 = URLManager(4, "Malware", "악성 코드 또는 악성 소프트웨어를 다운로드하거나 실행하도록 설계된 URL입니다.", True)

    new1.save()
    new2.save()
    new3.save()
    new4.save()
"""

# def index(request):
#     return HttpResponse("안녕하세요  test에 오신것을 환영합니다.")



def checkurl_main(request):
    if request.method == 'POST':
        url_string = request.POST.get('input_string', '')
        if url_string:
            context = information(url_string)
            return render(request, 'checkurl/output.html', context)

    return render(request, 'checkurl/input.html')


def information(input_string):
    AI_output, url_type = multi_processing(input_string)
    ip, country = get_ip(input_string)
    type_explanation = url_manager_view(url_type)
    if AI_output == True:
        AI_output = "피싱"
    else:
        AI_output = "정상"
    insert_db(AI_output, url_type, input_string, ip, country)

    context = {'url': input_string, 'AI_output': AI_output, 'url_type': url_type, 'type_explanation': type_explanation, 'ip': ip, 'country': country}
    ## url : 클라이언트가 입력한 url(str), AI_output : 악성여부(bool), url_type : AI가 판단한 해당 url의 타입(str), type_explanation : 해당 type에 대한 설명(str), ip(str), country : 국가명(str)
    return context



def multi_processing(input_string):

    print("multi_process in!")
    return_queue_ai = multiprocessing.JoinableQueue()
    return_queue_db = multiprocessing.JoinableQueue()

    AI_process = multiprocessing.Process(target=multi.AI, args=(input_string, return_queue_ai))
    DB_process = multiprocessing.Process(target=multi.scan_DB, args=(input_string, return_queue_db))
    
    # DB_process와 AI_process를 시작합니다.
    DB_process.start()
    AI_process.start()

    # DB_process와 AI_process가 완료될 때까지 대기합니다.
    DB_process.join()
    AI_process.join()

    # 결과를 가져옵니다.
    result_DB = return_queue_db.get()
    result_AI = return_queue_ai.get()
    
    # 반환된 값이 None인 경우를 처리합니다.
    if result_DB is None:
        result_DB = (False, "Null")
    if result_AI is None:
        result_AI = (False, "Null")

    print(result_DB, result_AI)
    
    if result_DB[1] != "benign": ##db에 해당 url 정보가 존재한다면
        return result_AI[0], result_AI[1]
    else:
        return result_DB[0], result_DB[1]



def insert_db(AI_output, url_type, input_string, ip, country):
    try:
        new_test_entry = url_judge(AI_output, url_type, input_string, ip, country)
        new_test_entry.save()
        print("데이터가 저장되었습니다.")
    except Exception as e:
        print(f"Database Exception: {e}")






def get_ip(input_string):
    def get_ip_address(domain):
        try:
            ip_address = socket.gethostbyname(domain)
            return ip_address
        except socket.gaierror as e:
            print(f"An error occurred while resolving the host: {e}")
            return None

    def get_country(ip_address):
        try:
            url = f"https://ipapi.co/{ip_address}/country_name/"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return response.text.strip()  # Remove leading/trailing whitespace
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching country information: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    domain = input_string

    ip_address = get_ip_address(domain)
    if ip_address is None:
        return None, None  # IP 주소를 가져올 수 없는 경우 None 반환

    country = get_country(ip_address)
    if country is None:
        return ip_address, None  # 국가 정보를 가져올 수 없는 경우 IP 주소만 반환

    return ip_address, country





def url_manager_view(type):
    type_upper = type.capitalize()
    url_manager_data = URLManager.objects.filter(url_type=type_upper)
    type_explanation = ""
    if url_manager_data:
        type_explanation = url_manager_data[0].type_explanation

    return type_explanation






