from flask_restful import Resource 
from flask import request
import mysql.connector
from mysql.connector import Error 

from mysql_connection import get_connection

from flask_jwt_extended import get_jwt_identity, jwt_required

# Resource : API를 동작하게 만들어주는 클래스
# API 동작하는 코드를 만들기 위해서는 
# class(클래스)를 만들어야 함

# class : 비슷한 데이터끼리 모아둔 것(테이블이랑 비슷함)
# 테이블에는 컬럼이 있고, 클래스는 변수와 함수로 구성된 묶음으로
# 테이블과 다른점은 함수가 있다는 점! 

# API를 만들기 위해서는 
# flask_restful 라이브러리의 Resource 클래스를 상속해서 만들어야함
# 파이썬에서 상속은 괄호()


class RecipeListResource(Resource):  
    # 클래스 이름을 지어주고 Resource 상속함

    @jwt_required()
    def post(self):
        # 포스트로 요청한것을 처리하는 코드 작성하기
        # self 필수
        print('API 동작')

    # {  "name": "김치찌개",
    #    "descriptoion": "맛있게 끓이는 방법",
    #    "nun_of_servings": 4,
    #    "cook_time": 30,
    #    "directions": "고기볶고 김치넣고 물붓고 두부넣고",
    #    "is_publish": 1  }


        # 로직(순서)
        # 1. 클라이언트가 보낸 데이터를 받아온다.
        data = request.get_json()
        print(data) 


        # 1-1. 헤더에 담긴 JWT 토큰을 받아오기
        user_id = get_jwt_identity()

        print(user_id)
  
        # 2. 받아온 데이터를 DB에 저장한다.
        try:
            # 2-0. 데이터베이스 만든걸 연결
            connection = get_connection()

            # 2-1. 쿼리문 만들기
            # MySQL 레시피_디비에서 작성한걸 여기로 복붙함
            # 쿼리문은 MySQL에서 작성하고 문제없는지 실행 확인한 다음 여기로 가져오는거래
            ## 중요!!!!! : 컬럼과 매칭되는 데이터만 %s 로 바꿔줌!!
            
            query = '''insert into recipe
                    (name, description, num_of_servings, cook_time,
                        directions , is_publish, user_id)
                    values
                    (%s, %s, %s, %s, %s, %s, %s);'''
            
            # 2-3. 쿼리에 매칭되는 변수 처리!  중요! 튜플로 처리해준다!
            # %s 에 들어갈 내용을 아래 내용으로 넣어달라는 것
            record = (data['name'], data['description'], data['num_of_servings'],
                      data['cook_time'], data['directions'], data['is_publish'], 
                      user_id)
            

            # 2-4. 커서를 가져온다
            cursor = connection.cursor()

            # 2-5. 쿼리문을 커서로 실행한다.
            cursor.execute(query, record)

            # 2-6. DB에 반영 완료하라는 commit 해주기
            connection.commit()

            # 2-7. 자원해제
            cursor.close()
            connection.close()

        # 3. 에러났다면 에러 알려주고, 그렇지 않으면 잘 저장되었다고 알려준다.
        # 위 코드에서 에러났을때 안내해주는거
        except Error as e:  
            print(e)
            return {'result':'fall', 'error':str(e)}, 500
        
        # 정상작동되었다면 결과를 응답하기
        return {'result' : 'success'}
    
    def get(self):
        print('레시피 가져오는 API 동작')


        # 1. 클라이언트로부터 데이터를 받아온다.
        # 데이터 받을게 없어서 패스

        # 2. 저장되어있는 레시피 리스트를 DB로부터 가져온다.
        # 2-1. DB 커넥션

        try : 
            connection = get_connection()

            # 2-2. 쿼리문 만들기
            # query = ''' select * from recipe
            #             order by created_at desc; '''

            query = ''' select r.*, u.username
                        from recipe r
                        join user u
                            on r.user_id = u.id
                        where is_publish =1; '''
            
            # 2-3. 변수처리할 부분은 변수처리하기
            # 일단 없음

            # 2-4. 커서 가져오기
            cursor = connection.cursor(dictionary=True)
                            # 가져올때 딕셔너리로 바꿔달라는 것 

            # 2-5. 쿼리문을 커서로 실행하기
            cursor.execute(query)

            # 2-6. 실행결과를 가져오기
            result_list = cursor.fetchall()
            print(result_list)

            cursor.close()
            connection.close()
        
        except Error as e:
            print(e)
            return {'result':'fall', 'error':str(e)}, 500 # 클라이언트에게 보내는 http 상태 코드

        
        # 3. 데이터 가공이 필요하면 가공한 후에 클라이언트에 응답한다.
        # 파이썬에서 사용하는 datetime은 json이 못받기 때문에
        # created_at 과 updated_at 을 문자열로 변경
        i = 0
        for row in result_list:
            # print(row)
            result_list[i]['created_at'] = row['created_at'].isoformat()
            result_list[i]['updated_at'] = row['updated_at'].isoformat()
            i = i+1    

        return {'result' : 'success', 
                'count': len(result_list),
                'items' : result_list}, 200 # 상태코드숫자. 바꿔줄 수 있음!


