# falsk 기본 틀
from flask import Flask  # 대소문자 주의!
from flask_restful import Api
from resources.recipe import RecipeListResource, RecipeResource

app = Flask(__name__)

api = Api(app)  # 변수생성

# 경로와 Api 동작코드(Resource/리솔스)를 연결하기
api.add_resource(RecipeListResource, '/recipes')
               # recipe.py에서 만든거
               
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
                            # recipe_id의 숫자 가져오기


if __name__ == '__main__':
    app.run()