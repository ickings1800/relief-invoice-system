from requests_oauthlib import OAuth2Session
from django.conf import settings
import functools

def freshbooks_access(func):
    # One-time configuration and initialization.
    refresh_url = "https://api.freshbooks.com/auth/oauth/token"
    client_id = settings.FRESHBOOKS_CLIENT_ID
    client_secret = settings.FRESHBOOKS_CLIENT_SECRET
    redirect_uri = settings.FRESHBOOKS_REDIRECT_URI

    extra = {
        'client_id': client_id,
        'client_secret': client_secret,
    }
    @functools.wraps(func)
    def freshbooks_wrapper(request, *args, **kwargs):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.session['client_id'] = client_id
        request.session['client_secret'] = client_secret
        request.session['redirect_uri'] = redirect_uri
        token = request.session['oauth_token']
        freshbooks_account_id = request.session.get('freshbooks_account_id', None)

        try:
            freshbooks = OAuth2Session(client_id, token=token, redirect_uri=redirect_uri)

            if not freshbooks_account_id:
                res = freshbooks.get("https://api.freshbooks.com/auth/api/v1/users/me").json()

                account_id = res.get('response')\
                                .get('business_memberships')[0]\
                                .get('business')\
                                .get('account_id')

                request.session['freshbooks_account_id'] = account_id

        except TokenExpiredError as e:
            token = freshbooks.refresh_token(refresh_url, **extra)
            request.session['oauth_token'] = token

        response = func(request, *args, **kwargs)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return freshbooks_wrapper