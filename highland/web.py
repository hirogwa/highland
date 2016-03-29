from flask import request
from highland import app, models


@app.route('/ping', methods=['GET'])
def ping():
    print(request.form)
    print(request.args)
    print(request.get_json())
    user = models.User('name', 'email')
    return user.username
