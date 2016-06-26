import React from "react";
import ReactDOM from "react-dom";
import _ from "underscore";
import { Button, Form, Table, Radio } from 'react-bootstrap';
import { TextArea, TextInput, OptionSelector, ExplicitSelector } from './common.js';

class DraftStatusSelector extends React.Component {
    render() {
        let options = [{
            value: 'draft',
            caption: 'Draft'
        }, {
            value: 'published',
            caption: 'Published'
        }];

        return (
            <OptionSelector name='Draft Status'
                            value={this.props.draftStatus}
                            options={options}
                            handleChange={this.props.handleChange} />
        );
    }
}

class AudioSelectorRow extends React.Component {
    constructor(props) {
        super(props);
        this.handler = this.handler.bind(this);
    }

    handler() {
        this.props.handleChange(this.props.audio.id);
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
                <Radio checked={this.props.selected} onChange={this.handler} />
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

class AudioSelector extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            audios: []
        };
        this.componentDidMount = this.componentDidMount.bind(this);
    }

    componentDidMount() {
        let self = this;
        let xhr = new XMLHttpRequest();
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
    }

    render() {
        var rows = [];
        let self = this;
        this.state.audios.forEach(function(audio) {
            rows.push(
                <AudioSelectorRow audio={audio}
                                  key={audio.id}
                                  selected={self.props.selectedId === audio.id}
                                  handleChange={self.props.handleChange} />
            );
        });
        return (
            <Table condensed={this.props.condensed}>
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

var Mode = {
    UPDATE: 'update',
    CREATE: 'create'
};

var App = React.createClass({
    getInitialState: function() {
        return {
            episode: {
                title: '',
                subtitle: '',
                description: '',
                audio_id: -1,
                image_id: -1,
                draft_status: '',
                scheduled_datetime: '',
                explicit: false,
                alias: ''
            }
        };
    },

    handleChangeTitle: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {title: event.target.value})
        });
    },

    handleChangeSubtitle: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {subtitle: event.target.value})
        });
    },

    handleChangeDescription: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {description: event.target.value})
        });
    },

    handleChangeAlias: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {alias: event.target.value})
        });
    },

    handleChangeExplicit: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {explicit: event.target.value === 'yes'})
        });
    },

    handleChangeAudioId: function(audioId) {
        this.setState({
            episode: _.extend(this.state.episode, {audio_id: audioId})
        });
    },

    handleChangeDraftStatus: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {draft_status: event.target.value})
        });
    },

    componentDidMount: function() {
        var self = this;
        if (this.props.mode === Mode.UPDATE) {
            let xhr = new XMLHttpRequest();
            let url = '/episode/{s}/{e}'
                    .replace('{s}', this.props.showId)
                    .replace('{e}', this.props.episodeId);
            xhr.open('get', url, true);
            xhr.onload = function() {
                if (this.status == 200) {
                    let data = JSON.parse(this.response);
                    self.setState({
                        episode: data.episode
                    });
                } else {
                    console.error(this.statusText);
                }
            };
            xhr.send();
        }
    },

    saveEpisode: function() {
        let xhr = new XMLHttpRequest();
        xhr.open(this.props.mode == Mode.UPDATE ? 'put' : 'post', '/episode', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onload = function() {
            let data = JSON.parse(this.response);
            if (this.status == 200) {
                console.info(data);
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send(
            JSON.stringify(_.extend(this.state.episode, {show_id: this.props.showId}))
        );
    },

    render: function() {
        return (
            <Form>
              <TextInput name='Title'
                         value={this.state.episode.title}
                         handleChange={this.handleChangeTitle} />
              <TextInput name='Subtitle'
                         value={this.state.episode.subtitle}
                         handleChange={this.handleChangeSubtitle} />
              <TextArea name='Description'
                        value={this.state.episode.description}
                        handleChange={this.handleChangeDescription} />
              <TextInput name='Alias'
                         value={this.state.episode.alias}
                         handleChange={this.handleChangeAlias} />
              <ExplicitSelector explicit={this.state.episode.explicit}
                                handleChange={this.handleChangeExplicit} />
              <DraftStatusSelector draftStatus={this.state.episode.draft_status}
                                   handleChange={this.handleChangeDraftStatus} />
              <AudioSelector condensed={true}
                             selectedId={this.state.episode.audio_id}
                             handleChange={this.handleChangeAudioId} />
              <Button bsStyle="primary" onClick={this.saveEpisode}>Save</Button>
            </Form>
        );
    }
});

ReactDOM.render(<App showId={showId} episodeId={episodeId} mode={mode} />,
                document.querySelector(".mainContainer"));
