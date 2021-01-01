from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from public_chat.models import PublicChatRoom


def home_screen_view(request, *args, **kwargs):
    context = {

    }
    return render(request, 'home.html', context)

def community_view(request): 
	context = {}
	context['debug_mode'] = settings.DEBUG
	context['room'] = 1
	return render(request, 'grouphome.html', context)

	

	