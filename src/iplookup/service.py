import os
import requests
from django.core.cache import cache


IPAPI_URL = 'https://ipapi.co/{ip}/json/'
IPAPI_URL_ME = 'https://ipapi.co/json/'
RDAP_URL = 'https://rdap.org/ip/{ip}'

# Cache TTL (seconds) for IPAPI responses; configurable via env `IPAPI_CACHE_TTL`
CACHE_TTL = int(os.environ.get('IPAPI_CACHE_TTL', 300))


def fetch_ip_data(ip: str | None = None, timeout: int = 5) -> dict:
    """Fetch IP information from ipapi.co.

    If ip is None, fetches data for the caller (useful for 'me').
    Returns parsed JSON as dict, or a dict with `error` on failure.
    """
    # Simple caching to reduce rate-limit exposure
    cache_key = f"ipapi:{ip or 'me'}"
    try:
        cached = cache.get(cache_key)
    except Exception:
        cached = None
    if cached is not None:
        return cached

    try:
        url = IPAPI_URL_ME if not ip else IPAPI_URL.format(ip=ip)
        resp = requests.get(url, timeout=timeout)
        # Handle explicit rate limiting from the upstream service
        if resp.status_code == 429:
            retry_after = resp.headers.get('Retry-After')
            return {'error': 'rate_limited', 'message': 'Upstream rate limit (ipapi.co)', 'retry_after': retry_after}

        resp.raise_for_status()
        data = resp.json()
        # ipapi returns {'error': True, 'reason': ...} in some cases
        if isinstance(data, dict) and data.get('error'):
            return {'error': data.get('reason', 'unknown')}

        # cache the successful response
        try:
            cache.set(cache_key, data, CACHE_TTL)
        except Exception:
            # if cache backend is not configured or fails, ignore caching
            pass

        return data
    except requests.RequestException as exc:
        return {'error': str(exc)}


def fetch_rdap_data(ip: str, timeout: int = 6) -> dict:
    """Fetch RDAP record for an IP using rdap.org as a proxy.

    Returns parsed JSON or {'error': ...} on failure.
    """
    try:
        url = RDAP_URL.format(ip=ip)
        resp = requests.get(url, timeout=timeout, headers={'Accept': 'application/json'})
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.RequestException as exc:
        return {'error': str(exc)}


def fetch_abuseipdb(ip: str, timeout: int = 6) -> dict:
    """Fetch AbuseIPDB report for an IP if API key is configured via ABUSEIPDB_KEY.

    Returns parsed JSON or {'error': ...}.
    """
    key = os.environ.get('ABUSEIPDB_KEY')
    if not key:
        return {'error': 'no_api_key'}
    try:
        url = 'https://api.abuseipdb.com/api/v2/check'
        params = {'ipAddress': ip, 'maxAgeInDays': 90}
        headers = {'Key': key, 'Accept': 'application/json'}
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        return {'error': str(exc)}


def fetch_shodan(ip: str, timeout: int = 6) -> dict:
    """Fetch Shodan host data if SHODAN_KEY is configured via env.

    Returns parsed JSON or {'error': ...}.
    """
    key = os.environ.get('SHODAN_KEY')
    if not key:
        return {'error': 'no_api_key'}
    try:
        url = f'https://api.shodan.io/shodan/host/{ip}?key={key}'
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        return {'error': str(exc)}
