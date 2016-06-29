import dateutil.parser
import traceback
from flask import request, jsonify, render_template
from highland import app, models,\
    show_operation, episode_operation, audio_operation, user_operation,\
    image_operation


@app.route('/show/<show_id>', methods=['GET'])
def get_show(show_id):
    try:
        show = show_operation.get_show_or_assert(test_user(), show_id)
        return jsonify(show=dict(show), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


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
            assert explicit is not None, 'explicit required'
            # TODO: UI not ready
            # assert image_id, 'image id required'
            assert alias, 'alias required'

            show = show_operation.create(
                test_user(), title, description, subtitle, language, author,
                category, explicit, image_id, alias)
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


@app.route('/episode', methods=['POST', 'PUT', 'DELETE'])
def episode():
    try:
        if 'POST' == request.method:
            args = request.get_json()
            (show_id, draft_status, alias, scheduled_datetime, title, subtitle,
             description, audio_id, explicit, image_id) = (
                 args.get('show_id'),
                 args.get('draft_status'),
                 args.get('alias'),
                 args.get('scheduled_datetime'),
                 args.get('title'),
                 args.get('subtitle'),
                 args.get('description'),
                 args.get('audio_id'),
                 args.get('explicit'),
                 args.get('image_id'))

            assert show_id, 'show id required'
            assert draft_status, 'draft status required'
            assert alias, 'alias required'
            assert title, 'title required'
            assert subtitle, 'subtitle required'
            assert description, 'description required'
            assert audio_id, 'audio id required'
            assert explicit is not None, 'explicit required'

            episode = episode_operation.create(
                test_user(), show_id, draft_status, alias,
                datetime_valid_or_none(scheduled_datetime), title,
                subtitle, description, audio_id, explicit, image_id)

            return jsonify(episode=dict(episode), result='success'), 201

        if 'PUT' == request.method:
            args = request.get_json()
            (show_id, id, draft_status, alias, scheduled_datetime, title,
             subtitle, description, audio_id, explicit, image_id) = (
                 args.get('show_id'),
                 args.get('id'),
                 args.get('draft_status'),
                 args.get('alias'),
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
            assert alias, 'alias required'
            assert title, 'title required'
            assert subtitle, 'subtitle required'
            assert description, 'description required'
            assert audio_id, 'audio id required'
            assert explicit is not None, 'explicit required'

            episode = episode_operation.update(
                test_user(), show_id, id, draft_status, alias,
                datetime_valid_or_none(scheduled_datetime), title, subtitle,
                description, audio_id, explicit, image_id)
            return jsonify(episode=dict(episode), result='success')

        if 'DELETE' == request.method:
            args = request.get_json()
            episode_operation.delete(test_user(),
                                     args.get('show_id'),
                                     args.get('episode_ids'))
            return jsonify(result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/episodes/<show_id>', methods=['GET'])
def get_episode_list(show_id):
    try:
        episodes = episode_operation.load(test_user(), show_id)
        return jsonify(episodes=[dict(x) for x in episodes], result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/episode/<show_id>/<episode_id>', methods=['GET'])
def get_episode(show_id, episode_id):
    try:
        episode = episode_operation.get_episode_or_assert(
            test_user(), show_id, episode_id)
        return jsonify(episode=dict(episode), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/audio', methods=['POST', 'GET', 'DELETE'])
def audio():
    try:
        if 'POST' == request.method:
            audio = audio_operation.create(test_user(), request.files['file'])
            return jsonify(audio=dict(audio), result='success'), 201
        if 'GET' == request.method:
            user = test_user()
            audios = audio_operation.load(user)

            def _dict(x):
                d = dict(x)
                d['url'] = audio_operation.get_audio_url(user, x)
                return d
            return jsonify(audios=[_dict(x) for x in audios], result='success')
        if 'DELETE' == request.method:
            args = request.get_json()
            audio_operation.delete(test_user(), args.get('audio_ids'))
            return jsonify(result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        image = image_operation.get_image_or_assert(test_user(), image_id)
        image_d = dict(image)
        image_d['url'] = image_operation.get_image_url(image)
        return jsonify(image=image_d, result='success')
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

            def _dict(x):
                d = dict(x)
                d['url'] = image_operation.get_image_url(x)
                return d
            return jsonify(images=[_dict(x) for x in images], result='success')
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


def datetime_valid_or_none(d):
    try:
        return dateutil.parser.parse(d)
    except:
        return None


@app.route('/page/show/<id_or_new>', methods=['GET'])
def dashboard_show(id_or_new):
    if id_or_new == 'new':
        mode = 'create'
        show_id = -1
    else:
        mode = 'update'
        show_id = id_or_new

    return render_template(
        'dashboard/page_show.html', show_id=show_id, mode=mode)


@app.route('/page/audio', methods=['GET'])
def dashboard_audio():
    return render_template('dashboard/page_audio.html')


@app.route('/page/episode/<show_id>/<id_or_new>', methods=['GET'])
def dashboard_episode(show_id, id_or_new):
    show_operation.get_show_or_assert(test_user(), show_id)
    if id_or_new == 'new':
        mode = 'create'
        episode_id = -1
    else:
        mode = 'update'
        episode_id = id_or_new

    return render_template(
        'dashboard/page_episode.html',
        show_id=show_id, episode_id=episode_id, mode=mode)


@app.route('/page/episode/<show_id>', methods=['GET'])
def dashboard_episode_list(show_id):
    show_operation.get_show_or_assert(test_user(), show_id)
    return render_template('dashboard/page_episode_list.html', show_id=show_id)
