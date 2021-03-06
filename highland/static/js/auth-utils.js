import AWS from 'aws-sdk';

class AuthenticatedRequest {
    constructor(identity, options) {
        this.identity = identity;
        this.identity.init()
            .then(() => {
                AWS.config.update({
                    credentials: this.identity.getIdentityCredentials()
                });
                this.s3Image = new AWS.S3({
                    params: {
                        Bucket: options.imageBucket
                    }
                });
                this.s3Audio = new AWS.S3({
                    params: {
                        Bucket: options.audioBucket
                    }
                });
                console.info(this.identity);
            })
            .catch(e => console.error(e));
    }

    /**
     * @param name : key under the dedicated "directory".
     */
    postImage(data, name, type) {
        return this.postMedia(this.s3Image, data, name, type);
    }

    /**
     * @param name : key under the dedicated "directory".
     */
    postAudio(data, name, type) {
        return this.postMedia(this.s3Audio, data, name, type);
    }

    postMedia(s3, data, name, type) {
        return this.promiseRequest(this.makePostMediaRequest(s3, data, name, type));
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

    makePostMediaRequest(s3, data, name, type) {
        return (resolve, reject) => {
            s3.upload({
                Key: `${this.identity.identityId}/${name}`,
                Body: data,
                ACL: 'public-read',
                ContentType: type
            }, function(err, data) {
                if (err) {
                    reject(err);
                } else {
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
                    resolve(JSON.parse(this.response));
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
            xhr.onload = () => {
                if (xhr.status === 200 || xhr.status === 201) {
                    resolve(JSON.parse(xhr.response));
                } else {
                    reject(xhr);
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
        return new Promise((resolve, reject) => {
            this.identity.establishSession()
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
