from passlib.hash import pbkdf2_sha256
from config import Config

# 1. 원문 비밀번호를 단방향으로 암호화 하는 함수
def hash_password(original_password):
    password = pbkdf2_sha256.hash(original_password + Config.SALT)
                                # 비번 + 그 뒤에 붙을 문자열(아무거나 입력 가능)
                                # 노출되면 안되니깐 Config 에 입력하고 불러옴
    return password


# 2. 유저가 입력한 비번이 맞는지 확인하는 함수
def check_password(original_password, hash_password):
    check = pbkdf2_sha256.verify(original_password + Config.SALT, hash_password)
    return check

