import jwt
import tornado

from constants import JWT_ALGORITHM, JWT_SECRET


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        auth_header = self.request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(
                    token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                return payload['user_id']
            except jwt.ExpiredSignatureError:
                return None
        return None
