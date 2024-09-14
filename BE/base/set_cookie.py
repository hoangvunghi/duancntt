import datetime

from django.http import HttpResponse
from django.utils import timezone
#import utcnow from django.utils.timezone



def set_cookie(
    response: HttpResponse,
    key: str,
    value: str,
    cookie_host: str,
    days_expire: int = 365,
):
    max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(days=days_expire), "%a, %d-%b-%Y %H:%M:%S GMT",
    )
    domain = cookie_host.split(":")[0]
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=domain,
        secure=False,
    )
