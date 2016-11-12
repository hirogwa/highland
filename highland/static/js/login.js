import React from "react";
import ReactDOM from "react-dom";
import { Button, Form, Modal } from 'react-bootstrap';
import { TextInput } from './common.js';
import {
    AuthenticationDetails, CognitoUser, CognitoUserPool
} from 'amazon-cognito-identity-js';


class PasswordResetInputs extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
              <TextInput name='Type password'
                         type='password'
                         value={this.props.password}
                         handleChange={this.props.handleChangePassword} />
              <TextInput name='Type password again'
                         type='password'
                         value={this.props.passwordRetyped}
                         handleChange={this.props.handleChangePasswordRetyped} />
            </div>
        );
    }
}

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

    handleChangePassword(e) {
        this.setState({password: e.target.value});
    }

    handleChangePasswordRetyped(e) {
        this.setState({passwordRetyped: e.target.value});
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
                self.postToken(accessToken);
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

    postToken(accessToken) {
        const xhr = new XMLHttpRequest();
        const url = '/access_token';
        xhr.open('post', url, true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onload = function() {
            if (this.status == 200) {
                const data = JSON.parse(this.response);
                console.info(data);
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send(
            JSON.stringify({access_token: accessToken})
        );
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
                           handleChange={(e) => {this.setState({username: e.target.value});}}/>
                <TextInput name='password'
                           type='password'
                           value={this.state.password}
                           handleChange={(e) => {this.setState({password: e.target.value});}}/>
                <Button bsStyle="primary"
                        target="_blank"
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
