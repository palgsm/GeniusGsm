from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render

from .service import fetch_ip_data, fetch_rdap_data
import socket
import ipaddress
import re
import os
try:
    import dns.resolver
except Exception:
    dns = None

# Optional GeoIP2 reader (uses local GeoLite2-City.mmdb). Set path with GEOIP_DB_PATH env var.
geoip_reader = None
try:
    import geoip2.database
    possible = []
    envp = os.environ.get('GEOIP_DB_PATH')
    if envp:
        possible.append(envp)
    possible.extend([
        '/usr/share/GeoIP/GeoLite2-City.mmdb',
        '/usr/local/share/GeoIP/GeoLite2-City.mmdb',
        'GeoLite2-City.mmdb',
    ])
    for p in possible:
        try:
            if p and os.path.exists(p):
                geoip_reader = geoip2.database.Reader(p)
                break
        except Exception:
            continue
except Exception:
    geoip_reader = None


def summarize_rdap(rdap: dict) -> dict:
    """Create a compact summary from an RDAP JSON dict for UI display."""
    if not rdap or not isinstance(rdap, dict):
        return {}
    s = {}
    s['handle'] = rdap.get('handle') or rdap.get('objectClassName')
    s['name'] = rdap.get('name') or rdap.get('ldhName')
    start = rdap.get('startAddress') or rdap.get('ip_network')
    end = rdap.get('endAddress')
    if start and end:
        s['inetnum'] = f"{start} - {end}"
    elif start:
        s['inetnum'] = start
    s['country'] = rdap.get('country')
    s['type'] = rdap.get('type') or rdap.get('objectClassName')
    # entities -> simplified contacts
    ents = []
    for ent in rdap.get('entities', []) or []:
        if isinstance(ent, dict):
            c = {}
            c['handle'] = ent.get('handle')
            # vcardArray parsing
            v = ent.get('vcardArray')
            if isinstance(v, list) and len(v) >= 2:
                for item in v[1]:
                    if not isinstance(item, list) or len(item) < 4:
                        continue
                    name = item[0]
                    value = item[3]
                    if name == 'fn':
                        c['name'] = value
                    elif name == 'email':
                        c.setdefault('emails', []).append(value)
                    elif name == 'tel':
                        c.setdefault('phones', []).append(value)
                    elif name == 'org':
                        c['org'] = value
            if ent.get('roles'):
                c['roles'] = ent.get('roles')
            ents.append(c)
    # deduplicate entities by handle, then by primary email, then by name
    seen = set()
    uniq = []
    for e in ents:
        key = (e.get('handle') or '').lower(), tuple(sorted((e.get('emails') or []))), (e.get('name') or '').lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(e)
    s['entities'] = uniq
    # events/remarks
    evs = []
    for ev in rdap.get('events', []) or []:
        if isinstance(ev, dict):
            evs.append({'action': ev.get('eventAction') or ev.get('action'), 'date': ev.get('eventDate') or ev.get('date')})
    s['events'] = evs
    rks = []
    for r in rdap.get('remarks', []) or []:
        if isinstance(r, dict):
            rks.append(r.get('description') or r.get('title') or r.get('type'))
    s['remarks'] = rks
    return s
import shutil
import subprocess


@require_GET
def ip_info(request, ip: str | None = None):
    """Return IP information as JSON.

    - If `ip` path param is provided, lookup that IP.
    - If not provided, attempts to lookup requester's IP via external service.
    """
    # Accept query param `ip` as override too
    qip = request.GET.get('ip')
    target_ip = qip or ip
    # IP API removed; return RDAP data instead (best-effort)
    if not target_ip:
        return JsonResponse({'error': 'no_ip_provided'}, status=400)
    data = fetch_rdap_data(target_ip)
    return JsonResponse(data, safe=False)


