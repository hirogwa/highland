import React from "react";
import ReactDOM from "react-dom";
import { Button, Form, Modal } from 'react-bootstrap';
import {
    AuthenticationDetails, CognitoUser, CognitoUserPool
} from 'amazon-cognito-identity-js';
import { postAccessToken } from './auth-utils.js';
import { PasswordResetInputs, TextInput } from './common.js';


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
                    console.info(resp);
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

class Login extends React.Component {
    constructor(props) {
        super(props);
        this.authenticate = this.authenticate.bind(this);
        this.state = {
            username: '',
            password: '',
            cognitoUser: undefined,
            showRequireNewPasswordModal: false
        };
    }

    authenticate() {
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
            },

            onFailure: function() {
                console.error(arguments);
            },

            newPasswordRequired: function() {
                console.info(arguments);
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

    render() {
        return (
            <div className="container">
              <h3>Login</h3>
              <Form>
                <TextInput name='username'
                           value={this.state.username}
                           handleChange={(t) => {this.setState({username: t});}}/>
                <TextInput name='password'
                           type='password'
                           value={this.state.password}
                           handleChange={(t) => {this.setState({password: t});}}/>
                <Button bsStyle="primary"
                        type="submit"
                        onClick={this.authenticate}
                        disabled={!this.validInput()}>
                  Login
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
