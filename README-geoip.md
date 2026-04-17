GeoIP (GeoLite2) setup
-----------------------

This project supports local GeoIP lookups using MaxMind GeoLite2 City database and the `geoip2` Python library.

1) Install Python dependency

```bash
pip install -r requirements.txt
```

2) Download GeoLite2-City database (free) from MaxMind

- Create a free MaxMind account and generate a License Key: https://www.maxmind.com
- Download using your license key (replace `YOUR_LICENSE_KEY`):

```bash
LICENSE_KEY=YOUR_LICENSE_KEY
curl -s -L "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${LICENSE_KEY}&suffix=tar.gz" -o geolite2.tar.gz
tar xzf geolite2.tar.gz
# find the mmdb file (example path shows GeoLite2-City_*/GeoLite2-City.mmdb)
find . -name 'GeoLite2-City.mmdb' -print
```

3) Place the `GeoLite2-City.mmdb` file in one of the paths the app checks or set `GEOIP_DB_PATH` environment variable, for example:

```bash
export GEOIP_DB_PATH=/path/to/GeoLite2-City.mmdb
```

4) Restart the Django app. When the database file is present the lookup page will show `city`, `country`, `latitude`, `longitude` and `timezone` for resolved IPs.

Notes:
- MaxMind requires agreeing to their license and creating an account to download the GeoLite2 databases. This is still free for GeoLite2.
- If you prefer not to create an account, you can manually place a `GeoLite2-City.mmdb` file in the repo root and set `GEOIP_DB_PATH` accordingly.
