import dateutil.parser
import traceback

from flask import request, jsonify, redirect, render_template, \
    url_for, Response

from highland import app, \
    show_operation, episode_operation, audio_operation, user_operation,\
    image_operation, public_view, feed_operation, stat_operation, settings,\
    cognito_auth

app.secret_key = settings.APP_SECRET
auth = cognito_auth.CognitoAuth(settings.COGNITO_JWT_SET,
                                settings.COGNITO_REGION,
                                settings.COGNITO_USER_POOL_ID)


page_loaders = []


def page_loader(func):
    if func.__name__ not in []:
        page_loaders.append(func.__name__)
    print(page_loaders)
    return func


@app.route('/stat/episode_by_day', methods=['GET'])
@auth.require_authenticated()
def stat_episode_by_day():
    show_id = request.args.get('show_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    assert show_id, 'show_id required'
    return jsonify(
        stat_operation.get_episode_by_day(
            auth.authenticated_user, show_id, date_from, date_to))


@app.route('/stat/episode_past_week', methods=['GET'])
@auth.require_authenticated()
def stat_episode_past_week():
    show_id = request.args.get('show_id')
    assert show_id, 'show_id required'
    return jsonify(stat_operation.get_episode_one_week(
        auth.authenticated_user, show_id))


@app.route('/stat/episode_cumulative', methods=['GET'])
@auth.require_authenticated()
def stat_episode_cumulative():
    show_id = request.args.get('show_id')
    assert show_id, 'show_id required'
    return jsonify(stat_operation.get_episode_cumulative(
        auth.authenticated_user, show_id))


@app.route('/show/<show_id>', methods=['GET'])
@auth.require_authenticated()
def get_show(show_id):
    try:
        show = show_operation.get_show_or_assert(
            auth.authenticated_user, show_id)
        return jsonify(show=dict(show), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/show', methods=['POST', 'PUT', 'GET'])
@auth.require_authenticated()
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
            assert alias, 'alias required'

            show = show_operation.create(
                auth.authenticated_user, title, description, subtitle,
                language, author, category, explicit, image_id, alias)
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

            show = show_operation.update(
                auth.authenticated_user, id, title, description, subtitle,
                language, author, category, explicit, image_id)
            return jsonify(show=dict(show), result='success')

        if 'GET' == request.method:
            shows = show_operation.load(auth.authenticated_user)
            return jsonify(shows=list(map(dict, shows)), result='success')
    except Exception:
        app.logger.error(traceback.format_exc())
        return jsonify(result='error'), 500


@app.route('/episode', methods=['POST', 'PUT', 'DELETE'])
@auth.require_authenticated()
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
            assert explicit is not None, 'explicit required'

            episode = episode_operation.create(
                auth.authenticated_user, show_id, draft_status, alias,
                audio_id, image_id, datetime_valid_or_none(scheduled_datetime),
                title, subtitle, description, explicit)

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
            assert explicit is not None, 'explicit required'

            episode = episode_operation.update(
                auth.authenticated_user, show_id, id, draft_status, alias,
                audio_id, image_id, datetime_valid_or_none(scheduled_datetime),
                title, subtitle, description, explicit)
            return jsonify(episode=dict(episode), result='success')

        if 'DELETE' == request.method:
            args = request.get_json()
            episode_operation.delete(auth.authenticated_user,
                                     args.get('show_id'),
                                     args.get('episode_ids'))
            return jsonify(result='success')
    except Exception:
        app.logger.error(traceback.format_exc())
        return jsonify(result='error'), 500


@app.route('/episodes/<show_id>', methods=['GET'])
@auth.require_authenticated()
def get_episode_list(show_id):
    try:
        public = request.args.get('public')
        if public:
            episodes = episode_operation.load_public(
                auth.authenticated_user, show_id)
        else:
            episodes = episode_operation.load(
                auth.authenticated_user, show_id)
        return jsonify(episodes=[dict(x) for x in episodes], result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/episode/<show_id>/<episode_id>', methods=['GET'])
@auth.require_authenticated()
def get_episode(show_id, episode_id):
    try:
        episode = episode_operation.get_episode_or_assert(
            auth.authenticated_user, show_id, episode_id)
        return jsonify(episode=dict(episode), result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/audio', methods=['POST', 'GET', 'DELETE'])
@auth.require_authenticated()
def audio():
    try:
        if 'POST' == request.method:
            audio = audio_operation.create(
                auth.authenticated_user, request.files['file'])
            return jsonify(audio=dict(audio), result='success'), 201
        if 'GET' == request.method:
            args = request.args
            unused_only = args.get('unused_only') == 'True'
            whitelisted_id = args.get('whitelisted_id')
            user = auth.authenticated_user
            audios = audio_operation.load(
                user, unused_only,
                int(whitelisted_id) if whitelisted_id else None)

            return jsonify(audios=audios, result='success')
        if 'DELETE' == request.method:
            args = request.get_json()
            audio_operation.delete(auth.authenticated_user, args.get('ids'))
            return jsonify(result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/image/<image_id>', methods=['GET'])
@auth.require_authenticated()
def get_image(image_id):
    try:
        user = auth.authenticated_user
        image = image_operation.get_image_or_assert(user, image_id)
        image_d = dict(image)
        image_d['url'] = image_operation.get_image_url(user, image)
        return jsonify(image=image_d, result='success')
    except Exception as e:
        app.logger.error(traceback.format_exc())
        raise e


@app.route('/image', methods=['POST', 'GET', 'DELETE'])
@auth.require_authenticated()
def image():
    try:
        if 'POST' == request.method:
            image = image_operation.create(
                auth.authenticated_user, request.files['file'])
            return jsonify(image=dict(image), result='success'), 201
        if 'GET' == request.method:
            user = auth.authenticated_user
            images = image_operation.load(user)

            def _dict(x):
                d = dict(x)
                d['url'] = image_operation.get_image_url(user, x)
                return d
            return jsonify(images=[_dict(x) for x in images], result='success')
        if 'DELETE' == request.method:
            args = request.get_json()
            image_operation.delete(auth.authenticated_user, args.get('ids'))
            return jsonify(result='success')
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


@auth.user_loader
def get_user(username):
    return user_operation.get(username)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'


def datetime_valid_or_none(d):
    try:
        return dateutil.parser.parse(d)
    except:
        return None


@app.route('/publish_site', methods=['POST'])
def publish_site():
    '''
    test only
    '''
    args = request.get_json()
    public_view.update_full(auth.authenticated_user, args.get('show_id'))
    return 'done'


@app.route('/preview_site/<show_id>', methods=['GET'])
def preview_site(show_id):
    '''
    test only
    '''
    user = auth.authenticated_user
    show = show_operation.get_show_or_assert(user, show_id)
    show_image = image_operation.get_image_or_assert(user, show.image_id) \
        if show.image_id else None
    return public_view.show_html(
        user,
        show,
        show_image,
        episode_operation.load_public(user, show_id),
        False)


@app.route('/preview_site/<show_id>/<episode_id>', methods=['GET'])
def preview_site_episode_test(show_id, episode_id):
    '''
    test only
    '''
    user = auth.authenticated_user
    show = show_operation.get_show_or_assert(user, show_id)
    show_image = image_operation.get_image_or_assert(user, show.image_id) \
        if show.image_id else None
    return public_view.episode_html(
        user,
        show,
        show_image,
        episode_operation.get_episode_or_assert(user, show_id, episode_id),
        False)


@app.route('/preview/site/', methods=['GET'])
def preview_site_episode():
    user = auth.authenticated_user
    args = request.args
    show_id, title, subtitle, description, audio_id, image_id = \
        args.get('show_id'), \
        args.get('title'), \
        args.get('subtitle'), \
        args.get('description'), \
        args.get('audio_id'), \
        args.get('image_id')

    show = show_operation.get_show_or_assert(user, show_id)
    return public_view.preview_episode(
        user, show, title, subtitle, description, audio_id, image_id)


@app.route('/preview_feed/<show_id>', methods=['GET'])
def preview_feed(show_id):
    '''
    test only
    '''
    user = auth.authenticated_user
    return Response(
        feed_operation.generate(
            user, show_operation.get_show_or_assert(user, show_id)),
        mimetype=feed_operation.FEED_CONTENT_TYPE)


@app.route('/publish_feed', methods=['POST'])
def publish_feed():
    '''
    test only
    '''
    args = request.get_json()
    feed_operation.update(auth.authenticated_user, args.get('show_id'))
    return 'feed published'


@app.route('/', methods=['GET'])
@auth.require_authenticated(fallback=True, page=True)
@page_loader
def dashboard_page():
    shows = show_operation.load(auth.authenticated_user)
    if not shows:
        # TODO redirect: some way to create one
        return '', 401

    # assume one show per user for now
    show = shows[0]

    return render_template(
        'dashboard/dashboard.html',
        show_id=show.id,
        cognito_user_pool_id=settings.COGNITO_USER_POOL_ID,
        cognito_client_id=settings.COGNITO_CLIENT_ID)


@app.route('/login', methods=['GET'])
def login():
    if auth.authenticated:
        return redirect(url_for('dashboard_page'))

    return render_template(
        'dashboard/login.html',
        cognito_user_pool_id=settings.COGNITO_USER_POOL_ID,
        cognito_client_id=settings.COGNITO_CLIENT_ID)


@auth.unauthenticated_redirect
def login_redirect():
    return redirect(url_for('login'))


@app.route('/access_token', methods=['POST'])
@auth.login
def register_access_token():
    return jsonify(result='success',
                   username=auth.username)


@auth.refresh_token_attempt
def refresh_token_attempt():
    return redirect(url_for('refresh_token'))


@app.route('/refresh_token', methods=['GET'])
def refresh_token():
    return render_template(
        'dashboard/refresh-token.html',
        cognito_user_pool_id=settings.COGNITO_USER_POOL_ID,
        cognito_client_id=settings.COGNITO_CLIENT_ID,
        redirect_url='/', fallback_url='/login')


@app.route('/logout', methods=['POST', 'GET'])
@auth.logout
def logout():
    if request.method == 'POST':
        return jsonify(result='success')
    if request.method == 'GET':
        return login_redirect()
