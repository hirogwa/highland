import dateutil.parser
import traceback
from flask import request, jsonify, render_template
from highland import app, models,\
    show_operation, episode_operation, audio_operation, user_operation,\
    image_operation


@app.route('/show', methods=['POST', 'PUT', 'GET'])
def show():
    try:
        if 'POST' == request.method:
            args = request.get_json()
            (title, description, subtitle, language, author, category,
             explicit, image_id, alias) = (
                 args.get('title'),
                 args.get('description'),
                 args.get('subtitle'),
                 args.get('language'),
                 args.get('author'),
                 args.get('category'),
                 args.get('explicit'),
                 args.get('image_id'),
                 args.get('alias'))
            assert title, 'title required'
            assert description, 'description required'
            assert subtitle, 'subtitle required'
            assert language, 'language required'
            assert author, 'author required'
            assert category, 'category required'
            assert explicit, 'explicit required'
            assert image_id, 'image id required'
            assert alias, 'alias required'

            show = show_operation.create(
                test_user(), title, description, subtitle, language, author,
                category, explicit.lower() == 'True', image_id, alias)
            return jsonify(show=dict(show), result='success'), 201

        if 'PUT' == request.method:
            args = request.get_json()
            (id, title, description, subtitle, language, author, category,
             explicit, image_id) = (
                 args.get('id'),
                 args.get('title'),
                 args.get('description'),
                 args.get('subtitle'),
                 args.get('language'),
                 args.get('author'),
                 args.get('category'),
                 args.get('explicit'),
                 args.get('image_id'))
            assert id, 'id required'
            assert title, 'title required'
            assert description, 'description required'
            assert subtitle, 'subtitle required'
            assert language, 'language required'
            assert author, 'author required'
            assert category, 'category required'
            assert explicit is not None, 'explicit required'
            assert image_id, 'image id required'

            show = show_operation.update(
                test_user(), id, title, description, subtitle, language,
                author, category, explicit, image_id)
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
            (show_id, draft_status, scheduled_datetime, title, subtitle,
             description, audio_id, explicit, image_id) = (
                 args.get('show_id'),
                 args.get('draft_status'),
                 args.get('scheduled_datetime'),
                 args.get('title'),
                 args.get('subtitle'),
                 args.get('description'),
                 args.get('audio_id'),
                 args.get('explicit'),
                 args.get('image_id'))

            assert show_id, 'show id required'
            assert draft_status, 'draft status required'
            assert title, 'title required'
            assert subtitle, 'subtitle required'
            assert description, 'description required'
            assert audio_id, 'audio id required'
            assert explicit, 'explicit required'
            assert image_id, 'image id required'

            episode = episode_operation.create(
                test_user(), show_id, draft_status,
                dateutil.parser.parse(scheduled_datetime), title,
                subtitle, description, audio_id, explicit.lower() == 'true',
                image_id)

            return jsonify(episode=dict(episode), result='success'), 201

        if 'PUT' == request.method:
            args = request.get_json()
            (show_id, id, draft_status, scheduled_datetime, title, subtitle,
             description, audio_id, explicit, image_id) = (
                 args.get('show_id'),
                 args.get('id'),
                 args.get('draft_status'),
                 args.get('scheduled_datetime'),
                 args.get('title'),
                 args.get('subtitle'),
                 args.get('description'),
                 args.get('audio_id'),
                 args.get('explicit'),
                 args.get('image_id'))

            assert show_id, 'show id required'
            assert id, 'id required'
            assert draft_status, 'draft status required'
            assert title, 'title required'
            assert subtitle, 'subtitle required'
            assert description, 'description required'
            assert audio_id, 'audio id required'
            assert explicit, 'explicit required'
            assert image_id, 'image id required'

            episode = episode_operation.update(
                test_user(), show_id, id, draft_status,
                dateutil.parser.parse(scheduled_datetime), title, subtitle,
                description, audio_id, explicit.lower() == 'true', image_id)
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


@app.route('/image', methods=['POST', 'GET'])
def image():
    try:
        if 'POST' == request.method:
            image = image_operation.create(test_user(), request.files['file'])
            return jsonify(image=dict(image), result='success'), 201
        if 'GET' == request.method:
            images = image_operation.load(test_user())
            return jsonify(images=list(map(dict, images)), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/user', methods=['POST', 'PUT'])
def user():
    try:
        if 'POST' == request.method:
            args = request.get_json()
            (username, email, password, name) = (
                args.get('username'),
                args.get('email'),
                args.get('password'),
                args.get('name'))
            assert username, 'username required'
            assert email, 'email required'
            assert password, 'password required'
            assert name, 'name required'
            user = user_operation.create(username, email, password, name)
            return jsonify(user=dict(user), result='success')

        if 'PUT' == request.method:
            args = request.get_json()
            (id, username, email, password, name) = (
                args.get('id'),
                args.get('username'),
                args.get('email'),
                args.get('password'),
                args.get('name'))
            assert id, 'id required'
            assert username, 'username required'
            assert email, 'email required'
            assert password, 'password required'
            assert name, 'name required'
            user = user_operation.update(int(id), username, email, password,
                                         name)
            return jsonify(user=dict(user), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/user/<user_id>', methods=['GET'])
def user_get(user_id):
    try:
        user = user_operation.get(id=int(user_id))
        return jsonify(user=dict(user), result='success')
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
    user = models.User('name', 'email', 'somepass')
    return user.username


@app.route('/page/show', methods=['GET'])
def dashboard_show():
    return render_template('dashboard/page_show.html')
