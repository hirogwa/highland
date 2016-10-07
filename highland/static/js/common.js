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
    render() {
        return (
            <FormGroup>
              <ControlLabel>{this.props.name}</ControlLabel>
              <FormControl type="text" placeholder="Enter text"
                           value={this.props.value}
                           onChange={this.props.handleChange}
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
            file: ''
        };
        this.handleFileChange = this.handleFileChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleFileChange(event) {
        this.setState({
            file: event.target.files[0]
        });
    }

    handleSubmit(){
        return new Promise((resolve, reject) => {
            let formData = new FormData();
            formData.append('file', this.state.file);

            var xhr = new XMLHttpRequest();
            xhr.open('post', this.props.url, true);
            xhr.onload = function() {
                if (this.status == 201) {
                    resolve(this.response);
                } else {
                    reject(this.statusText);
                }
            };
            xhr.send(formData);
        });
    }

    render() {
        return (
            <Form>
              <FormGroup controlId="formControlsFile">
                <ControlLabel>{this.props.label}</ControlLabel>
                <FormControl type="file" onChange={this.handleFileChange} />
                <Button type="submit" onClick={this.handleSubmit}
                        disabled={!this.state.file}>
                  Upload
                </Button>
              </FormGroup>
            </Form>
        );
    }
}

class Deleter extends React.Component {
    constructor(props) {
        super(props);
        this.handleDelete = this.handleDelete.bind(this);
    }

    handleDelete() {
        let xhr = new XMLHttpRequest();
        xhr.open('delete', this.props.url, true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                console.info(data);
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send(
            JSON.stringify({ids: this.props.selectedIds})
        );
    }

    render() {
        return (
            <Form>
              <Button bsStyle="danger" onClick={this.handleDelete}
                      type="submit"
                      disabled={this.props.selectedIds.length < 1}>
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
                <Alert bsStyle={this.props.style} onDismiss={this.handleAlertDismiss}>
                  <p>{this.props.content}</p>
                </Alert>
            );
        } else {
            return (<div></div>);
        }
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
    NavLink: NavLink
};
