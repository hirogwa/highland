import React from "react";
import ReactDOM from "react-dom";
import _ from "underscore";
import { Button, Form } from 'react-bootstrap';
import { TextArea, TextInput, OptionSelector, ExplicitSelector } from './common.js';
import { ImageSelector } from './image-util.js';
import { AudioSelector } from './audio-util.js';

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
                audio_id: null,
                image_id: -1,
                draft_status: 'draft',
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

    handleSelectAudio: function(id) {
        this.setState({
            episode: _.extend(this.state.episode, {audio_id: id})
        });
    },

    handleSelectImage: function(id) {
        this.setState({
            episode: _.extend(this.state.episode, {image_id: id})
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
            if (this.status == 200 || 201) {
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
              <AudioSelector selectedAudioId={this.state.episode.audio_id}
                             handleSelect={this.handleSelectAudio} />
              <ImageSelector selectedImageId={this.state.episode.image_id}
                             handleSelect={this.handleSelectImage} />
              <Button bsStyle="primary" onClick={this.saveEpisode}>Save</Button>
            </Form>
        );
    }
});

ReactDOM.render(<App showId={showId} episodeId={episodeId} mode={mode} />,
                document.querySelector(".mainContainer"));
