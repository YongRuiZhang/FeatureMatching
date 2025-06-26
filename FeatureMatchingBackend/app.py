import os

from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from apis.detection import detection_api
from apis.matching import matching_api
from apis.mosaic import mosaic_api
from apis.User import user_api
from flask_cors import CORS  # 解决跨域问题

from models import db
from utils.Res import res

dir_path_base = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__,
            root_path=dir_path_base,
            static_folder=dir_path_base + '/static',
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


@app.get('/files/<path:filename>')
def get_files(filename):
    file_path = os.path.join(app.config['FILES_FOLDER'], filename)
    if not os.path.exists(file_path):
        return res(code='404', msg='文件不存在')
    return send_from_directory(app.config['FILES_FOLDER'], filename, as_attachment=False)


if __name__ == '__main__':
    app.run()
