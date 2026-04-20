# Security Configuration Guide

## Quick Start

### Development (Default)
```bash
# No environment setup needed - DEBUG=1 is the default
python3 manage.py runserver
```

### Production
```bash
# 1. Generate a new SECRET_KEY
bash generate_secret_key.sh

# Copy the output and set it:
export SECRET_KEY='<your-generated-key>'
export DJANGO_DEBUG=0

# 2. Verify configuration
python3 manage.py check --deploy

# 3. Run production server
gunicorn project.wsgi:application --bind 0.0.0.0:8000
```

---

## Environment Variables

### DJANGO_DEBUG (Required for Production)
Controls whether Django debug mode is enabled.

```bash
# Development (default)
DJANGO_DEBUG=1      # Full error details, SQL queries, etc.

# Production
DJANGO_DEBUG=0      # Errors hidden, no sensitive information exposed
# Or: unset (defaults to '0')
```

### SECRET_KEY (Must Change Before Production)
Django's secret key for cryptographic operations.

```bash
export SECRET_KEY='<generate-with-generate_secret_key.sh>'
```

### Other Options (Optional)
See `.env.example` for other environment variables like:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`

---

## Security Settings by Environment

### Automatic Security Levels

```
┌─────────────────────────────────────────────────────────────────┐
│ Environment Variable: DJANGO_DEBUG=1 (Development)              │
├─────────────────────────────────────────────────────────────────┤
│ DEBUG = True           ✓ Full error details for debugging        │
│ CSRF_COOKIE_SECURE = False     ✓ Works over localhost HTTP      │
│ SESSION_COOKIE_SECURE = False  ✓ Works over localhost HTTP      │
│ SECURE_SSL_REDIRECT = False    ✓ Not required for localhost     │
│ ALLOWED_HOSTS = ['localhost', '127.0.0.1', ...]                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Environment Variable: DJANGO_DEBUG=0 (Production)               │
├─────────────────────────────────────────────────────────────────┤
│ DEBUG = False          ✓ No error details exposed               │
│ CSRF_COOKIE_SECURE = True      ✓ Requires HTTPS only           │
│ SESSION_COOKIE_SECURE = True   ✓ Requires HTTPS only           │
│ SECURE_SSL_REDIRECT = True     ✓ Forces HTTPS                  │
│ HSTS → Include Subdomains → Preload (1 year)                   │
│ X-Content-Type-Options = 'nosniff'  ✓ Prevents MIME sniffing  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Security Features

### ✅ CSRF Protection (Cross-Site Request Forgery)
- Token required for all POST/PUT/DELETE requests
- HttpOnly flag prevents JavaScript access
- SameSite=Strict prevents cross-site submissions
- Secure flag (production) requires HTTPS

### ✅ Session Security
- HttpOnly flag prevents JavaScript access
- Secure flag (production) requires HTTPS
- SameSite=Strict prevents cross-site leakage
- 14-day timeout (customizable)

### ✅ HTTPS Enforcement (Production)
- Automatic redirect from HTTP → HTTPS
- HSTS header (1 year) forces browser HTTPS
- Certificate pinning ready

### ✅ Headers Security
- X-Frame-Options: DENY (clickjacking protection)
- X-Content-Type-Options: nosniff (MIME sniffing prevention)
- Referrer-Policy: no-referrer-when-downgrade
- Content-Security-Policy: configured

### ✅ Password Security
- 4 validation rules enforced:
  - User attribute similarity check
  - Minimum length (8+ characters)
  - Common password blacklist
  - Numeric-only prevention

---

## Troubleshooting

### Issue: "This site can't be reached" in production
**Cause**: SECURE_SSL_REDIRECT=True requires HTTPS
**Solution**: Install SSL certificate (Let's Encrypt) and use HTTPS URLs

### Issue: CSRF token validation fails
**Cause**: Cookie domain mismatch
**Solution**: Ensure CSRF_TRUSTED_ORIGINS is properly configured

### Issue: "DEBUG" showing in error messages
**Cause**: DJANGO_DEBUG=1 set in production
**Solution**: Set `export DJANGO_DEBUG=0` in production environment

### Issue: Django check --deploy fails
**Cause**: SECRET_KEY needs to be changed
**Solution**: Run `bash generate_secret_key.sh` and set SECRET_KEY environment variable

---

## Testing

### Verify Development Mode
```bash
DJANGO_DEBUG=1 python3 manage.py check
# Should show DEBUG=True, CSRF_COOKIE_SECURE=False
```

### Verify Production Mode
```bash
DJANGO_DEBUG=0 python3 manage.py check --deploy
# Should show DEBUG=False, CSRF_COOKIE_SECURE=True
# (May show SECRET_KEY warning until you set it)
```

### Test Server is Running
```bash
curl -I http://localhost:8000/
# Should see X-Frame-Options and other security headers
```

---

## Common Deployment Scenarios

### Docker Composition
```dockerfile
ENV DJANGO_DEBUG=0
ENV SECRET_KEY=<generated-key>
RUN python3 manage.py check --deploy
```

### Systemd Service
```ini
[Service]
Environment="DJANGO_DEBUG=0"
Environment="SECRET_KEY=<generated-key>"
ExecStart=/path/to/gunicorn project.wsgi
```

### Environment File (.env)
```bash
# .env (NOT committed to git!)
DJANGO_DEBUG=0
SECRET_KEY=<generated-key>
```

Then load with: `source .env && python3 manage.py runserver`

---

## Additional Security Resources

See also:
- **SECURITY.md** - Complete production checklist
- **SECURITY_AUDIT_REPORT.md** - Detailed audit results
- **generate_secret_key.sh** - Generate production SECRET_KEY
- **.env.example** - Environment variables template

---

**Last Updated**: 2026-04-19
**Django Version**: 6.0.3
**Python Version**: 3.12+
