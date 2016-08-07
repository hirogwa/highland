import React from "react";
import { Checkbox, Table } from 'react-bootstrap';
import { Deleter, Uploader } from './common.js';

class SingleAudio extends React.Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect(event) {
        this.props.handleSelect(this.props.audio.id, event.target.checked);
    }

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
                <Checkbox checked={this.props.selected}
                          onChange={this.handleSelect} />
              </td>
              <td>
                <a href={this.props.audio.url}>
                  {this.props.audio.filename}
                </a>
              </td>
              <td>{duration}</td>
              <td>{this.props.audio.create_datetime}</td>
              <td>{this.props.audio.guid}</td>
            </tr>
        );
    }
}

class AudioList extends React.Component {
    render() {
        let rows = [];
        let self = this;
        this.props.audios.forEach(function(audio) {
            rows.push(
                <SingleAudio audio={audio} key={audio.id}
                             selected={self.props.selectedIds.indexOf(audio.id) > -1}
                             handleSelect={self.props.handleSelect} />
            );
        });
        return (
            <Table>
              <thead>
                <tr>
                  <th></th>
                  <th>File</th>
                  <th>Duration</th>
                  <th>Created</th>
                  <th>Guid</th>
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
            audios: [],
            selectedIds: []
        };
    },

    handleSelectAudio: function(id, checked) {
        let ids = this.state.selectedIds;
        let index = ids.indexOf(id);
        if (checked) {
            if (index > -1) {
                return;
            }
            ids.push(id);
        } else {
            if (index < 0) {
                return;
            }
            ids.splice(index, 1);
        }

        this.setState({
            selectedIds: ids
        });
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
              <Uploader label="New Audio"
                        url="/audio" />
              <AudioList audios={this.state.audios}
                         selectedIds={this.state.selectedIds}
                         handleSelect={this.handleSelectAudio} />
              <Deleter selectedIds={this.state.selectedIds}
                       url="/audio" />
            </div>
        );
    }
});

module.exports = {
    Audio: App
};
