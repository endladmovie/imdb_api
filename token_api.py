import uuid

VALID_TOKENS = set()

def create_token():
    token = str(uuid.uuid4())
    VALID_TOKENS.add(token)
    return token

def check_token(token):
    return token in VALID_TOKENS
