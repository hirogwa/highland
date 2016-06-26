import React from "react";
import ReactDOM from "react-dom";
import { Button, ControlLabel, Form, FormControl, FormGroup, HelpBlock, Table } from 'react-bootstrap';

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
        this.state.file = event.target.files[0];
    }

    handleSubmit(){
        return new Promise((resolve, reject) => {
            let formData = new FormData();
            formData.append('file', this.state.file);

            var xhr = new XMLHttpRequest();
            xhr.open('post', '/audio', true);
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
                <ControlLabel>New audio</ControlLabel>
                <FormControl type="file" onChange={this.handleFileChange} />
                <HelpBlock>Upload new file here.</HelpBlock>
                <Button type="submit" onClick={this.handleSubmit}>
                  Upload
                </Button>
              </FormGroup>
              {this.state.previewUrl}
            </Form>
        );
    }
}

class SingleAudio extends React.Component {
    render() {
        var hours = parseInt(this.props.audio.duration / 3600, 10);
        var minutes = parseInt(this.props.audio.duration / 60, 10);
        var seconds = parseInt(this.props.audio.duration % 60, 10);
        var duration = "h:m:s".replace('h', hours)
                .replace('m', minutes < 10 ? '0' + minutes : minutes)
                .replace('s', seconds < 10 ? '0' + seconds : seconds);
        return (
            <tr>
              <td>
                <a href={this.props.audio.url}>
                  {this.props.audio.filename}
                </a>
              </td>
              <td>{duration}</td>
              <td>{this.props.audio.create_datetime}</td>
            </tr>
        );
    }
}

class AudioList extends React.Component {
    render() {
        var rows = [];
        this.props.audios.forEach(function(audio) {
            rows.push(<SingleAudio audio={audio} key={audio.id} />);
        });
        return (
            <Table>
              <thead>
                <tr>
                  <th></th>
                  <th>Duration</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {rows}
              </tbody>
            </Table>
        );
    }
}

var App = React.createClass({
    getInitialState: function() {
        return {
            audios: []
        };
    },

    componentDidMount: function() {
        var self = this;
        var xhr = new XMLHttpRequest();
        xhr.open('get', '/audio', true);
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                self.setState({
                    audios: data.audios
                });
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send();
    },

    render: function() {
        return (
            <div>
              <Uploader />
              <AudioList audios={this.state.audios}/>
            </div>
        );
    }
});

ReactDOM.render(<App/>,
                document.querySelector(".mainContainer"));
