import traceback
from flask import request, jsonify
from highland import app, models, show_operation


@app.route('/show', methods=['POST', 'PUT', 'GET'])
def show():
    try:
        if 'POST' == request.method:
            args = request.get_json()
            title, description = args.get('title'), args.get('description')
            assert title, 'title required'
            assert description, 'description required'

            show = show_operation.create(test_user(), title, description)
            return jsonify(show=dict(show), result='success'), 201

        if 'PUT' == request.method:
            args = request.get_json()
            id, title, description = (
                args.get('id'), args.get('title'), args.get('description'))
            assert id, 'id required'
            assert title, 'title required'
            assert description, 'description required'

            show = show_operation.update(test_user(), id, title, description)
            return jsonify(show=dict(show), result='success')

        if 'GET' == request.method:
            shows = show_operation.load(test_user())
            return jsonify(shows=list(map(dict, shows)), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


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
