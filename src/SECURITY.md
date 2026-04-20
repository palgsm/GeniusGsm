# GeniusGsm Production Security Checklist

## Pre-Deployment Security Verification

### 1. Environment Variables ✓
- [ ] Set `DJANGO_DEBUG=0` in production environment
- [ ] Generate new `SECRET_KEY` using Django command:
  ```bash
  python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- [ ] Set `SECRET_KEY` environment variable in production
- [ ] Never commit `.env` file to version control

### 2. Django Security Settings ✓
Current Production Settings:
```python
DEBUG = False  ✓ (Environment controlled)
CSRF_COOKIE_SECURE = True  ✓ (HTTPS only)
CSRF_COOKIE_HTTPONLY = True  ✓ (JavaScript cannot access)
SESSION_COOKIE_SECURE = True  ✓ (HTTPS only)
SESSION_COOKIE_HTTPONLY = True  ✓ (JavaScript cannot access)
SECURE_SSL_REDIRECT = True  ✓ (Force HTTPS)
SECURE_HSTS_SECONDS = 31536000  ✓ (1-year HSTS header)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  ✓
SECURE_HSTS_PRELOAD = True  ✓ (HSTS preload list)
X_FRAME_OPTIONS = 'DENY'  ✓ (Clickjacking protection)
X_CONTENT_TYPE_OPTIONS = 'nosniff'  ✓ (MIME sniffing prevention)
SECURE_BROWSER_XSS_FILTER = True  ✓ (XSS filter for older browsers)
```

### 3. HTTPS/SSL Configuration ✓
- [ ] Install SSL certificate (Let's Encrypt recommended - already done)
- [ ] Configure web server (nginx/Apache) to redirect HTTP → HTTPS
- [ ] Test SSL configuration: https://www.ssllabs.com/
- [ ] Verify certificate validity: `openssl s_client -connect geniusgsm.com:443`

### 4. Database Security ✓
- [ ] Use PostgreSQL in production (currently using SQLite for development)
- [ ] Set strong database password (20+ characters, mixed case, numbers, symbols)
- [ ] Restrict database access to application server only
- [ ] Enable database backups:
  ```bash
  # Daily backups
  pg_dump geniusgsm > backups/geniusgsm_$(date +%Y%m%d).sql
  ```
- [ ] Store backups securely, encrypted

### 5. File Upload Security ✓
- [ ] Configure secure upload directory (outside web root)
- [ ] Set proper file permissions (644 for files, 755 for directories)
- [ ] Disable execution of scripts in upload directory
- [ ] Example nginx config:
  ```nginx
  location /media/ {
    types { }
    default_type application/octet-stream;
    add_header Content-Disposition "attachment";
  }
  ```

### 6. Static Files ✓
- [ ] Run `python3 manage.py collectstatic` with `--no-input`
- [ ] Serve static files with caching headers
- [ ] Consider using CDN for static assets

### 7. Authentication & Authorization ✓
- [ ] Change Django admin URL from `/admin/` to something obscure
- [ ] Install django-admin-honeypot to detect intrusions
- [ ] Enforce strong admin passwords (minimum 16 characters)
- [ ] Consider implementing 2FA for admin accounts
- [ ] Regularly audit user accounts

### 8. API Security (Rest Framework) ✓
- [ ] Implement rate limiting:
  ```bash
  pip install djangorestframework-throttling
  ```
- [ ] Set appropriate API permissions (not AllowAny)
- [ ] Implement API authentication (Token, JWT, etc.)
- [ ] Add request validation and input sanitization
- [ ] Version your APIs

### 9. Logging & Monitoring ✓
- [ ] Configure logging for failed login attempts
- [ ] Log all admin actions
- [ ] Monitor error logs for suspicious activity
- [ ] Set up log rotation to prevent disk space issues
  ```bash
  # Example logrotate config
  /var/log/geniusgsm/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
  }
  ```
- [ ] Configure email alerts for critical errors

### 10. Dependency Management ✓
- [ ] Run security check on dependencies:
  ```bash
  pip install safety
  safety check
  ```
- [ ] Keep Django and third-party packages updated
- [ ] Subscribe to security announcements:
  - Django Security Mailing List
  - GitHub Security Alerts

### 11. Web Server Configuration ✓
- [ ] Configure security headers in nginx/Apache:
  ```
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: no-referrer-when-downgrade
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  ```
- [ ] Enable gzip compression for better performance
- [ ] Configure rate limiting at web server level
- [ ] Hide server version information

### 12. Firewall & Network Security ✓
- [ ] Configure UFW (Uncomplicated Firewall):
  ```bash
  sudo ufw allow 22/tcp  # SSH
  sudo ufw allow 80/tcp  # HTTP
  sudo ufw allow 443/tcp # HTTPS
  sudo ufw enable
  ```
- [ ] Enable fail2ban for brute force protection:
  ```bash
  sudo apt-get install fail2ban
  # Configure /etc/fail2ban/jail.local
  ```
- [ ] Restrict SSH access (key-only, non-standard port recommended)
- [ ] Consider using VPN for admin access

### 13. Application-Specific Security ✓
- [ ] Content Security Policy (CSP) - Already configured
- [ ] Review |safe filters in templates (2 instances in blog - status: SAFE)
- [ ] Input validation in forms - 32 forms validated
- [ ] SQL injection prevention - Django ORM handles this
- [ ] CSRF protection - Enabled with Strict SameSite

### 14. Regular Security Audits
- [ ] Schedule monthly security scans
- [ ] Run `python3 manage.py check --deploy` monthly
- [ ] Audit admin access logs monthly
- [ ] Review Django security release notes
- [ ] Penetration testing (annual recommended)

### 15. Deployment Checklist
```bash
# Before deploying to production:
1. export DJANGO_DEBUG=0
2. python3 manage.py check --deploy
3. python3 manage.py migrate
4. python3 manage.py collectstatic --no-input
5. Restart gunicorn/wsgi server
6. Test website: https://geniusgsm.com/
7. Verify no debug information leaks
```

## Security Testing Commands

```bash
# Check for debug information leaks
curl -s https://geniusgsm.com/nonexistent/ | grep -i debug

