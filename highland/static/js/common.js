import React from "react";
import {
    Alert, Button, ControlLabel, Form, FormControl, FormGroup
} from 'react-bootstrap';
import { Link } from 'react-router';

class OptionSelector extends React.Component {
    render() {
        let options = [];
        this.props.options.forEach(function(op) {
            options.push(
                <option value={op.value} key={op.value}>{op.caption}</option>
            );
        });
        return (
            <FormGroup controlId="formControlsExplicitSelect">
              <ControlLabel>{this.props.name}</ControlLabel>
              <FormControl componentClass="select" placeholder="select"
                           value={this.props.value}
                           onChange={this.props.handleChange}>
                {options}
              </FormControl>
            </FormGroup>
        );
    }
}

class ExplicitSelector extends React.Component {
    render() {
        let options = [{
            value: 'yes',
            caption: 'Yes'
        }, {
            value: 'no',
            caption: 'No'
        }];

        return (
            <OptionSelector name='Explicit'
                            value={this.props.explicit ? 'yes' : 'no'}
                            options={options}
                            handleChange={this.props.handleChange} />
        );
    }
}

class TextInput extends React.Component {
    constructor(props) {
        super(props);
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        this.props.handleChange(e.target.value);
    }

    render() {
        return (
            <FormGroup>
              <ControlLabel>{this.props.name}</ControlLabel>
              <FormControl type={this.props.type || "text"}
                           placeholder="Enter text"
                           disabled={this.props.disabled}
                           autoFocus={this.props.autoFocus}
                           value={this.props.value}
                           onChange={this.handleChange}
                           />
            </FormGroup>
        );
    }
}

class TextArea extends React.Component {
    render() {
        return (
            <FormGroup>
              <ControlLabel>{this.props.name}</ControlLabel>
              <FormControl componentClass="textarea" placeholder="Enter text"
                           value={this.props.value}
                           onChange={this.props.handleChange}
                           />
            </FormGroup>
        );
    }
}

class Uploader extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            file: null,
            formKey: 1,
            uploading: false
        };
        this.handleFileChange = this.handleFileChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleFileChange(event) {
        let file = event.target.files[0];
        getMimeType(file)
            .then(t => {
                this.setState({
                    file: file,
                    type: t
                });
            })
            .catch(e => console.error(e));
    }

    handleSubmit(){
        this.setState({ uploading: true });
        return this.props.handleSubmit(this.state.file, this.state.type)
            .then(() => this.setState({
                file: null,
                formKey: this.state.formKey + 1,
                uploading: false
            }));
    }

    uploadable() {
        return this.state.file && !this.state.uploading;
    }

    render() {
        return (
            <Form>
              <FormGroup controlId="formControlsFile">
                <ControlLabel>{this.props.label}</ControlLabel>
                <FormControl type="file"
                             key={this.state.formKey}
                             onChange={this.handleFileChange} />
                <Button onClick={this.handleSubmit}
                        disabled={!this.uploadable()}>
                  Upload
                </Button>
              </FormGroup>
            </Form>
        );
    }
}

const HEADER_TO_MIME = {
    '89504e': 'image/png',
    'ffd8ff': 'image/jpeg',
    '494433': 'audio/mpeg'
};

function getMimeType(file) {
    return new Promise((resolve, reject) => {
        let reader = new window.FileReader();
        reader.onloadend = function(e) {
            const arr = new Uint8Array(e.target.result).subarray(0, 3);
            let header = '';
            arr.forEach(x => header += x.toString(16));

            let result = HEADER_TO_MIME[header];
            if (!result) {
                console.warn('MIME not identified. Naively falling back to type info from file object');
                result = file.type;
            }
            resolve(result);
        };
        reader.readAsArrayBuffer(file);
    });
}

function executeIfDefined(func, args) {
    if (func) {
        func.apply(this, args);
    }
}

class Deleter extends React.Component {
    constructor(props) {
        super(props);
        this.handleDelete = this.handleDelete.bind(this);
        this.state = {
            deleting: false
        };
    }

    handleDelete() {
        executeIfDefined(this.props.onDeleting);
        this.setState({
            deleting: true
        });

        this.props.authenticatedRequest.delete(
            this.props.url, {ids: this.props.selectedIds})
            .then(() => {
                executeIfDefined(this.props.onDeleted);
                this.setState({
                    deleting: true
                });
            })
            .catch(e => {
                console.error(e);
                executeIfDefined(this.props.onDeletionFailed);
            });
    }

    deletable() {
        if (this.props.selectedIds.length < 1) {
            return false;
        }
        return !this.state.deleting;
    }

    render() {
        return (
            <Form>
              <Button bsStyle="danger"
                      onClick={this.handleDelete}
                      className={this.props.className}
                      disabled={!this.deletable()}>
                      Delete Selected
              </Button>
            </Form>
        );
    }
}

class AlertBox extends React.Component {
    constructor(props) {
        super(props);
        this.handleAlertDismiss =
            props.nondismissible ? undefined : this.handleAlertDismiss.bind(this);
        this.state = {
            alertVisible: true
        };
    }

    handleAlertDismiss() {
        this.setState({
            alertVisible: false
        });
        this.props.handleAlertDismiss();
    }

    render() {
        if (this.state.alertVisible) {
            return (
                <Alert bsStyle={this.props.style || 'info'}
                       onDismiss={this.handleAlertDismiss}>
                  <p>{this.props.content}</p>
                </Alert>
            );
        } else {
            return (<div></div>);
        }
    }
}

class PasswordResetRequirement extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const className = this.props.passed ? 'text-success' : 'text-danger';
        const text = `${this.props.text}${this.props.passed ? ' - ok!' : ''}`;
        return (
            <div>
              <i className={className}>{text}</i>
            </div>
        );
    }
}

class PasswordResetInputs extends React.Component {
    constructor(props) {
        super(props);
    }

    buttonEnabled() {
        if (this.props.processing) {
            return false;
        }
        return this.requirements().concat(
            this.props.customRequirements || [])
            .every(x => x.passed());
    }

    requirements() {
        return [{
            statement: 'New password must be at least 6 characters long',
            passed: () => this.props.password.length >= 6
        }, {
            statement: 'New passwords need to match',
            passed: () => this.props.password &&
                this.props.password === this.props.passwordRetyped
        }];
    }

    render() {
        const requirementTrackers = this.requirements().concat(
            this.props.customRequirements || [])
                  .map((x, i) => (
                      <li key={i}>
                        <PasswordResetRequirement text={x.statement}
                                                  passed={x.passed()} />
                      </li>
                  ));

        return (
            <div>
              <TextInput name='New password'
                         type='password'
                         autoFocus={this.props.autoFocus}
                         value={this.props.password}
                         handleChange={this.props.handleChangePassword} />
              <TextInput name='New password again'
                         type='password'
                         value={this.props.passwordRetyped}
                         handleChange={this.props.handleChangePasswordRetyped} />
              <ul>
                {requirementTrackers}
              </ul>
              <Button bsStyle="success"
                      onClick={this.props.handleSubmit}
                      disabled={!this.buttonEnabled()}>
                {this.props.buttonText}
              </Button>
            </div>
        );
    }
}

class NavLink extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <Link {...this.props} activeClassName="active"/>;
    }
}

module.exports = {
    TextInput: TextInput,
    TextArea: TextArea,
    OptionSelector: OptionSelector,
    ExplicitSelector: ExplicitSelector,
    Uploader: Uploader,
    Deleter: Deleter,
    AlertBox: AlertBox,
    PasswordResetInputs: PasswordResetInputs,
    NavLink: NavLink
};
