
from django.http import HttpResponse
from django.shortcuts import render
import socket
import requests
import multiprocessing

from checkurl import multi
from checkurl.models import url_judge
from checkurl.models import URLManager




def index(request):
    return HttpResponse("안녕하세요  test에 오신것을 환영합니다.")



def checkurl_main(request):
    if request.method == 'POST':
        url_string = request.POST.get('input_string', '')
        if url_string:
            context = information(url_string)
            return render(request, 'checkurl/output.html', context)

    return render(request, 'checkurl/input.html')


def information(input_string):
    AI_output, url_type = multi_processing(input_string)
    print(AI_output)
    print(url_type)
    ip, country = get_ip(input_string)
    type_explanation = url_manager_view(url_type)
    insert_db(AI_output, url_type, input_string, ip, country)

    context = {'url': input_string, 'AI_output': AI_output, 'url_type': url_type, 'type_explanation': type_explanation, 'ip': ip, 'country': country}
    ## url : 클라이언트가 입력한 url(str), AI_output : 악성여부(bool), url_type : AI가 판단한 해당 url의 타입(str), type_explanation : 해당 type에 대한 설명(str), ip(str), country : 국가명(str)
    return context




def multi_processing(input_string):

    print("multi_process in!")
    return_queue = multiprocessing.JoinableQueue()
    AI_process = multiprocessing.Process(target=multi.AI, args=(input_string, return_queue))
    DB_process = multiprocessing.Process(target=multi.scan_DB, args=(input_string, return_queue))
    AI_process.start()
    DB_process.start()


    DB_process.join()
    result_DB = return_queue.get()
    if result_DB[1] != "Null": ##db에 해당 url 정보가 존재한다면
        return result_DB[0], result_DB[1]


    AI_process.join()
    result_AI = return_queue.get()
    print("multi_process finished!")
    return result_AI[0], result_AI[1]









def insert_db(AI_output, url_type, input_string, ip, country):
    try:
        new_test_entry = url_judge(AI_output, url_type, input_string, ip, country)
        new_test_entry.save()
        print("데이터가 저장되었습니다.")
    except Exception as e:
        print(f"Database Exception: {e}")





def get_ip(input_string):
    def get_ip_address(domain):
        ip_address = socket.gethostbyname(domain)
        return ip_address

    def get_country(ip_address):
        url = f"https://ipapi.co/{ip_address}/country_name/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            return response.text.strip()  # Remove leading/trailing whitespace
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    domain = input_string

    try:
        ip_address = get_ip_address(domain)
        country = get_country(ip_address)
    except socket.gaierror as e:
        print(f"An error occurred: {e}")
        return None

    return ip_address, country




def url_manager_view(type):
    type_upper = type.capitalize()
    url_manager_data = URLManager.objects.filter(url_type=type_upper)
    type_explanation = ""
    if url_manager_data:
        type_explanation = url_manager_data[0].type_explanation

    return type_explanation





