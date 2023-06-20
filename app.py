# falsk 기본 틀
from flask import Flask  # 대소문자 주의!
from flask_restful import Api
from config import Config
from resources.recipe import MyRecipeListResource, RecipeListResource, RecipePublishResource, RecipeResource
from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource, jwt_blocklist
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# config 환경변수 세팅한거 서버에 적용
app.config.from_object(Config)

# JWT 매니저 초기화
jwt = JWTManager(app)

# 로그아웃된 토큰으로 요청하는 경우 
# 이 경우는 비정상적인 경우여서 jwt 가 알아서 처리하는 코드 작성
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist


api = Api(app)  # 변수생성

# 경로와 Api 동작코드(Resource/리솔스)를 연결하기
api.add_resource(RecipeListResource, '/recipes')  # recipe.py
                              
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>') # recipe.py
                            # recipe_id의 숫자 가져오기

api.add_resource(UserRegisterResource, '/user/register') # user.py  

api.add_resource(UserLoginResource, '/user/login') # user.py  

api.add_resource(UserLogoutResource, '/user/logout') # user.py  

api.add_resource(RecipePublishResource, '/recipes/<int:recipe_id>/publish') # recipe.py

api.add_resource(MyRecipeListResource, '/recipes/me') # recipe.py

if __name__ == '__main__':
    app.run()