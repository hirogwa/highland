import React from "react";
import { Button } from "react-bootstrap";
import { CognitoUserPool } from 'amazon-cognito-identity-js';
import { AlertBox, PasswordResetInputs, TextInput } from "./common.js";

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
            passwordNewRetyped: '',
            activeAlert: null,
            requestSent: false
        };
    }

    execute() {
        this.setState({ requestSent: true });

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

        const self = this;
        cognitoUser.changePassword(
            this.state.passwordCurrent,
            this.state.passwordNew,
            function(err) {
                let content = '';
                let style = '';
                if (err) {
                    console.error(err);
                    style = 'danger';
                    if (err.code === "NotAuthorizedException") {
                        content = 'Incorrect username or password. Please double check and try again.';
                    } else {
                        content = 'Password reset failed. Please try again.';
                    }
                } else {
                    style = 'success';
                    content = 'Password updated successfully.';
                }
                self.setState({
                    passwordCurrent: '',
                    passwordNew: '',
                    passwordNewRetyped: '',
                    activeAlert: { style: style, content: content },
                    requestSent: false
                });
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

    buttonDisabled() {
        if (!this.validInput()) {
            return true;
        }
        return this.state.requestSent;
    }

    buttonText() {
        return this.state.requestSent ? 'Reseting Password...' : 'Reset Password';
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
              {alertBox}
              <TextInput name='Current password'
                         type='password'
                         autoFocus
                         value={this.state.passwordCurrent}
                         handleChange={this.handleChangePasswordCurrent} />
              <PasswordResetInputs
                 password={this.state.passwordNew}
                 passwordRetyped={this.state.passwordNewRetyped}
                 handleChangePassword={this.handleChangePasswordNew}
                 handleChangePasswordRetyped={this.handleChangePasswordNewRetyped} />
              <Button bsStyle="success"
                      className="pull-right"
                      onClick={this.execute}
                      disabled={this.buttonDisabled()}>
                {this.buttonText()}
              </Button>
            </div>
        );
    }
}

module.exports = {
    ResetPassword: ResetPassword
};
