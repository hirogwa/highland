import AWS from 'aws-sdk';
import {
    AuthenticationDetails, CognitoAccessToken, CognitoIdToken, CognitoRefreshToken,
    CognitoUser, CognitoUserPool, CognitoUserSession
} from 'amazon-cognito-identity-js';

class Identity {
    constructor(cognitoUserPoolId, cognitoClientId, identityPoolId, identityProvider) {
        AWS.config.update({ region: 'us-west-2' });
        this.userPool = new CognitoUserPool({
            UserPoolId: cognitoUserPoolId,
            ClientId: cognitoClientId
        });
        this.cognitoIdentity = new AWS.CognitoIdentity();
        this.identityPoolId = identityPoolId;
        this.identityProvider = identityProvider;
    }

    init() {
        return new Promise((resolve, reject) => {
            this.establishSession()
                .then(s => {
                    this.identityCredentials = new AWS.CognitoIdentityCredentials({
                        IdentityPoolId: this.identityPoolId,
                        Logins: {
                            [this.identityProvider]: s.getIdToken().getJwtToken()
                        }
                    });
                    return Promise.resolve(s);
                })
                .then(s => {
                    this.getIdentityId(s)
                        .then(() => resolve(this));
                })
                .catch(() => {
                    reject('failed to establish session');
                });
        });
    }

    getIdentityId(session) {
        return new Promise((resolve, reject) => {
            this.cognitoIdentity.getId({
                IdentityPoolId: this.identityPoolId,
                Logins: {
                    [this.identityProvider]: session.getIdToken().getJwtToken()
                }
            }, (err, data) => {
                if (err) {
                    reject(err);
                } else {
                    this.identityId = data.IdentityId;
                    resolve(this);
                }
            });
        });
    }

    getIdentityCredentials() {
        return this.identityCredentials;
    }

    initiateUser() {
        const cognitoUser = this.userPool.getCurrentUser();
        const currentSession = this._cachedSession(cognitoUser);
        if (currentSession && currentSession.isValid()) {
            const xhr = new XMLHttpRequest();
            const idToken = currentSession.getIdToken().getJwtToken();
            const accessToken = currentSession.getAccessToken().getJwtToken();

            xhr.open('post', '/initiate_user', true);
            xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            return new Promise((resolve, reject) => {
                xhr.onload = () => {
                    if (xhr.status == 200) {
                        const data = JSON.parse(xhr.response);
                        resolve(data);
                    } else {
                        reject(xhr.statusText);
                    }
                };
                xhr.send(JSON.stringify({
                    id_token: idToken,
                    access_token: accessToken
                }));
            });
        } else {
            return Promise.reject();
        }
    }

    authenticateUser(username, password) {
        const authenticationDetails = new AuthenticationDetails({
            Username : username,
            Password : password
        });
        const cognitoUser = new CognitoUser({
            Username : username,
            Pool : this.userPool
        });

        const p = new Promise((resolve, reject) => {
            cognitoUser.authenticateUser(authenticationDetails, {
                onSuccess: result => resolve(result),
                newPasswordRequired: () => {
                    this.cognitoUserNewPasswordRequired = cognitoUser;
                    resolve('newPasswordRequired');
                },
                onFailure: e => reject(e)
            });
        });
        return p
            .then(result => {
                if (result === 'newPasswordRequired') {
                    return Promise.resolve(result);
                } else {
                    const accessToken = result.getAccessToken().getJwtToken();
                    const idToken = result.getIdToken().getJwtToken();
                    return postTokens(accessToken, idToken);
                }
            });
    }

    completeNewPasswordChallenge(password) {
        const cognitoUser = this.cognitoUserNewPasswordRequired;
        return new Promise((resolve, reject) => {
            cognitoUser.completeNewPasswordChallenge(password, {}, {
                onSuccess: resp => resolve(resp),
                onFailure: err => reject(err)
            });
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
                        postTokens(
                            session.getAccessToken().getJwtToken(),
                            session.getIdToken().getJwtToken())
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

    logout() {
        const cognitoUser = this.userPool.getCurrentUser();
        cognitoUser.signOut();
    }
}

function postTokens(accessToken, idToken) {
    const xhr = new XMLHttpRequest();
    const url = '/auth_tokens';
    xhr.open('post', url, true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    return new Promise(function(resolve, reject) {
        xhr.onload = function() {
            if (this.status == 200) {
                const data = JSON.parse(this.response);
                resolve(data);
            } else {
                console.error(this.statusText);
                reject(this.statusText);
            }
        };
        xhr.send(
            JSON.stringify({ access_token: accessToken, id_token: idToken })
        );
    });
}

module.exports = {
    Identity: Identity
};
