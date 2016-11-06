import React from "react";
import ReactDOM from "react-dom";
import { Button, Form } from 'react-bootstrap';
import { TextInput } from './common.js';
import {
    AuthenticationDetails, CognitoUser, CognitoUserPool
} from 'amazon-cognito-identity-js';


class Login extends React.Component {
    constructor(props) {
        super(props);
        this.authenticate = this.authenticate.bind(this);
        this.state = {
            username: '',
            password: ''
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
        cognitoUser.authenticateUser(authenticationDetails, {
            onSuccess: function (result) {
                console.log(result);
                console.log('access token + ' + result.getAccessToken().getJwtToken());
            },

            onFailure: function() {
                console.error(arguments);
            },

            newPasswordRequired: function() {
                console.info(arguments);
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
                           handleChange={(e) => {this.setState({username: e.target.value});}}/>
                <TextInput name='password'
                           value={this.state.password}
                           handleChange={(e) => {this.setState({password: e.target.value});}}/>
                <Button bsStyle="primary"
                        target="_blank"
                        onClick={this.authenticate}
                        disabled={!this.validInput()}>
                  Login
                </Button>
              </Form>
            </div>
        );
    }
}

ReactDOM.render(
    <Login cognitoUserPoolId={cognitoUserPoolId}
           cognitoClientId={cognitoClientId} />,
    document.querySelector(".mainContainer"));
