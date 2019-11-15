import datetime
from dateutil.parser import parse
from requests_futures.sessions import FuturesSession
# import requests

# session = requests.Session()
session = FuturesSession()


def login(username, password) -> FuturesSession:
    """Util method to gain Piscada Cloud access token"""

    credentials = {
        'piscadaId': username,
        'password': password
    }

    future = session.post('https://auth.piscada.cloud/login', json=credentials)
    return future


def list_controllers(token) -> FuturesSession:
    auth_hdr = {"Authorization": f"Bearer {token}"}

    url = 'https://controllers-api.piscada.cloud/controllers'
    return session.get(url, headers=auth_hdr)


def list_alarms(token, controller) -> FuturesSession:
    auth_hdr = {"Authorization": f"Bearer {token}"}

    return None


def parse_ts_timestamp(ts):
    ts_parsed = None
    try:
        ts_parsed = parse(ts).isoformat()
    except (ValueError, OverflowError) as err:
        print(f"Unable to parse ts timestamp", err)
    finally:
        return ts_parsed


def timeseries(token, controller, tagName, **kwargs):
    ts_from = kwargs.get('from', None)
    if ts_from:
        ts_from = parse_ts_timestamp(ts_from)
    else:
        ts_from = datetime
