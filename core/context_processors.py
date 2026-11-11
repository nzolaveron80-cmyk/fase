from .models import SiteConfig


def site(request):
    return {"site": SiteConfig.load()}
