import React from "react";
import { Checkbox, Table } from 'react-bootstrap';
import { NavLink } from './common.js';
import { getAudioSeconds } from './audio-util.js';
import { Media } from './media.js';

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

        var episodeLink = 'N/A';
        var checkBox = <span></span>;
        if (this.props.audio.episode_id) {
            episodeLink = (
                <NavLink to={'/episode/' + this.props.audio.episode_id}>
                  {this.props.audio.episode_title}
                </NavLink>);
        } else {
            checkBox = (
                <Checkbox checked={this.props.selected}
                          onChange={this.handleSelect} />
            );
        }

        return (
            <tr>
              <td>{checkBox}</td>
              <td>
                <a href={this.props.audio.url}>
                  {this.props.audio.filename}
                </a>
              </td>
              <td>{duration}</td>
              <td>{this.props.audio.create_datetime}</td>
              <td>{episodeLink}</td>
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
                  <th>Episode</th>
                </tr>
              </thead>
              <tbody>
                {rows}
              </tbody>
            </Table>
        );
    }
}

class Audio extends React.Component {
    constructor(props) {
        super(props);
        this.handleUpload = this.handleUpload.bind(this);
        this.handleSelectAudio = this.handleSelectAudio.bind(this);
        this.reloadAudioList = this.reloadAudioList.bind(this);
        this.state = {
            audios: [],
            selectedIds: []
        };
    }

    handleSelectAudio(id, checked) {
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
    }

    reloadAudioList() {
        return this.props.route.authenticatedRequest.get('/audio')
            .then(data => this.setState({
                audios: data.audios
            }))
            .catch((args) => console.error(args));
    }

    componentDidMount() {
        return this.reloadAudioList();
    }

    handleUpload(file, type) {
        const authReq = this.props.route.authenticatedRequest;
        return getAudioSeconds(file)
            .then(second => authReq.post('/audio', {
                filename: file.name,
                filetype: type,
                duration: second,
                length: file.size
            }))
            .then(response => authReq.postAudio(
                file, response.audio.guid, type));
    }

    render() {
        const audioList = (
              <AudioList audios={this.state.audios}
                         selectedIds={this.state.selectedIds}
                         handleSelect={this.handleSelectAudio} />
        );

        return (
            <Media selectedIds={this.state.selectedIds}
                   url="/audio"
                   authenticatedRequest={this.props.route.authenticatedRequest}
                   uploaderLabel="New Audio"
                   handleUpload={this.handleUpload}
                   mediaList={audioList}
                   reloadList={this.reloadAudioList}
                   />
        );
    }
}

module.exports = {
    Audio: Audio
};
