from django.shortcuts import render


# Create your views here.
def home_page(request):
    return render(
        request=request,
        template_name='lists/home.html',
        context={
            'new_item_text': request.POST.get('item_text'),
        }
    )
