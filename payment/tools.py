from urllib.parse import quote


def convert_to_uri_params(params: dict):
    return "&".join("=".join(quote(str(i)) for i in item) for item in params.items())
