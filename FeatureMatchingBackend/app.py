from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from apis.detection import detection_api
from apis.matching import matching_api
from apis.mosaic import mosaic_api
from apis.test import test_api
from apis.User import user_api
from flask_cors import CORS  # 解决跨域问题

from models import db

dir_path_base = '/Users/yonruizhang/MyUse/school/大四/毕业设计/代码/FeatureMatching/'
app = Flask(__name__,
            root_path="http://localhost:5173",
            static_folder=dir_path_base + 'src/assets',
            template_folder=dir_path_base + "src"
            )

app.config.from_object('config.Config')
CORS(app, resources={r"/*": {"origins": "*"}})
db.init_app(app)
Migrate(app, db)
jwt = JWTManager(app)

app.register_blueprint(detection_api, url_prefix='/detection')
app.register_blueprint(matching_api, url_prefix='/matching')
app.register_blueprint(mosaic_api, url_prefix='/mosaic')
app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(test_api, url_prefix='/test')


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
