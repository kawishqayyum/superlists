from django.shortcuts import render, redirect
from lists.models import Item


# Create your views here.
def home_page(request):

    if request.method == 'POST':
        Item.objects.create(text=request.POST.get('item_text'))
        return redirect('/')

    items = Item.objects.all()
    return render(
        request=request,
        template_name='lists/home.html',
        context={'items': items}
    )
