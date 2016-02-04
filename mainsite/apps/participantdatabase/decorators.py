from django.contrib import messages
from django.shortcuts import redirect


def permision_required_or_message(perm, redirect_url):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the given url and displaying a message.
    
    """
    def _wrapped_decorator(view):
        def _wraped_view(request):
            if request.user.has_perm(perm):
                return view(request)
            else:
                message = 'You account has not been enabled.'
                message+= ' Please await admin approval.'
                messages.add_message(request, messages.WARNING, message)
                return redirect(redirect_url)
        return _wraped_view
    return _wrapped_decorator
                