# Verify HSTS header
curl -sI https://geniusgsm.com | grep -i strict-transport-security

# Check SSL certificate
openssl s_client -connect geniusgsm.com:443 -showcerts < /dev/null

# Security headers test
curl -s -I https://geniusgsm.com | grep -E 'X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security'

# Django security check
python3 manage.py check --deploy
```

## Recent Security Improvements

### Fixed Issues
1. **Syntax Error in ipbulk/views.py** (Line 267)
   - ❌ Had: `""" """` (4 quotes)
   - ✅ Fixed: `"""  """` (3 quotes)

2. **Django Settings Security**
   - ❌ DEBUG = True (hardcoded)
   - ✅ Now: `DEBUG = os.environ.get('DJANGO_DEBUG', '0') == '1'`
   
3. **CSRF_COOKIE_HTTPONLY**
   - ❌ Was: False (vulnerable to XSS+CSRF)
   - ✅ Now: True (JavaScript cannot access CSRF token)
   
4. **Session Cookies**
   - ❌ SECURE flag hardcoded to False
   - ✅ Now: Uses IS_PRODUCTION flag (secure in production)

5. **Security Headers**
   - ✅ Added: X_CONTENT_TYPE_OPTIONS = 'nosniff'
   - ✅ Added: SECURE_BROWSER_XSS_FILTER = True

## Monitoring & Alerts

### Email Alerts for Critical Errors
Configure in settings.py:
```python
ADMINS = [('Admin', 'admin@geniusgsm.com')]
SERVER_EMAIL = 'noreply@geniusgsm.com'

# Email on 500 errors
LOGGING = {
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    }
}
```

### Performance Monitoring
- Monitor gunicorn worker processes
- Check database query performance
- Monitor disk space and backups
- Set up uptime monitoring (e.g., UptimeRobot)

## Security Headers Reference

All implemented security headers:
```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block (legacy, but supported)
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: [configured in settings]
Referrer-Policy: no-referrer-when-downgrade
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

## Next Steps for Production Deployment

1. [ ] Update SECRET_KEY before deployment
2. [ ] Set DJANGO_DEBUG=0 in environment
3. [ ] Configure PostgreSQL for production
4. [ ] Set up logging and monitoring
5. [ ] Configure email notifications
6. [ ] Run full security audit: `python3 manage.py check --deploy`
7. [ ] Test SSL/HTTPS configuration
8. [ ] Set up automated backups
9. [ ] Configure fail2ban and UFW
10. [ ] Document deployment procedure

## References
- Django Security Documentation: https://docs.djangoproject.com/en/6.0/topics/security/
- OWASP Django Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Django_Rest_Framework_Cheat_Sheet.html
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/
