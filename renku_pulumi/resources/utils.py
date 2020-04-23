import base64


def b64encode(s):
    return base64.b64encode(s.encode()).decode("ascii")
