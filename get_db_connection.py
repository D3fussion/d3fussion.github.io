import pg8000
from urllib.parse import urlparse, parse_qs

URL = ""

def get_db_connection():
    result = urlparse(URL)
    query_params = parse_qs(result.query)

    conn = pg8000.connect(
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port or 5432,
        database=result.path.lstrip('/'),
        ssl_context=True if query_params.get("sslmode", [""])[0] == "require" else None
    )

    return conn
