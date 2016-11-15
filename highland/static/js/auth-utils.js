import {
    CognitoAccessToken, CognitoIdToken, CognitoRefreshToken,
    CognitoUserPool, CognitoUserSession
} from 'amazon-cognito-identity-js';

class AuthenticatedRequest {
    constructor(cognitoUserPoolId, cognitoClientId) {
        this.userPool = new CognitoUserPool({
            UserPoolId: cognitoUserPoolId,
            ClientId: cognitoClientId
        });
    }

    get(url) {
        return this.promiseRequest(this.makeGetRequest(url));
    }

    post(url, data) {
        return this.promiseRequest(this.makeUpdateRequest('post', url, data));
    }

    put(url, data) {
        return this.promiseRequest(this.makeUpdateRequest('put', url, data));
    }

    delete(url, data) {
        return this.promiseRequest(this.makeDeleteRequest(url, data));
    }

    makeGetRequest(url) {
        return (resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('get', url, true);
            xhr.onload = function() {
                if (this.status === 200) {
                    resolve(this.response);
                } else {
                    reject(this);
                }
            };
            xhr.send();
        };
    }

    makeUpdateRequest(method, url, data) {
        return (resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open(method, url, true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.onload = function() {
                if (this.status === 200 || this.status === 201) {
                    resolve(this.response);
                } else {
                    reject(this);
                }
            };
            xhr.send(JSON.stringify(data));
        };
    }

    makeDeleteRequest(url, data) {
        return (resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('delete', url, true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhr.onload = function() {
                if (this.status === 200) {
                    resolve(this.response);
                } else {
                    reject(this);
                }
            };
            xhr.send(JSON.stringify(data));
        };
    }

    promiseRequest(makeRequest) {
        const self = this;
        return new Promise(function(resolve, reject) {
            self.establishSession()
                .then(() => makeRequest(resolve, reject))
                .catch(() => reject());
        });
    }

    establishSession() {
        const cognitoUser = this.userPool.getCurrentUser();
        const currentSession = this._cachedSession(cognitoUser);
        if (currentSession && currentSession.isValid()) {
            return Promise.resolve(currentSession);
        } else {
            return new Promise(function(resolve, reject) {
                cognitoUser.getSession(function(err, session) {
                    if (err) {
                        reject(err);
                    } else {
                        postAccessToken(session.getAccessToken().getJwtToken())
                            .then((p) => resolve(p))
                            .catch((p) => reject(p));
                    }
                });
            });
        }
    }

    _cachedSession(cognitoUser) {
        const keyPrefix = "CognitoIdentityServiceProvider."
                  + `${this.userPool.getClientId()}.${cognitoUser.getUsername()}`;
        const idTokenKey = `${keyPrefix}.idToken`;
        const accessTokenKey = `${keyPrefix}.accessToken`;
        const refreshTokenKey = `${keyPrefix}.refreshToken`;

        const storage = window.localStorage;
        if (storage.getItem(idTokenKey)) {
            return new CognitoUserSession({
                IdToken: new CognitoIdToken({
                    IdToken: storage.getItem(idTokenKey)
                }),
                AccessToken: new CognitoAccessToken({
                    AccessToken: storage.getItem(accessTokenKey)
                }),
                RefreshToken: new CognitoRefreshToken({
                    RefreshToken: storage.getItem(refreshTokenKey)
                })
            });
        } else {
            return undefined;
        }

    }
}

function postAccessToken(accessToken) {
    const xhr = new XMLHttpRequest();
    const url = '/access_token';
    xhr.open('post', url, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    return new Promise(function(resolve, reject) {
        xhr.onload = function() {
            if (this.status == 200) {
                const data = JSON.parse(this.response);
                console.info(data);
                resolve(data);
            } else {
                console.error(this.statusText);
                reject(this.statusText);
            }
        };
        xhr.send(
            JSON.stringify({access_token: accessToken})
        );
    });
}

function logout() {
    const cognitoUser = this.userPool.getCurrentUser();
    cognitoUser.signOut();

    const xhr = new XMLHttpRequest();
    xhr.open('post', '/logout', true);
    return new Promise(function(resolve, reject) {
        xhr.onload = function() {
            if (this.status == 200) {
                resolve(this.response);
            } else {
                reject(this.statusText);
            }
        };
        xhr.send();
    });
}

module.exports = {
    AuthenticatedRequest: AuthenticatedRequest,
    postAccessToken: postAccessToken,
    logout: logout
};
