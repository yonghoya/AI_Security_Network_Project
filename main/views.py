from django.shortcuts import render, redirect
# branch test 
def index(request):
    keyword = request.GET.get('keyword')

    if keyword:
        return redirect('output', keyword=keyword)
    else:
        return render(request, 'main/input.html')

def output(request, keyword):
    if request.method == 'POST':
        return redirect('index')

    context = {'keyword': keyword}
    return render(request, 'main/output.html', context)