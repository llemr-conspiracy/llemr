from .models import PageviewRecord


class AuditMiddleware(object):

    def process_response(self, request, response):
        print(dir(request))
        print(dir(response))

        info = {}

        info['user'] = request.user.username
        info['role'] = request.session.get('clintype_pk', 'no role')

        for verb in ['GET', 'POST', ]:
            if getattr(request, verb):
                assert 'verb' not in info, info['verb']
                info['verb'] = verb

        info['url'] = request.get_full_path()
        info['referrer'] = request.META.get('HTTP_REFERER', '')

        info['status_code'] = response.status_code

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        info['user-ip'] = ip

        PageviewRecord.objects.create(
            user=request.user,
            role=request.session.get('clintype_pk', None),
            user_ip=info['user-ip'],
            request_verb=info['verb'],
            url=request.get_full_path(),
            referrer=request.META.get('HTTP_REFERER', None),
            status_code=response.status_code
        )

        return response
