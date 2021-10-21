import datetime
from dateutil.parser import parse
from requests_futures.sessions import FuturesSession

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


def tag_timeseries(token, controller, tag_name, **kwargs):
    auth_hdr = {"Authorization": f"Bearer {token}"}

    ts_from = kwargs.get('from', None)
    if ts_from:
        ts_from = parse_ts_timestamp(ts_from)
    else:
        ts_from = datetime.datetime.today() - datetime.timedelta(hours=1)
        ts_from = ts_from.replace(microsecond=0).isoformat()

    params = {
        'from': ts_from,
        'include_timestamps': 'true',
        'time_format': 'epoch'
    }

    ts_to = kwargs.get('to', None)
    if ts_to:
        ts_to = parse_ts_timestamp(ts_to)
        params.update({
            'to': ts_to
        })

    tags = [tag_name,]

    params.update({
        'tags': tags
    })

    return session.get(
        f'https://historian.piscada.cloud/{controller}/timeseries/json-value/{tag_name}',
        params=params,
        headers=auth_hdr
    )
