from django.shortcuts import render, redirect

def index(request):
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        if keyword:
            return redirect('output', keyword=keyword)
    return render(request, 'main/input.html')
    
def output(request, keyword):
    if request.method == 'POST':
        return redirect('index')

    context = {'keyword': keyword}
    return render(request, 'main/output.html', context)
