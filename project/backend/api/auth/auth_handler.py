from datetime import datetime, timedelta
import uuid

import jwt
from api.base import BaseHandler
from db import DBSession
from model.model import Session, User
from constants import JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS, JWT_SECRET


class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")


class RegisterHandler(BaseHandler):
    def post(self):
        username = self.get_argument('username')
        email = self.get_argument('email')
        password = self.get_argument('password')

        db_session = DBSession()
        try:
            user = User(username=username, email=email)
            # Assuming you have a set_password method
            user.set_password(password)
            db_session.add(user)
            db_session.commit()
            self.write({"message": "User registered successfully"})
        except Exception as e:
            db_session.rollback()
            self.set_status(400)
            self.write({"error": str(e)})
        finally:
            db_session.close()


class LoginHandler(BaseHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')

        db_session = DBSession()
        try:
            user = db_session.query(User).filter_by(username=username).first()
            # Assuming you have a check_password method

            if user and user.check_password(password=password, user=user):
                payload = {
                    'user_id': str(user.user_id),
                    'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }
                jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
                refresh_token = str(uuid.uuid4())

                # Save session
                session = Session(user_id=user.user_id, jwt_token=jwt_token, refresh_token=refresh_token,
                                  expires_at=datetime.utcnow() + timedelta(days=7))
                db_session.add(session)
                db_session.commit()

                self.write({
                    "access_token": jwt_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": JWT_EXP_DELTA_SECONDS
                })
            else:
                self.set_status(401)
                self.write({"error": "Invalid username or password"})
        finally:
            db_session.close()


class LogoutHandler(BaseHandler):
    def post(self):
        token = self.get_argument('token', None)
        if token:
            db_session = DBSession()
            try:
                session = db_session.query(Session).filter_by(
                    jwt_token=token).first()
                if session:
                    session.is_active = False
                    db_session.commit()
                    self.write({"message": "Logged out successfully"})
                else:
                    self.set_status(400)
                    self.write({"error": "Invalid token"})
            finally:
                db_session.close()
        else:
            self.set_status(400)
            self.write({"error": "Token is required"})


class RefreshTokenHandler(BaseHandler):
    def post(self):
        refresh_token = self.get_argument('refresh_token')
        db_session = DBSession()
        try:
            session = db_session.query(Session).filter_by(
                refresh_token=refresh_token, is_active=True).first()
            if session and session.expires_at > datetime.utcnow():
                payload = {
                    'user_id': str(session.user_id),
                    'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                }
                new_jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)
                session.jwt_token = new_jwt_token
                db_session.commit()

                self.write({
                    "access_token": new_jwt_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": JWT_EXP_DELTA_SECONDS
                })
            else:
                self.set_status(401)
                self.write({"error": "Invalid or expired refresh token"})
        finally:
            db_session.close()
