from django.shortcuts import render, redirect

def index(request):
    keyword = request.GET.get('keyword')

    if keyword:
        return redirect('output', keyword=keyword)
    else:
        return render(request, 'main/input.html')

def output(request, keyword):
    context = {'keyword': keyword}
    return render(request, 'main/output.html', context)