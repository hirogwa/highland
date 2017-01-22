import React from "react";
import ReactDOM from "react-dom";
import { Button, Form, Modal } from 'react-bootstrap';
import { Identity } from './identity.js';
import { AlertBox, PasswordResetInputs, TextInput } from './common.js';


const AuthStatus = {
    NOT_STARTED: 'NOT_STARTED',
    AUTHENTICATING: 'AUTHENTICATING',
    AUTHENTICATED: 'AUTHENTICATED'
};

class NewPasswordRequiredModal extends React.Component {
    constructor(props) {
        super(props);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            password: '',
            passwordRetyped: '',
            activeAlert: null,
            authStatus: AuthStatus.NOT_STARTED
        };
    }

    handleSubmit() {
        this.setState({ authStatus: AuthStatus.AUTHENTICATING });
        this.props.identity.completeNewPasswordChallenge(this.state.password)
            .then(() => this.props.identity.initiateUser())
            .then(() => {
                this.setState({
                    authStatus: AuthStatus.AUTHENTICATED
                });
                window.location = '/';
            })
            .catch(err => {
                console.error(err);
                this.setState({
                    authStatus: AuthStatus.NOT_STARTED,
                    activeAlert: {
                        style: 'danger',
                        content: 'Password reset failed. Please try again.'
                    }
                });
            });
    }

    buttonText() {
        if (this.state.authStatus === AuthStatus.AUTHENTICATING) {
            return 'Processing request...';
        }
        if (this.state.authStatus === AuthStatus.AUTHENTICATED) {
            return 'Success :)';
        }
        return 'Reset Password and Login';
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
            <Modal show={this.props.showModal} onHide={this.props.handleHide}>
              <Modal.Header>
                <Modal.Title>New Password Required</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                {alertBox}
                <PasswordResetInputs
                   autoFocus
                   buttonText={this.buttonText()}
                   password={this.state.password}
                   passwordRetyped={this.state.passwordRetyped}
                   processing={this.state.authStatus === AuthStatus.AUTHENTICATING}
                   handleChangePassword={x => this.setState({ password: x })}
                   handleChangePasswordRetyped={x => this.setState({ passwordRetyped: x })}
                   handleSubmit={this.handleSubmit} />
              </Modal.Body>
            </Modal>
        );
    }
}

class Login extends React.Component {
    constructor(props) {
        super(props);
        this.authenticate = this.authenticate.bind(this);
        this.state = {
            username: '',
            password: '',
            showRequireNewPasswordModal: false,
            activeAlert: null,
            authStatus: AuthStatus.NOT_STARTED
        };
    }

    authenticate() {
        this.setState({ authStatus: AuthStatus.AUTHENTICATING });
        this.props.identity.authenticateUser(this.state.username, this.state.password)
            .then(result => {
                if (result === 'newPasswordRequired') {
                    this.setState({
                        showRequireNewPasswordModal : true
                    });
                } else {
                    window.location = '/';
                    this.setState({
                        authStatus: AuthStatus.AUTHENTICATED
                    });
                }
            })
            .catch(e => {
                let content = '';
                if (e && e.code === 'UserNotFoundException') {
                    content = 'User does not exist in our record. Please double check and try again.';
                } else if (e && e.code === 'NotAuthorizedException') {
                    content = 'Incorrect username or password. Please double check and try again.';
                } else {
                    content = 'Login failed. Please try again.';
                }
                this.setState({
                    authStatus: AuthStatus.NOT_STARTED,
                    activeAlert: {
                        style: 'danger',
                        content: content
                    }
                });
            });
    }

    validInput() {
        return this.state.username && this.state.password;
    }

    buttonDisabled() {
        if (!this.validInput()) {
            return true;
        }
        return this.state.authStatus !== AuthStatus.NOT_STARTED;
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
                 identity={this.props.identity}
                 handleHide={() => {this.setState({showRequireNewPasswordModal: false});}}
                 />
            </div>
        );
    }
}

const identity = new Identity(
    cognitoUserPoolId, cognitoClientId,
    cognitoIdentityPoolId, cognitoIdentityProvider);

ReactDOM.render(
    <Login identity={identity} />,
    document.querySelector(".mainContainer"));
