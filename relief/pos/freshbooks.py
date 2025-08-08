import functools
import time

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from requests_oauthlib import OAuth2Session

from .services import FreshbooksService


def freshbooks_access(func):
    # One-time configuration and initialization.
    refresh_url = "https://api.freshbooks.com/auth/oauth/token"
    client_id = settings.FRESHBOOKS_CLIENT_ID
    redirect_uri = settings.FRESHBOOKS_REDIRECT_URI

    @functools.wraps(func)
    def freshbooks_wrapper(request, *args, **kwargs):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        current_unix_time = int(time.time())

        freshbooks_account_id = request.session.get("freshbooks_account_id")

        print(f"wrapper:: Account ID: {freshbooks_account_id}")

        if not freshbooks_account_id:
            return HttpResponseRedirect(reverse("pos:select_company"))

        def token_updater(token):
            request.session["oauth_token"] = token.get("access_token")
            request.session["refresh_token"] = token.get("refresh_token")
            request.session["unix_token_expires"] = current_unix_time + token.get("expires_in")

            if request.user.is_authenticated:
                request.user.freshbooks_access_token = token.get("access_token")
                request.user.freshbooks_refresh_token = token.get("refresh_token")
                request.user.freshbooks_token_expires = current_unix_time + token.get("expires_in")
                request.user.save()

        oauth_token = request.session.get("oauth_token")
        refresh_token = request.session.get("refresh_token")
        expires_in = request.session.get("unix_token_expires", -1)

        print(f"wrapper:: OAuth Token: {oauth_token}")
        print(f"wrapper:: Refresh Token: {refresh_token}")
        print(f"wrapper:: Expires In: {expires_in}")

        token = {
            "access_token": oauth_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": expires_in - current_unix_time,
        }

        print(f"wrapper:: token: {token}")

        freshbooks = OAuth2Session(
            client_id,
            token=token,
            auto_refresh_url=refresh_url,
            token_updater=token_updater,
            redirect_uri=redirect_uri,
        )

        freshbooks_svc = FreshbooksService(freshbooks_account_id, freshbooks)

        response = func(request, freshbooks_svc, *args, **kwargs)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return freshbooks_wrapper
