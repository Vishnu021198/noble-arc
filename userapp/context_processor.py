from .models import Category


def product_links(request):
    links = Category.objects.all()
    return dict(links=links)