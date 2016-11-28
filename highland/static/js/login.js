import React from "react";
import ReactDOM from "react-dom";
import { Button, Form, Modal } from 'react-bootstrap';
import {
    AuthenticationDetails, CognitoUser, CognitoUserPool
} from 'amazon-cognito-identity-js';
import { postAccessToken } from './auth-utils.js';
import { AlertBox, PasswordResetInputs, TextInput } from './common.js';


class NewPasswordRequiredModal extends React.Component {
    constructor(props) {
        super(props);
        this.handleChangePassword = this.handleChangePassword.bind(this);
        this.handleChangePasswordRetyped = this.handleChangePasswordRetyped.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            password: '',
            passwordRetyped: ''
        };
    }

    validInput() {
        return this.state.password &&
            this.state.password === this.state.passwordRetyped;
    }

    handleChangePassword(text) {
        this.setState({password: text});
    }

    handleChangePasswordRetyped(text) {
        this.setState({passwordRetyped: text});
    }

    handleSubmit() {
        this.props.cognitoUser.completeNewPasswordChallenge(
            this.state.password, {}, {
                onFailure: function(err) {
                    console.info(err);
                },

                onSuccess: function(resp) {
                    window.location = '/';
                }
            });
    }

    render() {
        return (
            <Modal show={this.props.showModal} onHide={this.props.handleHide}>
              <Modal.Header>
                <Modal.Title>New Password Required</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <PasswordResetInputs
                   autoFocus
                   handleChangePassword={this.handleChangePassword}
                   handleChangePasswordRetyped={this.handleChangePasswordRetyped}/>
              </Modal.Body>
              <Modal.Footer>
                <Button bsStyle="success"
                        onClick={this.handleSubmit}
                        disabled={!this.validInput()}>
                  Reset Password and Login
                </Button>
              </Modal.Footer>
            </Modal>
        );
    }
}

const AuthStatus = {
    NOT_STARTED: 'NOT_STARTED',
    AUTHENTICATING: 'AUTHENTICATING',
    AUTHENTICATED: 'AUTHENTICATED'
};

class Login extends React.Component {
    constructor(props) {
        super(props);
        this.authenticate = this.authenticate.bind(this);
        this.state = {
            username: '',
            password: '',
            cognitoUser: undefined,
            showRequireNewPasswordModal: false,
            activeAlert: null,
            authStatus: AuthStatus.NOT_STARTED
        };
    }

    authenticate() {
        this.setState({ authStatus: AuthStatus.AUTHENTICATING });

        const authenticationDetails = new AuthenticationDetails({
            Username : this.state.username,
            Password : this.state.password
        });
        const userPool = new CognitoUserPool({
            UserPoolId : this.props.cognitoUserPoolId,
            ClientId : this.props.cognitoClientId
        });

        const cognitoUser = new CognitoUser({
            Username : this.state.username,
            Pool : userPool
        });
        const self = this;
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: function (result) {
                console.log(result);
                const accessToken = result.getAccessToken().getJwtToken();
                console.log('access token + ' + accessToken);
                postAccessToken(accessToken)
                    .then(() => window.location='/')
                    .catch();
                self.setState({
                    authStatus: AuthStatus.AUTHENTICATED
                });
            },

            onFailure: function(e) {
                let content = '';

                if (e && e.code === 'UserNotFoundException') {
                    content = 'User does not exist in our record. Please double check and try again.';
                } else if (e && e.code === 'NotAuthorizedException') {
                    content = 'Incorrect username or password. Please double check and try again.';
                } else {
                    content = 'Login failed. Please try again.';
                }
                self.setState({
                    authStatus: AuthStatus.NOT_STARTED,
                    activeAlert: {
                        style: 'danger',
                        content: content
                    }
                });
            },

            newPasswordRequired: function() {
                self.setState({
                    cognitoUser: cognitoUser,
                    showRequireNewPasswordModal : true
                });
            }
        });
    }

    validInput() {
        return this.state.username && this.state.password;
    }

    buttonDisabled() {
        if (!this.validInput()) {
            return true;
        }
        if (this.state.authStatus !== AuthStatus.NOT_STARTED) {
            return true;
        }
        return false;
    }

    buttonText() {
        if (this.state.authStatus === AuthStatus.AUTHENTICATING) {
            return 'Logging in...';
        }
        if (this.state.authStatus === AuthStatus.AUTHENTICATED) {
            return 'Success :)';
        }
        return 'Log in';
    }

    render() {
        let alertBox = <div></div>;
        if (this.state.activeAlert) {
            alertBox = (
                <AlertBox style={this.state.activeAlert.style}
                          content={this.state.activeAlert.content}
                          nondismissible>
                </AlertBox>
            );
        }

        return (
            <div className="container">
              <h3>Login</h3>
              {alertBox}
              <Form>
                <TextInput name='username'
                           autoFocus
                           value={this.state.username}
                           handleChange={(t) => {this.setState({username: t});}}/>
                <TextInput name='password'
                           type='password'
                           value={this.state.password}
                           handleChange={(t) => {this.setState({password: t});}}/>
                <Button bsStyle="primary"
                        onClick={this.authenticate}
                        disabled={this.buttonDisabled()}>
                  {this.buttonText()}
                </Button>
              </Form>

              <NewPasswordRequiredModal
                 showModal={this.state.showRequireNewPasswordModal}
                 cognitoUser={this.state.cognitoUser}
                 handleHide={() => {this.setState({showRequireNewPasswordModal: false});}}
                 />
            </div>
        );
    }
}

ReactDOM.render(
    <Login cognitoUserPoolId={cognitoUserPoolId}
           cognitoClientId={cognitoClientId} />,
    document.querySelector(".mainContainer"));
