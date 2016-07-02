import React from "react";
import { ControlLabel, FormControl, FormGroup } from 'react-bootstrap';

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

class Image extends React.Component {
    constructor(props) {
        super(props);
        this.state = {url: ''};
        this.componentWillReceiveProps = this.componentWillReceiveProps.bind(this);
    }

    componentWillReceiveProps(nextProps) {
        if (this.props.imageId === nextProps.imageId) {
            return;
        }

        let self = this;
        let xhr = new XMLHttpRequest();
        xhr.open('get', '/image/' + nextProps.imageId, true);
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                self.setState({
                    url: data.image.url
                });
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send();
    }

    render() {
        return (
            <div>
              <img src={this.state.url} className="img-thumbnail"/>
            </div>
        );
    }
}

module.exports = {
    TextInput: TextInput,
    TextArea: TextArea,
    OptionSelector: OptionSelector,
    ExplicitSelector: ExplicitSelector,
    Image: Image
};