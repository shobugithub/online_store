from django.utils import timezone

class LoggIPWriterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        now = timezone.now()

        ip = request.META.get('HTTP_USER_AGENT', 'ip addres nomalum')

        print(f'{[now]} ip address {ip}')

        return self.get_response(request)
