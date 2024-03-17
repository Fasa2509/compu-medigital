from dotenv import dotenv_values
import jwt as jsonwebtoken

config = dotenv_values(".env")


def encode_jwt(payload):
    secret = config.get("JWT_SECRET")
    secret = "extremadamenteseguraclave"
    if not secret:
        raise Exception()

    return jsonwebtoken.encode(payload, secret, algorithm="HS256")


def decode_jwt(chars):
    secret = config.get("JWT_SECRET")
    secret = "extremadamenteseguraclave"
    if not secret:
        raise Exception()

    return jsonwebtoken.decode(chars, secret, algorithms=["HS256"])
