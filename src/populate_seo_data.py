#!/usr/bin/env python
"""
Script to populate default SEO configurations for all GeniusGsm tools
Run this from Django shell: python manage.py shell < populate_seo.py
"""

from project.models import SEOConfig

# Default SEO configurations for each tool
SEO_DATA = [
    {
        'app_name': 'home',
        'title': 'GeniusGsm - Advanced Cybersecurity Intelligence Platform with 13+ Tools',
        'meta_description': 'GeniusGsm is a comprehensive cybersecurity platform with 13+ tools including IP lookup, abuse check, JWT analyzer, speed test, phishing detection, and more. Free online security tools for professionals.',
        'meta_keywords': 'cybersecurity tools, IP lookup, abuse check, JWT token, phishing detector, speed test, online security, IP geolocation, URL analyzer, security platform, cybersecurity, internet tools',
        'og_title': 'GeniusGsm - Cybersecurity Intelligence Platform',
        'og_description': 'Advanced cybersecurity tools for IP lookup, abuse check, JWT analysis, phishing detection, and more.',
        'twitter_title': 'GeniusGsm - Cybersecurity Tools',
        'twitter_description': 'Complete cybersecurity intelligence platform with 13+ security tools for professionals.',
        'canonical_url': 'https://geniusgsm.com/',
    },
    {
        'app_name': 'iplookup',
        'title': 'IP Lookup & Geolocation - Check IP Address Information - GeniusGsm',
        'meta_description': 'Free IP lookup tool to check IP address location, ISP, country, city, latitude/longitude, and reputation. Get detailed geolocation data for any IP address instantly.',
        'meta_keywords': 'IP lookup, IP address, geolocation, ISP lookup, IP reputation, whois lookup, IP information, IP checker, find IP address, IP geolocation, IP location, IP tracker',
        'og_title': 'Free IP Lookup & Geolocation Tool - GeniusGsm',
        'og_description': 'Check IP address location, ISP, country, and detailed geolocation information instantly.',
        'twitter_title': 'Instant IP Lookup & Geolocation',
        'twitter_description': 'Get location and ISP info for any IP address in seconds.',
        'canonical_url': 'https://geniusgsm.com/ip/lookup/',
    },
    {
        'app_name': 'abusecheck',
        'title': 'Abuse Check - IP Reputation & Blacklist Scanner - GeniusGsm',
        'meta_description': 'Check if an IP address is blacklisted or has a bad reputation. Scan IP reputation across multiple security databases and abuse lists instantly.',
        'meta_keywords': 'abuse check, IP reputation, blacklist checker, spam IP, malicious IP, IP blacklist, abuse database, spam database, IP scanner, reputation check, safety check',
        'og_title': 'IP Reputation & Blacklist Checker - GeniusGsm',
        'og_description': 'Check IP reputation and detect blacklisted or malicious IP addresses.',
        'twitter_title': 'Check IP Reputation & Blacklist Status',
        'twitter_description': 'Instantly check if an IP is blacklisted or has bad reputation.',
        'canonical_url': 'https://geniusgsm.com/abuse/lookup/',
    },
    {
        'app_name': 'ipbulk',
        'title': 'IP Bulk Checker - Batch IP Lookup & Analysis - GeniusGsm',
        'meta_description': 'Process multiple IP addresses at once with our bulk IP checker. Get geolocation, ISP, and reputation data for thousands of IPs instantly.',
        'meta_keywords': 'IP bulk, bulk IP lookup, batch IP checker, multiple IP lookup, IP batch processor, IP list checker, geolocation bulk, IP bulk analysis',
        'og_title': 'Bulk IP Checker Tool - Process Multiple IPs - GeniusGsm',
        'og_description': 'Check multiple IP addresses in bulk with instant geolocation and reputation data.',
        'twitter_title': 'Process Multiple IPs in Bulk',
        'twitter_description': 'Batch check IP addresses for location, ISP, and reputation.',
        'canonical_url': 'https://geniusgsm.com/ipbulk/groups/',
    },
    {
        'app_name': 'urlanalyzer',
        'title': 'URL Analyzer - Analyze & Check URLs for Safety - GeniusGsm',
        'meta_description': 'Analyze URLs to detect phishing, malware, and safety threats. Check URL safety, expand shortened links, and scan for malicious content.',
        'meta_keywords': 'URL analyzer, URL safety, check URL, phishing detector, malware detector, URL scanner, link safety, malicious URL, URL reputation, website safety checker',
        'og_title': 'URL Analyzer & Safety Checker - GeniusGsm',
        'og_description': 'Check if a URL is safe, detect phishing, malware, and malicious links.',
        'twitter_title': 'Analyze & Check URL Safety',
        'twitter_description': 'Scan URLs for phishing, malware, and malicious content instantly.',
        'canonical_url': 'https://geniusgsm.com/urlanalyzer/',
    },
    {
        'app_name': 'shortener',
        'title': 'Short Link Expander - Expand Shortened URLs - GeniusGsm',
        'meta_description': 'Expand and check shortened URLs (bit.ly, tinyurl, short links). Reveal the destination URL before clicking. Free online link expander tool.',
        'meta_keywords': 'short link expander, expand URL, shortened URL, bitly expander, tinyurl expander, URL shortener, link preview, destination URL, safe link checker',
        'og_title': 'Short Link Expander - Expand Shortened URLs - GeniusGsm',
        'og_description': 'Expand shortened URLs and see the real destination before clicking.',
        'twitter_title': 'Expand Shortened Links Safely',
        'twitter_description': 'Reveal what is hiding behind shortened URLs (bit.ly, tinyurl, etc).',
        'canonical_url': 'https://geniusgsm.com/shortener/',
    },
    {
        'app_name': 'preview',
        'title': 'Link Preview - Preview URLs Without Visiting - GeniusGsm',
        'meta_description': 'Preview website content, title, description, and images without visiting the URL. Safe link preview tool to inspect web pages instantly.',
        'meta_keywords': 'link preview, URL preview, website preview, page preview, safe preview, link inspection, web preview, URL inspector, page title checker',
        'og_title': 'Link Preview Tool - Preview URLs Safely - GeniusGsm',
        'og_description': 'Preview website content, images, and titles instantly without visiting the link.',
        'twitter_title': 'Preview Links & Websites',
        'twitter_description': 'See what is on a webpage before clicking the link.',
        'canonical_url': 'https://geniusgsm.com/preview/',
    },
    {
        'app_name': 'phishing',
        'title': 'Phishing Detector - Detect Phishing & Malicious Websites - GeniusGsm',
        'meta_description': 'Advanced phishing detector to identify phishing attempts and malicious websites. Protect yourself from phishing attacks and fraud.',
        'meta_keywords': 'phishing detector, phishing check, detect phishing, malicious website detector, phishing email, phishing attack, fraud detector, scam detector, website security',
        'og_title': 'Phishing & Malicious Website Detector - GeniusGsm',
        'og_description': 'Identify phishing attempts and protect yourself from malicious websites.',
        'twitter_title': 'Detect Phishing & Malware',
        'twitter_description': 'Protect yourself from phishing attacks and malicious websites.',
        'canonical_url': 'https://geniusgsm.com/phishing/',
    },
    {
        'app_name': 'randomlines',
        'title': 'Random Lines Generator - Shuffle Text & Lines - GeniusGsm',
        'meta_description': 'Shuffle and randomize text lines instantly. Free online tool to mix up, randomize, and reorder text lines in any order.',
        'meta_keywords': 'random lines, shuffle text, randomize lines, text shuffler, line mixer, random text generator, shuffle lines, text randomizer',
        'og_title': 'Random Lines Shuffler - Randomize Text - GeniusGsm',
        'og_description': 'Quickly shuffle and randomize text lines in any order.',
        'twitter_title': 'Shuffle & Randomize Text',
        'twitter_description': 'Mix up text lines randomly with one click.',
        'canonical_url': 'https://geniusgsm.com/randomlines/',
    },
    {
        'app_name': 'duplicatecounter',
        'title': 'Duplicate Counter - Find & Remove Duplicate Lines - GeniusGsm',
        'meta_description': 'Count and remove duplicate lines from text. Identify repeated entries and clean up your data with our free duplicate line remover.',
        'meta_keywords': 'duplicate counter, remove duplicates, duplicate finder, line counter, text cleaner, duplicate remover, unique lines, data deduplication',
        'og_title': 'Duplicate Counter & Remover - GeniusGsm',
        'og_description': 'Find and remove duplicate lines from text instantly.',
        'twitter_title': 'Find & Remove Duplicate Lines',
        'twitter_description': 'Count duplicates and clean up your text data.',
        'canonical_url': 'https://geniusgsm.com/duplicatecounter/',
    },
    {
        'app_name': 'jwtchecker',
        'title': 'JWT Checker - Decode & Analyze JWT Tokens - GeniusGsm',
        'meta_description': 'Decode and analyze JWT tokens instantly. Check header, payload, and signature of JSON Web Tokens for debugging and security analysis.',
        'meta_keywords': 'JWT checker, JWT decoder, JWT validator, JWT analyzer, JSON Web Token, token decoder, JWT parser, identity token, access token',
        'og_title': 'JWT Token Decoder & Analyzer - GeniusGsm',
        'og_description': 'Decode and validate JWT tokens to inspect headers, payloads, and signatures.',
        'twitter_title': 'Decode JWT Tokens',
        'twitter_description': 'Instantly decode and analyze JSON Web Tokens.',
        'canonical_url': 'https://geniusgsm.com/jwtchecker/',
    },
    {
        'app_name': 'tempmail',
        'title': 'Temp Mail - Temporary Email Address Generator - GeniusGsm',
        'meta_description': 'Generate temporary email addresses instantly. Use disposable email to protect your privacy and avoid spam when signing up online.',
        'meta_keywords': 'temp mail, temporary email, disposable email, anonymous email, throw away email, privacy email, spam protection, email generator',
        'og_title': 'Temporary Email Generator - GeniusGsm',
        'og_description': 'Create temporary email addresses to protect your privacy online.',
        'twitter_title': 'Create Temporary Emails',
        'twitter_description': 'Generate disposable email addresses instantly.',
        'canonical_url': 'https://geniusgsm.com/tempmail/',
    },
    {
        'app_name': 'speedtest',
        'title': 'Internet Speed Test - Check Download, Upload & Ping - GeniusGsm',
        'meta_description': 'Fast and accurate internet speed test. Check your download speed, upload speed, and ping (latency). Get instant results with our free online speed tester.',
        'meta_keywords': 'speed test, internet speed test, download speed, upload speed, ping test, bandwidth test, connection speed, broadband test, internet speed checker, speed meter',
        'og_title': 'Internet Speed Test Tool - GeniusGsm',
        'og_description': 'Check your internet speed with our fast and accurate online speed test tool.',
        'twitter_title': 'Test Your Internet Speed',
        'twitter_description': 'Check download, upload, and ping speeds instantly.',
        'canonical_url': 'https://geniusgsm.com/speedtest/',
    },
]

# Create SEO configs
for data in SEO_DATA:
    config, created = SEOConfig.objects.get_or_create(
        app_name=data['app_name'],
        defaults=data
    )
    if created:
        print(f"✅ Created SEO config for {config.get_app_name_display()}")
    else:
        # Update existing
        for key, value in data.items():
            if key != 'app_name':
                setattr(config, key, value)
        config.save()
        print(f"✅ Updated SEO config for {config.get_app_name_display()}")

print(f"\n✨ Done: Successfully loaded {len(SEO_DATA)} SEO applications!")
