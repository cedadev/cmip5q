from django.template import Context, loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django import forms
from cmip5q.protoq.models import *
import uuid
from django.conf import settings
logging=settings.LOG

def list(request):
    ''' Returns a list of internal vocabularies '''
    vocabs=Vocab.objects.all()
    for v in vocabs:
        v.url=reverse('cmip5q.protoq.vocab.show',args=(v.id,))
    return render_to_response('vocab.html',{'v':vocabs})

def show (request,vocabID):
    ''' Returns members of a specific vocabulary '''
    vocab=Vocab.objects.get(id=vocabID)
    values=Value.objects.filter(vocab=vocab)
    return render_to_response('vocabvalues.html',{'v':values,'vocab':vocab})


