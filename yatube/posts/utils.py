from django.core.paginator import Paginator


def paginate_page(request, post_list, post_per_page=10):
    paginator = Paginator(post_list, post_per_page)
    page_obj = paginator.get_page(request.GET.get('page'))
    return page_obj
