import AWS from 'aws-sdk';

class AuthenticatedRequest {
    constructor(identity, mediaBucket) {
        this.identity = identity;
        this.identity.init()
            .then(() => {
                AWS.config.update({
                    credentials: this.identity.getIdentityCredentials()
                });
                this.s3 = new AWS.S3({
                    params: {
                        Bucket: mediaBucket
                    }
                });
            })
            .catch(e => console.error(e));
    }

    postMedia(data) {
        return this.promiseRequest(this.makePostMediaRequest(data));
    }

    get(url) {
        return this.promiseRequest(this.makeGetRequest(url));
    }

    post(url, data) {
        return this.promiseRequest(this.makeUpdateRequest('post', url, data));
    }

    postForm(url, form) {
        return this.promiseRequest(this.makeFormRequest(url, form));
    }

    put(url, data) {
        return this.promiseRequest(this.makeUpdateRequest('put', url, data));
    }

    delete(url, data) {
        return this.promiseRequest(this.makeDeleteRequest(url, data));
    }

    makePostMediaRequest(data) {
        return (resolve, reject) => {
            this.s3.upload({
                // TODO name will be UUID (from server)
                Key: `${this.identity.identityId}/${data.name}`,
                Body: data,
                ACL: 'public-read'
            }, function(err, data) {
                if (err) {
                    reject(err);
                } else {
                    console.info(data);
                    resolve(data);
                }
            });
        };
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

    makeFormRequest(url, form) {
        return (resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open('post', url, true);
            xhr.onload = function() {
                if (this.status == 201) {
                    resolve(this.response);
                } else {
                    reject(this);
                }
            };
            xhr.send(form);
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
            self.identity.establishSession()
                .then(() => makeRequest(resolve, reject))
                .catch(() => reject());
        });
    }

    logout() {
        this.identity.logout();

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
}

module.exports = {
    AuthenticatedRequest: AuthenticatedRequest
};
