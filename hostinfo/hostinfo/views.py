from django.conf import settings
from django.http import JsonResponse


def version(request):
    ans = {"version": settings.VERSION}
    return JsonResponse(ans)


# EOF
