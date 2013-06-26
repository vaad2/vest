from django.http import HttpResponse



def json_handler_decorator_dispatch(**dkwargs):
    def param_decorator(fun):
        def decorator_fun(self, request, *args, **kwargs):
            if 'pre_init' in dkwargs:
                dkwargs['pre_init'](self, request, *args, **kwargs)
            if 'cmd' in request.REQUEST:
                if 'callback' in dkwargs:
                    result = dkwargs['callback'](self, request, *args, **kwargs)
                    if isinstance(result, HttpResponse):
                        return result

                try:
                    handler = getattr(self, 'cmd_%s' % request.REQUEST['cmd'].lower())
                    result = handler(request, *args, **kwargs)
                    if 'post_process' in dkwargs:
                        result = dkwargs['post_process'](self, result, request, *args, **kwargs)

                    return result
                except Exception, exception:
                    raise Exception(exception)
            else:
                return fun(self, request, *args, **kwargs)

        return decorator_fun
    return param_decorator