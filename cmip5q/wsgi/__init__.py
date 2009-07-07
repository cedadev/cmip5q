
import django.core.handlers.wsgi

def app_factory(globalConfig, **localConfig):
    '''Paste app factory for Django WSGI handler'''
    return django.core.handlers.wsgi.WSGIHandler()