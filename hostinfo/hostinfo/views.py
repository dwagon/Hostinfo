from django.http import JsonResponse
from django.conf import settings


def version(request):
    ans = {"version": settings.VERSION}
    return JsonResponse(ans)


# EOF
