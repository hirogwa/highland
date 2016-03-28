from flask import request
from highland import app


@app.route('/ping', methods=['GET'])
def ping():
    print(request.form)
    print(request.args)
    print(request.get_json())
    return 'sup'
