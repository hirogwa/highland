import traceback
from flask import request, jsonify
from highland import app, models,\
    show_operation, episode_operation, audio_operation


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


@app.route('/episode', methods=['POST', 'PUT'])
def episode():
    try:
        if 'POST' == request.method:
            args = request.get_json()
            (show_id, title, description, audio_id) = (
                args.get('show_id'),
                args.get('title'),
                args.get('description'),
                args.get('audio_id'))

            assert show_id, 'show id required'
            assert title, 'title required'
            assert description, 'description required'
            assert audio_id, 'audio id required'

            episode = episode_operation.create(
                test_user(), show_id, title, description, audio_id)

            return jsonify(episode=dict(episode), result='success'), 201

        if 'PUT' == request.method:
            args = request.get_json()
            (show_id, id, title, description, audio_id) = (
                args.get('show_id'),
                args.get('id'),
                args.get('title'),
                args.get('description'),
                args.get('audio_id'))

            assert show_id, 'show id required'
            assert id, 'id required'
            assert title, 'title required'
            assert description, 'description required'
            assert audio_id, 'audio id required'

            episode = episode_operation.update(
                test_user(), show_id, id, title, description, audio_id)
            return jsonify(episode=dict(episode), result='success')

    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/episodes/<show_id>', methods=['GET'])
def episodes(show_id):
    try:
        episodes = episode_operation.load(test_user(), show_id)
        return jsonify(episodes=list(map(dict, episodes)), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/audio', methods=['POST', 'GET'])
def audio():
    try:
        if 'POST' == request.method:
            audio = audio_operation.create(test_user(), request.files['file'])
            return jsonify(audio=dict(audio), result='success'), 201
        if 'GET' == request.method:
            audios = audio_operation.load(test_user())
            return jsonify(audios=list(map(dict, audios)), result='success')
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
