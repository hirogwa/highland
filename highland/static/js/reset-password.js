import React from "react";
import { Button } from "react-bootstrap";
import { CognitoUserPool } from 'amazon-cognito-identity-js';
import { PasswordResetInputs, TextInput } from "./common.js";

class ResetPassword extends React.Component {
    constructor(props) {
        super(props);
        this.handleChangePasswordCurrent =
            this.handleChangePasswordCurrent.bind(this);
        this.handleChangePasswordNew =
            this.handleChangePasswordNew.bind(this);
        this.handleChangePasswordNewRetyped =
            this.handleChangePasswordNewRetyped.bind(this);
        this.execute = this.execute.bind(this);
        this.state = {
            passwordCurrent: '',
            passwordNew: '',
            passwordNewRetyped: ''
        };
    }

    execute() {
        const userPool = new CognitoUserPool({
            UserPoolId: this.props.route.cognitoUserPoolId,
            ClientId: this.props.route.cognitoClientId
        });
        const cognitoUser = userPool.getCurrentUser();
        cognitoUser.getSession(function(err) {
            if (err) {
                console.error(err);
            }
        });

        cognitoUser.changePassword(
            this.state.passwordCurrent,
            this.state.passwordNew,
            function(err) {
                if (err) {
                    console.error(err);
                }
            });
    }

    validInput() {
        return this.state.passwordCurrent
            && this.state.passwordNew
            && this.state.passwordNewRetyped
            && this.state.passwordNew === this.state.passwordNewRetyped;
    }

    handleChangePasswordCurrent(text) {
        this.setState({ passwordCurrent: text });
    }

    handleChangePasswordNew(text) {
        this.setState({ passwordNew: text });
    }

    handleChangePasswordNewRetyped(text) {
        this.setState({ passwordNewRetyped: text });
    }

    render() {
        return (
            <div className="container">
              <TextInput name='Current password'
                         type='password'
                         autoFocus
                         value={this.state.passwordCurrent}
                         handleChange={this.handleChangePasswordCurrent} />
              <PasswordResetInputs
                 handleChangePassword={this.handleChangePasswordNew}
                 handleChangePasswordRetyped={this.handleChangePasswordNewRetyped} />
              <Button bsStyle="success"
                      className="pull-right"
                      onClick={this.execute}
                      disabled={!this.validInput()}>
                Reset Password
              </Button>
            </div>
        );
    }
}

module.exports = {
    ResetPassword: ResetPassword
};
