import dateutil.parser
import traceback

from datetime import datetime
from flask import request, jsonify, redirect, render_template, \
    url_for, Response

from highland import app, \
    show_operation, episode_operation, audio_operation, user_operation,\
    image_operation, public_view, feed_operation, stat_operation, \
    cognito_auth, publish, common

app.secret_key = app.config.get('APP_SECRET')
auth = cognito_auth.CognitoAuth(app.config.get('COGNITO_JWT_SET'),
                                app.config.get('COGNITO_REGION'),
                                app.config.get('COGNITO_USER_POOL_ID'))


@app.errorhandler(Exception)
def handleError(error):
    app.logger.error(traceback.format_exc())
    return jsonify(result='error'), 500


@app.route('/stat/episode_by_day', methods=['GET'])
@auth.require_authenticated()
def stat_episode_by_day():
    show_id = request.args.get('show_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    common.require_true(show_id, 'show_id required')
    return jsonify(
        stat_operation.get_episode_by_day(
            auth.authenticated_user, show_id, date_from, date_to))


@app.route('/stat/episode_past_week', methods=['GET'])
@auth.require_authenticated()
def stat_episode_past_week():
    show_id = request.args.get('show_id')
    common.require_true(show_id, 'show_id required')
    return jsonify(stat_operation.get_episode_one_week(
        auth.authenticated_user, show_id))


@app.route('/stat/episode_cumulative', methods=['GET'])
@auth.require_authenticated()
def stat_episode_cumulative():
    show_id = request.args.get('show_id')
    common.require_true(show_id, 'show_id required')
    return jsonify(stat_operation.get_episode_cumulative(
        auth.authenticated_user, show_id))


@app.route('/show/<show_id>', methods=['GET'])
@auth.require_authenticated()
def get_show(show_id):
    show = show_operation.get(show_id)
    return jsonify(show=api_model(show), result='success')


@app.route('/show', methods=['POST', 'PUT', 'GET'])
@auth.require_authenticated()
def show():
    if 'POST' == request.method:
        args = request.get_json()
        (title, description, subtitle, language, author, category,
         explicit, image_id, alias) = _get_args(
             args, 'title', 'description', 'subtitle', 'language',
             'author', 'category', 'explicit', 'image_id', 'alias')
        common.require_true(title, 'title required')
        common.require_true(description, 'description required')
        common.require_true(subtitle, 'subtitle required')
        common.require_true(language, 'language required')
        common.require_true(author, 'author required')
        common.require_true(category, 'category required')
        common.require_true(explicit is not None, 'explicit required')
        common.require_true(alias, 'alias required')

        show = show_operation.create(
            auth.authenticated_user.id, title, description, subtitle,
            language, author, category, explicit, image_id, alias)
        return jsonify(show=api_model(show), result='success'), 201

    if 'PUT' == request.method:
        args = request.get_json()
        (id, title, description, subtitle, language, author, category,
         explicit, image_id) = _get_args(
             args, 'id', 'title', 'description', 'subtitle', 'language',
             'author', 'category', 'explicit', 'image_id')
        common.require_true(id, 'id required')
        common.require_true(title, 'title required')
        common.require_true(description, 'description required')
        common.require_true(subtitle, 'subtitle required')
        common.require_true(language, 'language required')
        common.require_true(author, 'author required')
        common.require_true(category, 'category required')
        common.require_true(explicit is not None, 'explicit required')

        show = show_operation.update(
            id, title, description, subtitle,
            language, author, category, explicit, image_id)
        return jsonify(show=api_model(show), result='success')

    if 'GET' == request.method:
        shows = show_operation.load(auth.authenticated_user.id)
        return jsonify(shows=[api_model(x) for x in shows], result='success')


@app.route('/episode', methods=['POST', 'PUT', 'DELETE'])
@auth.require_authenticated()
def episode():
    if 'POST' == request.method:
        args = request.get_json()
        (show_id, draft_status, alias, scheduled_datetime, title, subtitle,
         description, audio_id, explicit, image_id) = _get_args(
             args, 'show_id', 'draft_status', 'alias',
             'scheduled_datetime', 'title', 'subtitle', 'description',
             'audio_id', 'explicit', 'image_id')

        common.require_true(show_id, 'show id required')
        common.require_true(draft_status, 'draft status required')
        common.require_true(explicit is not None, 'explicit required')

        episode = episode_operation.create(
            show_id, draft_status, alias, audio_id, image_id,
            datetime_valid_or_none(scheduled_datetime),
            title, subtitle, description, explicit)

        return jsonify(episode=api_model(episode), result='success'), 201

    if 'PUT' == request.method:
        args = request.get_json()
        (id, draft_status, alias, scheduled_datetime, title,
         subtitle, description, audio_id, explicit, image_id) = _get_args(
             args, 'id', 'draft_status', 'alias', 'scheduled_datetime',
             'title', 'subtitle', 'description', 'audio_id', 'explicit',
             'image_id')

        common.require_true(id, 'id required')
        common.require_true(draft_status, 'draft status required')
        common.require_true(explicit is not None, 'explicit required')

        episode = episode_operation.update(
            id, draft_status, alias, audio_id, image_id,
            datetime_valid_or_none(scheduled_datetime),
            title, subtitle, description, explicit)
        return jsonify(episode=api_model(episode), result='success')

    if 'DELETE' == request.method:
        args = request.get_json()
        episode_operation.delete(args.get('episode_ids'))
        return jsonify(result='success')


@app.route('/episodes/<show_id>', methods=['GET'])
@auth.require_authenticated()
def get_episode_list(show_id):
    public = request.args.get('public')
    if public:
        episodes = episode_operation.load_public(show_id)
    else:
        episodes = episode_operation.load(show_id)
    return jsonify(episodes=[api_model(x) for x in episodes], result='success')


@app.route('/episode/<show_id>/<episode_id>', methods=['GET'])
@auth.require_authenticated()
def get_episode(show_id, episode_id):
    episode = episode_operation.get(episode_id)
    return jsonify(episode=api_model(episode), result='success')


@app.route('/audio', methods=['POST', 'GET', 'DELETE'])
@auth.require_authenticated()
def audio():
    if 'POST' == request.method:
        file_name, duration, length, file_type = _get_args(
            request.get_json(), 'filename', 'duration', 'length',
            'filetype')
        audio = audio_operation.create(
            auth.authenticated_user.id, file_name, duration, length,
            file_type)
        return jsonify(audio=api_model(audio), result='success'), 201

    if 'GET' == request.method:
        args = request.args
        unused_only = args.get('unused_only') == 'True'
        whitelisted_id = args.get('whitelisted_id')
        user = auth.authenticated_user
        audios = audio_operation.load(
            user.id, unused_only,
            int(whitelisted_id) if whitelisted_id else None)

        return jsonify(audios=[api_model(x) for x in audios], result='success')

    if 'DELETE' == request.method:
        args = request.get_json()
        audio_operation.delete(args.get('ids'))
        return jsonify(result='success')


@app.route('/image/<image_id>', methods=['GET'])
@auth.require_authenticated()
def get_image(image_id):
    user = auth.authenticated_user
    image = image_operation.get(image_id)
    image_d = api_model(image)
    image_d['url'] = image_operation.get_image_url(user, image)
    return jsonify(image=image_d, result='success')


@app.route('/image', methods=['POST', 'GET', 'DELETE'])
@auth.require_authenticated()
def image():
    if 'POST' == request.method:
        file_name, file_type = _get_args(
            request.get_json(), 'filename', 'filetype')
        image = image_operation.create(
            auth.authenticated_user, file_name, file_type)
        return jsonify(image=api_model(image), result='success'), 201

    if 'GET' == request.method:
        user = auth.authenticated_user
        images = image_operation.load(user)

        def _dict(x):
            d = api_model(x)
            d['url'] = image_operation.get_image_url(user, x)
            return d
        return jsonify(images=[_dict(x) for x in images], result='success')

    if 'DELETE' == request.method:
        args = request.get_json()
        image_operation.delete(auth.authenticated_user, args.get('ids'))
        return jsonify(result='success')


@app.route('/initiate_user', methods=['POST'])
@auth.signup
def initiate_user():
    user = user_operation.create(
        auth.authenticated_username, auth.identity_id)
    return jsonify(result='success', user=api_model(user))


@app.route('/user', methods=['PUT'])
@auth.require_authenticated()
def user():
    if 'PUT' == request.method:
        args = request.get_json()
        (id, username, name) = (
            args.get('id'),
            args.get('username'),
            args.get('name'))
        common.require_true(id, 'id required')
        common.require_true(username, 'username required')
        common.require_true(name, 'name required')
        user = user_operation.update(int(id), username, name)
        return jsonify(user=api_model(user), result='success')


@auth.user_loader
def get_user(username):
    return user_operation.get(username=username)


@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'


def datetime_valid_or_none(d):
    try:
        return dateutil.parser.parse(d)
    except:
        return None


@app.route('/publish_scheduled', methods=['POST'])
def publish_scheduled():
    result = publish.publish_scheduled()
    return jsonify(result=result)


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
    show = show_operation.get(show_id)
    show_image = image_operation.get(show.image_id) if show.image_id else None
    return public_view.show_html(
        user,
        show,
        show_image,
        episode_operation.load_public(show_id),
        False)


@app.route('/preview/site/', methods=['GET'])
@auth.require_authenticated()
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

    show = show_operation.get(show_id)
    return public_view.preview_episode(
        user, show, title, subtitle, description, audio_id, image_id)


@app.route('/preview_feed/<show_id>', methods=['GET'])
def preview_feed(show_id):
    '''
    test only
    '''
    user = auth.authenticated_user
    return Response(
        feed_operation.generate(user, show_operation.get(show_id)),
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
def dashboard_page():
    shows = show_operation.load(auth.authenticated_user.id)
    if not shows:
        # TODO redirect: some way to create one
        return '', 401

    # assume one show per user for now
    show = shows[0]

    return render_template(
        'dashboard/dashboard.html',
        show_id=show.id,
        s3_bucket_image=app.config.get('S3_BUCKET_IMAGE'),
        s3_bucket_audio=app.config.get('S3_BUCKET_AUDIO'),
        cognito_user_pool_id=app.config.get('COGNITO_USER_POOL_ID'),
        cognito_client_id=app.config.get('COGNITO_CLIENT_ID'),
        cognito_identity_pool_id=app.config.get('COGNITO_IDENTITY_POOL_ID'),
        cognito_identity_provider=app.config.get('COGNITO_IDENTITY_PROVIDER'))


@app.route('/login', methods=['GET'])
def login():
    if auth.authenticated:
        return redirect(url_for('dashboard_page'))

    return render_template(
        'dashboard/login.html',
        cognito_user_pool_id=app.config.get('COGNITO_USER_POOL_ID'),
        cognito_client_id=app.config.get('COGNITO_CLIENT_ID'),
        cognito_identity_pool_id=app.config.get('COGNITO_IDENTITY_POOL_ID'),
        cognito_identity_provider=app.config.get('COGNITO_IDENTITY_PROVIDER'))


@auth.unauthenticated_redirect
def login_redirect():
    return redirect(url_for('login'))


@app.route('/auth_tokens', methods=['POST'])
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
        cognito_user_pool_id=app.config.get('COGNITO_USER_POOL_ID'),
        cognito_client_id=app.config.get('COGNITO_CLIENT_ID'),
        redirect_url='/', fallback_url='/login')


@app.route('/logout', methods=['POST', 'GET'])
@auth.logout
def logout():
    if request.method == 'POST':
        return jsonify(result='success')
    if request.method == 'GET':
        return login_redirect()


def api_model(model):
    """Format model object in a way the client expects"""

    def _value(value):
        if isinstance(value, datetime):
            return str(value)
        else:
            return value
    return {k: _value(v) for k, v in dict(model).items()}


def _get_args(param, *names):
    return [param.get(name) for name in names]
