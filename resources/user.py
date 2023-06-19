from flask_restful import Resource 
from flask import request
import mysql.connector
from mysql.connector import Error 
from mysql_connection import get_connection
from email_validator import validate_email, EmailNotValidError
from resources.utils import check_password, hash_password
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
import datetime

# 회원가입 개발하기
class UserRegisterResource(Resource):
    def post(self):
        
        # 정보를 받아올 데이터  
        # {
        #  "username": "홍길동",
        #  "email": "abc@naver.com",
        #  "password": "1234"
        # }
        
        # 1. 클라이언트가 보낸 데이터를 받아오기
        data = request.get_json()

        # 2. 이메일 주소 형식이 올바른지 확인해보기
        try :
            validate_email(data['email'])  # data 안에 있는 email 체크

        except EmailNotValidError as e :
            return {'result':'fall', 'error':str(e)}, 400

        
        # 이메일 통과하면 여기서부터
        # 3. 비밀번호 길이가 유효한지 체크
        #    만약, 비번이 4자리 이상, 12자리 이하라고 한다면
        if len(data['password']) < 4 or len(data['password']) > 12: 
            return {'result':'fall', 'error':'비번 길이 에러'}, 400


        # 4. 비밀번호 암호화
        hashed_password = hash_password(data['password'])
        print(str(hashed_password))
        print()

        
        # 5. DB에 이미 회원정보가 있는지 확인하기
        try :
            connection = get_connection()
            query = '''select * 
                    from user
                    where email = %s;'''  # MySQL
            record = (data['email'], )  # 튜플 빼기위해 ,콤마 넣기

            cursor = connection.cursor()
            cursor.execute(query, record)
            
            result_list = cursor.fetchall()
            print(result_list)

            if len(result_list) == 1:
                return {'result':'fail', 'error':'이미 회원가입을 한 사람'},400 
            
            # if 문을 지나갔다면 회원이 아니므로, 
            # 회원가입 코드를 작성하기
            query = '''insert into user
                        (username, email, password)
                        values
                        (%s, %s, %s);'''
            record = (data['username'], data['email'], hashed_password)
                                            # data['password'] 를 사용하면 안됨
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            
            connection.commit()

            # DB에 데이터를 insert 한 후에
            # 그 인서트된 행의 아이디를 가져오는 코드
            user_id = cursor.lastrowid

            cursor.close()
            connection.close()
            

        except Error as e :
            print(e)
            return {'result':'fail', 'error':str(e)},500 
        
        # 유저아이디 암호화 인증 토큰 생성
        # create_access_token(user_id, expires_delta=datetime.timedelta(days=10))
        access_token = create_access_token(user_id)

        return {'result':'success', 'user_id':access_token}



# 로그인 개발하기
class UserLoginResource(Resource):
    def post(self):

        #   {
        #     "email": "abc@naver.com",
        #     "password": "1234"
        #    }
    
        # 1. 클라이언트가 보낸 데이터를 받아오기
        data = request.get_json()


        # 2. 이메일 주소로, DB에 select 하기
        try :
            connection = get_connection()
            query = '''select * 
                    from user
                    where email = %s;'''
            record = (data['email'],)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()
            
        except Error as e :
            print(e)
            return{'result':'fail', 'error':str(e)}, 500 
   
        # 만약 로그인 하려는데 정보가 뜨지 않는다면
        if len(result_list) == 0:
            return {'result':'fail', 'error':'회원가입한 사람 아님'}, 400 
        

        # 3. 비밀번호가 일치하는지 확인하기
        #  = 암호화된 비밀번호가 일치하는지
        print(result_list) # result_list 값 확인 테스트

        check = check_password(data['password'], result_list[0]['password'] )
        if check == False :
            return {'result':'fail', 'error':'비번이 맞지 않음'}, 400 
   
        
        # 4. 클라이언트에게 데이터를 보내주기
        access_token= create_access_token(result_list[0]['id'])

        return {'result':'success', 'user_id':access_token}



# 로그아웃 개발하기

# 로그아웃된 토큰을 저장할 set을 만들기
jwt_blocklist = set()

class UserLogoutResource(Resource):
    @jwt_required() 

    def delete(self):
        jti = get_jwt()['jti']
        print(jti)
        jwt_blocklist.add(jti)
        
        return {'result':'success'}