def ip_lookup_page(request):
    """Render a simple page with a form to lookup an IP and show details.

    Supports GET with optional `ip` query parameter (form uses GET so URLs are shareable).
    """
    ip = request.GET.get('ip', '').strip() or None
    result = None
    rdap = None
    is_domain = False
    resolved_ips = []
    whois_domain = ''

    if ip is not None:
        # Determine whether input is an IP or a domain
        try:
            ipaddress.ip_address(ip)
            is_domain = False
        except Exception:
            is_domain = True

        if is_domain:
            # Resolve A/AAAA records (best-effort)
            try:
                host, aliases, addrs = socket.gethostbyname_ex(ip)
                resolved_ips = addrs
            except Exception:
                resolved_ips = []

            # Attempt to fetch WHOIS for domain using system whois
            try:
                if shutil.which('whois'):
                    cp = subprocess.run(['whois', ip], capture_output=True, text=True, timeout=8)
                    if cp.returncode == 0:
                        whois_domain = cp.stdout
            except Exception:
                whois_domain = ''

            # If we resolved at least one IP, fetch RDAP for each address
            ip_results = []
            if resolved_ips:
                import json as _json
                for a in resolved_ips:
                    # Fetch ipapi data (preferred) and RDAP
                    try:
                        r = fetch_ip_data(a)
                    except Exception:
                        r = {'error': 'ip lookup failed'}
                    try:
                        rd = fetch_rdap_data(a)
                    except Exception:
                        rd = {'error': 'rdap lookup failed'}

                    try:
                        rd_sum = summarize_rdap(rd) if rd and not rd.get('error') else {}
                    except Exception:
                        rd_sum = {}

                    # If ipapi provided geo fields use them, otherwise fallback to geoip_reader
                    latitude = r.get('latitude') if isinstance(r, dict) else None
                    longitude = r.get('longitude') if isinstance(r, dict) else None
                    city = r.get('city') if isinstance(r, dict) else None
                    country = r.get('country_name') or r.get('country') if isinstance(r, dict) else None
                    timezone = r.get('timezone') if isinstance(r, dict) else None

                    if not (latitude and longitude) and geoip_reader:
                        try:
                            rec = geoip_reader.city(a)
                            latitude = latitude or rec.location.latitude
                            longitude = longitude or rec.location.longitude
                            city = city or rec.city.name
                            country = country or rec.country.name
                            timezone = timezone or rec.location.time_zone
                        except Exception:
                            pass

                    ipr = {
                        'ip': a,
                        'result': r,
                        'rdap': rd,
                        'result_text': _json.dumps(r, indent=2, ensure_ascii=False) if r is not None else '',
                        'rdap_summary': rd_sum,
                    }
                    ip_results.append(ipr)
                # set primary details to the first resolved IP's RDAP
                primary = ip_results[0]
                result = primary.get('result')
                rdap = primary.get('rdap')
            else:
                result = None
                rdap = None
            # DNS details (A/AAAA/MX/NS/TXT) using dnspython if available,
            # with robust fallbacks when dnspython is not installed.
            dns_details = {'A': [], 'AAAA': [], 'MX': [], 'NS': [], 'TXT': []}

            # Primary: try dnspython if available
            if 'dns' in globals() and dns is not None:
                try:
                    resolver = dns.resolver.Resolver()
                    for rtype in ('A', 'AAAA', 'MX', 'NS', 'TXT'):
                        try:
                            answers = resolver.resolve(ip, rtype, raise_on_no_answer=False)
                            records = []
                            if answers is not None:
                                for r in answers:
                                    records.append(r.to_text())
                            dns_details[rtype] = records
                        except Exception:
                            dns_details[rtype] = []
                except Exception:
                    # dnspython present but resolver init failed for some reason
                    pass

            # Fallbacks when dnspython not available or returned nothing
            # A records: use resolved_ips (socket.gethostbyname_ex) if present
            if not dns_details.get('A'):
                dns_details['A'] = resolved_ips or []

            # AAAA: try socket.getaddrinfo for IPv6 addresses
            if not dns_details.get('AAAA'):
                try:
                    infos = socket.getaddrinfo(ip, None, socket.AF_INET6)
                    v6s = []
                    for info in infos:
                        addr = info[4][0]
                        if addr and addr not in v6s:
                            v6s.append(addr)
                    dns_details['AAAA'] = v6s
                except Exception:
                    dns_details['AAAA'] = dns_details.get('AAAA', [])

            # Helper to run external system commands (dig/host) as a fallback
            def _run_cmd(cmd):
                try:
                    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if cp.returncode == 0:
                        return [l.strip() for l in cp.stdout.splitlines() if l.strip()]
                except Exception:
                    pass
                return []

            # MX records fallback: prefer dig, then host
            if not dns_details.get('MX'):
                if shutil.which('dig'):
                    dns_details['MX'] = _run_cmd(['dig', '+short', 'MX', ip])
                elif shutil.which('host'):
                    lines = _run_cmd(['host', '-t', 'mx', ip])
                    processed = []
                    for l in lines:
                        m = re.search(r'mail is handled by\s+\d+\s+(\S+)', l)
                        if m:
                            processed.append(m.group(1))
                        else:
                            parts = l.split()
                            if parts:
                                processed.append(parts[-1])
                    dns_details['MX'] = processed

            # NS records fallback
            if not dns_details.get('NS'):
                if shutil.which('dig'):
                    dns_details['NS'] = _run_cmd(['dig', '+short', 'NS', ip])
                elif shutil.which('host'):
                    lines = _run_cmd(['host', '-t', 'ns', ip])
                    processed = []
                    for l in lines:
                        parts = l.split()
                        if parts:
                            processed.append(parts[-1])
                    dns_details['NS'] = processed

            # TXT records fallback
            if not dns_details.get('TXT'):
                if shutil.which('dig'):
                    dns_details['TXT'] = _run_cmd(['dig', '+short', 'TXT', ip])
                elif shutil.which('host'):
                    lines = _run_cmd(['host', '-t', 'txt', ip])
                    processed = []
                    for l in lines:
                        if ':' in l:
                            processed.append(l.split(':', 1)[1].strip())
                        else:
                            processed.append(l)
                    dns_details['TXT'] = processed

            # Parse domain WHOIS text into simple structured fields
            def parse_whois(text: str) -> dict:
                if not text:
                    return {}
                out = {}
                # common WHOIS labels
                patterns = {
                    'registrar': r'Registrar:\s*(.+)',
                    'registrant': r'Registrant(Name|Organization|Org|):?\s*(.+)',
                    'creation_date': r'(Creation Date|Created On|Registered On|Created):?\s*(.+)',
                    'updated_date': r'(Updated Date|Updated On|Last Updated):?\s*(.+)',
                    'expiry_date': r'(Registry Expiry Date|Expiration Date|Expires On|Expiry Date):?\s*(.+)',
                    'name_servers': r'Name Server:\s*(.+)',
                    'emails': r'([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})',
                    'dnssec': r'DNSSEC:\s*(.+)'
                }
                # additional common contact fields
                patterns.update({
                    'registrant_email': r'Registrant Email:\s*(.+)',
                    'registrant_phone': r'Registrant Phone:\s*(.+)',
                    'registrant_org': r'Registrant Organization:\s*(.+)',
                    'admin_name': r'Admin(Name|Contact):?\s*(.+)',
                    'admin_email': r'Admin Email:\s*(.+)',
                    'admin_phone': r'Admin Phone:\s*(.+)',
                    'tech_name': r'Tech(Name|Contact):?\s*(.+)',
                    'abuse_contact': r'Abuse Contact:\s*(.+)|abuse@([\w.-]+)',
                    'address': r'(Street|Address|Registrant Street):?\s*(.+)'
                })
                for k, p in patterns.items():
                    flags = re.I
                    if k == 'emails':
                        matches = re.findall(p, text, flags)
                        out[k] = list(dict.fromkeys(matches)) if matches else []
                    elif k == 'name_servers':
                        matches = re.findall(p, text, flags)
                        out[k] = [m.strip() for m in matches] if matches else []
                    else:
                        m = re.search(p, text, flags)
                        out[k] = m.group(1).strip() if m else None
                return out

            parsed_whois = parse_whois(whois_domain)
        else:
            # input is an IP address — fetch RDAP and build minimal result
            try:
                rdap = fetch_rdap_data(ip)
            except Exception:
                rdap = {'error': 'rdap lookup failed'}
            # For direct IP input, prefer ipapi data then RDAP + GeoIP fallback
            try:
                result = fetch_ip_data(ip)
            except Exception:
                result = None

            try:
                rdap = fetch_rdap_data(ip)
            except Exception:
                rdap = {'error': 'rdap lookup failed'}

            # If ipapi didn't supply geo fields, try GeoIP
            if (not result or not result.get('latitude') or not result.get('longitude')) and geoip_reader:
                try:
                    rec = geoip_reader.city(ip)
                    if result is None:
                        result = {}
                    if not result.get('city'):
                        result['city'] = rec.city.name
                    if not (result.get('country') or result.get('country_name')):
                        result['country_name'] = rec.country.name
                    result.setdefault('latitude', rec.location.latitude)
                    result.setdefault('longitude', rec.location.longitude)
                    result.setdefault('timezone', rec.location.time_zone)
                except Exception:
                    pass
            
            # Fetch additional security info from AbuseIPDB if available
            abuseipdb_data = {}
            try:
                abuseipdb_data = fetch_abuseipdb(ip)
            except Exception:
                abuseipdb_data = {}
            
            # Fetch Shodan data if available
            shodan_data = {}
            try:
                shodan_data = fetch_shodan(ip)
            except Exception:
                shodan_data = {}

    # Convert result to pretty JSON for display (kept as text to avoid XSS risks)
    import json

    result_text = json.dumps(result, indent=2, ensure_ascii=False) if result is not None else ''
    rdap_text = json.dumps(rdap, indent=2, ensure_ascii=False) if rdap is not None else ''

    # Build a structured details dict with more fields for full display
    details = {}
    # Basic reverse DNS
    reverse_dns = None
    try:
        if ip:
            reverse_dns = socket.gethostbyaddr(ip)[0]
    except Exception:
        reverse_dns = None

    details['ip'] = ip or (result.get('ip') if result else '')
    details['reverse_dns'] = reverse_dns

    # ipapi integration removed: keep ipapi slot empty
    details['ipapi'] = {}

    # Parse RDAP entities into contacts list and extract events/links/remarks
    contacts = []
    rdap_events = []
    rdap_links = []
    rdap_remarks = []
    if rdap and isinstance(rdap, dict) and not rdap.get('error'):
        # entities
        for ent in rdap.get('entities', []):
            contact = {}
            # handle
            if isinstance(ent, dict):
                contact['handle'] = ent.get('handle')
                # vcardArray parsing (rdap standard)
                v = ent.get('vcardArray')
                if isinstance(v, list) and len(v) >= 2:
                    # v[1] is list of vcard entries
                    fields = v[1]
                    for item in fields:
                        if not isinstance(item, list) or len(item) < 4:
                            continue
                        name = item[0]
                        value = item[3]
                        if name == 'fn':
                            contact['name'] = value
                        elif name == 'email':
                            contact.setdefault('emails', []).append(value)
                        elif name == 'tel':
                            contact.setdefault('phones', []).append(value)
                        elif name == 'org':
                            contact['org'] = value
                        elif name == 'adr':
                            contact.setdefault('addrs', []).append(value)
                # roles
                if ent.get('roles'):
                    contact['roles'] = ent.get('roles')
            if contact:
                contacts.append(contact)

        # events
        for ev in rdap.get('events', []):
            if isinstance(ev, dict):
                rdap_events.append({'action': ev.get('eventAction') or ev.get('action'), 'date': ev.get('eventDate') or ev.get('date')})

        # links
        for l in rdap.get('links', []):
            if isinstance(l, dict):
                rdap_links.append({'value': l.get('value'), 'rel': l.get('rel'), 'href': l.get('href')})

        # remarks
        for r in rdap.get('remarks', []):
            if isinstance(r, dict):
                rdap_remarks.append(r.get('description') or r.get('title') or r.get('type'))

    details['contacts'] = contacts
    details['rdap_events'] = rdap_events
    details['rdap_links'] = rdap_links
    details['rdap_remarks'] = rdap_remarks

    # Deduplicate details.contacts by handle/email/name to avoid repeated rows in UI
    def _dedupe_contacts(lst: list) -> list:
        seen = set()
        out = []
        for c in lst:
            handle = (c.get('handle') or '').lower()
            emails = tuple(sorted(c.get('emails') or []))
            name = (c.get('name') or '').lower()
            key = (handle, emails, name)
            if key in seen:
                continue
            seen.add(key)
            out.append(c)
        return out

    details['contacts'] = _dedupe_contacts(details.get('contacts', []))

    # If RDAP returned ARIN-style `records`, normalize them for template rendering
    arin_records = []
    if rdap and isinstance(rdap, dict):
        # Common ARIN-like wrapper: {'total':..., 'records': [...], 'net': '...'}
        recs = None
        if isinstance(rdap.get('records'), list):
            recs = rdap.get('records')
        # Some RDAP proxies place objects under 'objects' or 'data' keys; try a couple fallbacks
        if recs is None and isinstance(rdap.get('objects'), list):
            recs = rdap.get('objects')
        if recs is None and isinstance(rdap.get('data'), list):
            recs = rdap.get('data')

        if isinstance(recs, list):
            for rec in recs:
                if not isinstance(rec, dict):
                    continue
                ar = {}
                # basic flat fields
                for f in ('range', 'id', 'name', 'country', 'status', 'domain', 'created', 'updated', 'source', 'raw'):
                    ar[f] = rec.get(f)

                # nested contact/org/tech/admin/abuse blocks
                for role in ('org', 'tech', 'admin', 'abuse', 'maintainer'):
                    val = rec.get(role)
                    if isinstance(val, dict):
                        ar[role] = {
                            'id': val.get('id'),
                            'name': val.get('name'),
                            'email': val.get('email'),
                            'address': val.get('address'),
                            'country': val.get('country'),
                            'phone': val.get('phone'),
                            'raw': val.get('raw'),
                        }
                # Build ordered subroles list for template-safe iteration (avoid dynamic lookup in template)
                subroles = []
                for role in details.get('arin_roles', ['org', 'tech', 'admin', 'abuse', 'maintainer']):
                    if ar.get(role):
                        subroles.append({'role': role, 'data': ar.get(role)})
                if subroles:
                    ar['subroles'] = subroles

                arin_records.append(ar)

    details['arin_records'] = arin_records
    # Roles order for rendering ARIN sub-records in the template
    details['arin_roles'] = ['org', 'tech', 'admin', 'abuse', 'maintainer']
    # Registry metadata (some RDAP proxies return totals/page/net fields)
    registry_meta = {}
    if rdap and isinstance(rdap, dict):
        for k in ('total', 'page', 'net'):
            if rdap.get(k) is not None:
                registry_meta[k] = rdap.get(k)
    details['registry_meta'] = registry_meta

    # Try to fetch raw WHOIS via system `whois` (best-effort). Fallback to empty string.
    whois_raw = ''
    try:
        if ip and shutil.which('whois'):
            cp = subprocess.run(['whois', ip], capture_output=True, text=True, timeout=8)
            if cp.returncode == 0:
                whois_raw = cp.stdout
    except Exception:
        whois_raw = ''

    # External links for deeper lookups (open in new tab)
    # Note: RDAP, Shodan and AbuseIPDB links were intentionally removed per user request.
    external_links = {
        'censys': f'https://search.censys.io/hosts/{ip}' if ip else '',
        'virustotal': f'https://www.virustotal.com/gui/ip-address/{ip}/details' if ip else '',
        'whois_lookup': f'https://www.whois.com/whois/{ip}' if ip else '',
    }


    # Build a whois-like textual representation for nicer display
    whois_text = ''
    if result and not result.get('error'):
        lines = []
        lines.append(f"Whois IP {ip or result.get('ip', '')}")
        lines.append("")
        # Add a simple header similar to regional whois
        lines.append("% This output is generated from IP metadata lookup service.")
        lines.append("% The objects are presented in a compact human-readable form.")
        lines.append("")

        # Common network fields
        inetnum = None
        # ipapi doesn't provide inetnum, but may provide network info under 'network' or 'range'
        for key in ('range', 'network', 'inetnum'):
            if result.get(key):
                inetnum = result.get(key)
                break
        if inetnum:
            lines.append(f"inetnum:\t {inetnum}")

        # map fields
        mapping = [
            ('netname', 'org'),
            ('asn', 'asn'),
            ('org', 'org'),
            ('company', 'org'),
            ('isp', 'org'),
            ('country', 'country'),
            ('city', 'city'),
            ('region', 'region'),
            ('latitude', 'geoloc_lat'),
            ('longitude', 'geoloc_lon'),
        ]

        # Add some keys directly from ipapi-style response
        if result.get('asn'):
            lines.append(f"asn:\t {result.get('asn')}")
        if result.get('org'):
            lines.append(f"org:\t {result.get('org')}")
        if result.get('isp'):
            lines.append(f"isp:\t {result.get('isp')}")
        if result.get('country'):
            lines.append(f"country:\t {result.get('country')}")
        if result.get('postal'):
            lines.append(f"postal:\t {result.get('postal')}")
        if result.get('city'):
            lines.append(f"city:\t {result.get('city')}")
        if result.get('region'):
            lines.append(f"region:\t {result.get('region')}")

        # Omit raw geolocation coordinates from the generated WHOIS text
        # (they are still shown in the IP Details card if desired)

        # abuse/contact if present
        abuse = result.get('abuse_email') or result.get('abuse') or result.get('org')
        if abuse:
            lines.append(f"abuse-contact:\t {abuse}")

        # created/updated fields if available
        if result.get('created'):
            lines.append(f"created:\t {result.get('created')}")
        if result.get('updated'):
            lines.append(f"last-modified:\t {result.get('updated')}")

        # source
        if result.get('source'):
            lines.append(f"source:\t {result.get('source')}")

        # If RDAP data is available, append selected RDAP fields into the same whois block
        if rdap and isinstance(rdap, dict) and not rdap.get('error'):
            lines.append("")
            lines.append("% RDAP data:")
            # Common RDAP keys
            if rdap.get('handle'):
                lines.append(f"handle:\t {rdap.get('handle')}")
            start = rdap.get('startAddress') or rdap.get('ip_network')
            end = rdap.get('endAddress')
            if start and end:
                lines.append(f"inetnum:\t {start} - {end}")
            elif start:
                lines.append(f"inetnum:\t {start}")

            if rdap.get('ipVersion'):
                lines.append(f"ipVersion:\t {rdap.get('ipVersion')}")
            if rdap.get('name'):
                lines.append(f"name:\t {rdap.get('name')}")
            if rdap.get('type'):
                lines.append(f"type:\t {rdap.get('type')}")
            if rdap.get('country'):
                lines.append(f"country:\t {rdap.get('country')}")

            # cidr lists (common RDAP arrays)
            for cidr_field in ('cidr0_cidrs', 'cidr', 'cidr0', 'cidr0prefix'):
                if rdap.get(cidr_field):
                    try:
                        for item in rdap.get(cidr_field):
                            if isinstance(item, dict):
                                prefix = item.get('v4prefix') or item.get('prefix') or item.get('v4prefix')
                                if prefix:
                                    lines.append(f"cidr:\t {prefix}")
                            else:
                                lines.append(f"cidr:\t {item}")
                    except Exception:
                        pass

            # entities: list names/roles
            ents = rdap.get('entities')
            if isinstance(ents, list):
                for e in ents:
                    name = None
                    if isinstance(e, dict):
                        name = e.get('handle') or e.get('vcardArray') or e.get('roles')
                        if not name:
                            name = e.get('remarks') or e.get('ldhName')
                    if name:
                        lines.append(f"entity:\t {name}")

            # events (registration/last changed)
            events = rdap.get('events')
            if isinstance(events, list):
                for ev in events:
                    t = ev.get('eventAction') or ev.get('action')
                    d = ev.get('eventDate') or ev.get('date')
                    if t and d:
                        lines.append(f"{t}:\t {d}")

        # Remove any accidental geoloc lines before producing final WHOIS text
        filtered = [l for l in lines if 'geoloc' not in l.lower()]
        whois_text = "\n".join(filtered)

    return render(request, 'iplookup/lookup.html', {
        'query_ip': ip or '',
        'result_text': result_text,
        'result': result,
        'whois_text': whois_text,
        'rdap_text': rdap_text,
        'rdap': rdap,
        'details': details,
        'whois_raw': whois_raw,
        'external_links': external_links,
        'is_domain': is_domain,
        'resolved_ips': resolved_ips,
        'whois_domain': whois_domain,
        'dns_details': dns_details if is_domain else {},
        'parsed_whois': parsed_whois if is_domain else {},
        'ip_results': ip_results if is_domain else [],
        'abuseipdb_data': abuseipdb_data if ip and not is_domain else {},
        'shodan_data': shodan_data if ip and not is_domain else {},
    })
