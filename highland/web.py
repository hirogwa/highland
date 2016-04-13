import json
import traceback
from flask import request, Response
from highland import app, models, show_operation


@app.route('/show', methods=['POST'])
def show():
    try:
        if 'POST' == request.method:
            args = request.get_json()
            title, description = args.get('title'), args.get('description')
            assert title, 'title required'
            assert description, 'description required'

            show = show_operation.create(test_user(), title, description)

            return json_response({
                'result': 'success',
                'show': dict(show)
            })
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


def json_response(data):
    return Response(
        json.dumps(data), mimetype='application/json')


def test_user():
    return models.User.query.filter_by(id=1).first()


@app.route('/ping', methods=['GET'])
def ping():
    app.logger.debug('processing ping request')
    print(request.form)
    print(request.args)
    print(request.get_json())
    user = models.User('name', 'email')
    return user.username
