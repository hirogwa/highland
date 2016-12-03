import React from "react";
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
            requestProcessing: false
        };
    }

    execute() {
        this.setState({ requestProcessing: true });

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
                    requestProcessing: false
                });
            });
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

    buttonText() {
        return this.state.requestProcessing ? 'Reseting Password...' : 'Reset Password';
    }

    customRequirements() {
        return [{
            statement: 'New password must be different from current password',
            passed: () => this.state.passwordNew
                && this.state.passwordCurrent
                && this.state.passwordCurrent !== this.state.passwordNew
        }];
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
                 buttonText={this.buttonText()}
                 customRequirements={this.customRequirements()}
                 password={this.state.passwordNew}
                 passwordRetyped={this.state.passwordNewRetyped}
                 processing={this.state.requestProcessing}
                 handleChangePassword={this.handleChangePasswordNew}
                 handleChangePasswordRetyped={this.handleChangePasswordNewRetyped}
                 handleSubmit={this.execute} />
            </div>
        );
    }
}

module.exports = {
    ResetPassword: ResetPassword
};
