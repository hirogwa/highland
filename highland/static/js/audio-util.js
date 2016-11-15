import React from "react";
import { ControlLabel, Radio, Table } from 'react-bootstrap';

class AudioNone extends React.Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect() {
        this.props.handleSelect(null);
    }

    render() {
        return(
            <tr>
              <td>
                <Radio checked={this.props.selected}
                       onChange={this.handleSelect} />
              </td>
              <td>None</td>
              <td>N/A</td>
              <td>N/A</td>
            </tr>
        );
    }
}

class AudioSingle extends React.Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect() {
        this.props.handleSelect(this.props.audio.id);
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
                <Radio checked={this.props.selected}
                       onChange={this.handleSelect} />
              </td>
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
    constructor(props) {
        super(props);
    }

    render() {
        var rows = [];
        let self = this;
        rows.push(
            <AudioNone key={-1}
                       selected={self.props.selectedId === null}
                       handleSelect={self.props.handleSelect} />
        );
        this.props.audios.forEach(function(audio) {
            rows.push(
                <AudioSingle audio={audio}
                                  key={audio.id}
                                  selected={self.props.selectedId === audio.id}
                                  handleSelect={self.props.handleSelect} />
            );
        });

        return (
            <Table striped bordered condensed hover>
              <thead>
                <tr>
                  <th></th>
                  <th>File</th>
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

class AudioSelector extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            audios: []
        };
    }

    loadAudioData(whitelistedId) {
        const self = this;
        const url = '/audio?unused_only=True' +
                (whitelistedId ? '&whitelisted_id=' + whitelistedId : '');
        this.props.authenticatedRequest.get(url)
            .then((resp) => {
                const data = JSON.parse(resp);
                self.setState({
                    audios: data.audios
                });
            })
            .catch((args) => console.error(args));
    }

    componentDidMount() {
        this.loadAudioData(this.props.whitelistedId);
    }

    componentWillReceiveProps(nextProps) {
        this.loadAudioData(nextProps.whitelistedId);
    }

    render() {
        return (
            <div>
              <ControlLabel>Audio</ControlLabel>
              <AudioList selectedId={this.props.selectedAudioId}
                         audios={this.state.audios}
                         handleSelect={this.props.handleSelect} />
            </div>
        );
    }
}

module.exports = {
    AudioSelector: AudioSelector
};