class RecipeResource(Resource): 
    # get 메소드에서 경로로 넘어오는 변수는, get 함수의 파리미터로 사용함

    def get(self, recipe_id): 
        # 1. 클라이언트로부터 데이터를 받아오기
        # 위의 reciup_id에 담겨있다.
        print(recipe_id)

        # 2. 데이터베이스에 레시피 아이디로 쿼리하기
        try:
            connection = get_connection()

            # query = ''' select * from recipe
            #             where id = %s; '''

            query = '''select r.*, u.username
                        from recipe r
                        join user u
                            on r.user_id = u.id
                        where r.id = %s; '''

            record = (recipe_id,) 
                    # %s에 들어갈 값은 reciope_id
                    # 튜플로 값을 가져와야하기 때문에 콤마 넣음

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall() # 실행한 결과 전부 다 가져오기

            print(result_list)

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result':'fall', 'error':str(e)}, 500

        # 3. 결과를 클라이언트에 응답하기
        i = 0
        for row in result_list:
            # print(row)
            result_list[i]['created_at'] = row['created_at'].isoformat()
            result_list[i]['updated_at'] = row['updated_at'].isoformat()
            i = i+1

        # 리스트에 없는 id 정수를 입력했을때 거르기
        if (result_list) != 1:
            return {'result' : 'success', 'items' : {} }
        else:
            return {'result' : 'success', 
                        'count': len(result_list),
                        'items' : result_list[0]}, 200
        
    @jwt_required()
    def put(self, recipe_id):
        
        # 1. 클라이언트로부터 데이터를 받아오기
        print(recipe_id)

        # body에 있는 json 데이터를 받아오기(수정내용)
        data = request.get_json()
        print(data)

        # user_id를 받아온다
        user_id = get_jwt_identity()

        # 2. 데이터베이스에 업데이트 하기
        try:
            connection = get_connection()
            query = ''' update recipe
                          set name = %s, description = %s,
			              num_of_servings = %s, cook_time = %s,
                          directions = %s, is_publish = %s
                        where id = %s and user_id = %s; '''
            
            recode = (data['name'], data['description'], 
                      data['num_of_servings'], data['cook_time'], 
                      data['directions'], data['is_publish'],
                      recipe_id, user_id)
            
            corsor = connection.cursor()
            
            corsor.execute(query, recode)

            connection.commit()

            corsor.close()
            connection.close()
                     
        except Error as e:
            print(e)
            return {'result':'fall', 'error':str(e)}, 500
        
        # 결과를 응답하기
        return {'result':'success'}
    
    @jwt_required()
    def delete(self, recipe_id):
        # 1. 클라이언트로부터 데이터를 받아오기
        print(recipe_id)

        # 유저아이디 
        user_id = get_jwt_identity()

        # DB에서 삭제하기
        try:
            connection = get_connection()

            query = ''' delete from recipe
                        where id = %s and user_id = %s; '''
            
            record = (recipe_id, user_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result':'fall', 'error':str(e)}, 500

        # 결과를 응답하기
        return {'result':'success'}
        
