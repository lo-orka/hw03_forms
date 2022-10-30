from django.core.paginator import Paginator


def page_limits(posts, page):
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page)
    return page_obj
