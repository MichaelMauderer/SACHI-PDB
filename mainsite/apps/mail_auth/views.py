from django.shortcuts import render, get_object_or_404


def activate_view(request, token):
    import models
    user_auth_token = get_object_or_404(models.UserAuthToken, activate_token=token)
    user_auth_token.user.is_active = True
    user_auth_token.user.save()
    return render(request, 'mail_auth/activate_message.html')