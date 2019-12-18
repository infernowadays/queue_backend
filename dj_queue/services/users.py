import hashlib

from dj_queue.models import SQUserInfo


def generate_sq_token(username, password):
    seed = username + password
    sq_token = _inner_generate_sq_token(seed)
    while len(SQUserInfo.objects.filter(sq_token=sq_token)) > 0:
        seed += sq_token
        sq_token = _inner_generate_sq_token(seed)
    return sq_token


def _inner_generate_sq_token(seed):
    m = hashlib.sha256()
    m.update(seed.encode('utf-8'))
    hashed = m.hexdigest()
    return f'sq{hashed[:20]}'
