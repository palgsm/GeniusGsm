import os
from typing import Dict, Any

try:
    from ipwhois import IPWhois
except Exception:
    IPWhois = None

try:
    import whois as whois_py
except Exception:
    whois_py = None

try:
    import dns.resolver
except Exception:
    dns = None

try:
    import geoip2.database
except Exception:
    geoip2 = None


def rdap_local(ip: str) -> Dict[str, Any]:
    """Lookup RDAP-like data for an IP using ipwhois locally.

    Returns a dict with keys similar to RDAP where possible, or {'error': ...}.
    """
    if IPWhois is None:
        return {'error': 'ipwhois_not_installed'}
    try:
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        return res
    except Exception as e:
        return {'error': str(e)}


def whois_local(domain: str) -> Dict[str, Any]:
    """Perform WHOIS lookup for a domain using python-whois.

    Returns dict-like object or {'error': ...}.
    """
    if whois_py is None:
        return {'error': 'python-whois_not_installed'}
    try:
        res = whois_py.whois(domain)
        # whois returns a dict-like object; convert safe fields
        out = {k: getattr(res, k, None) for k in ('domain_name', 'registrar', 'creation_date', 'updated_date', 'expiration_date', 'emails', 'name_servers')}
        return out
    except Exception as e:
        return {'error': str(e)}


def dns_local(name: str) -> Dict[str, Any]:
    """Return basic DNS records for a name using dnspython."""
    out = {'A': [], 'AAAA': [], 'MX': [], 'NS': [], 'TXT': []}
    if dns is None:
        return {'error': 'dnspython_not_installed'}
    resolver = dns.resolver.Resolver()
    for rtype in ('A', 'AAAA', 'MX', 'NS', 'TXT'):
        try:
            answers = resolver.resolve(name, rtype, raise_on_no_answer=False)
            if answers is None:
                continue
            for a in answers:
                out.setdefault(rtype, []).append(a.to_text())
        except Exception:
            continue
    return out


def geoip_local(ip: str) -> Dict[str, Any]:
    """Lookup GeoIP2 local DB if available (GEOIP_DB_PATH or common locations)."""
    if geoip2 is None:
        return {'error': 'geoip2_not_installed'}
    possible = []
    envp = os.environ.get('GEOIP_DB_PATH')
    if envp:
        possible.append(envp)
    possible.extend([
        '/usr/share/GeoIP/GeoLite2-City.mmdb',
        '/usr/local/share/GeoIP/GeoLite2-City.mmdb',
        'GeoLite2-City.mmdb',
    ])
    reader = None
    for p in possible:
        try:
            if p and os.path.exists(p):
                reader = geoip2.database.Reader(p)
                break
        except Exception:
            continue
    if reader is None:
        return {'error': 'geoip_db_not_found'}
    try:
        rec = reader.city(ip)
        return {
            'country': rec.country.name,
            'city': rec.city.name,
            'latitude': rec.location.latitude,
            'longitude': rec.location.longitude,
            'timezone': rec.location.time_zone,
        }
    except Exception as e:
        return {'error': str(e)}
