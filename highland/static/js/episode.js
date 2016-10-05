import React from "react";
import _ from "underscore";
import { Button, ButtonToolbar, Form } from 'react-bootstrap';
import { TextArea, TextInput, OptionSelector, ExplicitSelector, AlertBox } from './common.js';
import { ImageSelector } from './image-util.js';
import { AudioSelector } from './audio-util.js';
import { episodePath } from './paths';

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
            originalEpisodeId: null,
            episode: {
                title: '',
                subtitle: '',
                description: '',
                audio_id: null,
                image_id: null,
                draft_status: 'draft',
                scheduled_datetime: '',
                explicit: false,
                alias: ''
            },
            modified: false,
            activeAlert: null
        };
    },

    handleChangeTitle: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {title: event.target.value}),
            modified: true
        });
    },

    handleChangeSubtitle: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {subtitle: event.target.value}),
            modified: true
        });
    },

    handleChangeDescription: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {description: event.target.value}),
            modified: true
        });
    },

    handleChangeAlias: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {alias: event.target.value}),
            modified: true
        });
    },

    handleChangeExplicit: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {explicit: event.target.value === 'yes'}),
            modified: true
        });
    },

    handleChangeAudioId: function(audioId) {
        this.setState({
            episode: _.extend(this.state.episode, {audio_id: audioId}),
            modified: true
        });
    },

    handleChangeDraftStatus: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {draft_status: event.target.value}),
            modified: true
        });
    },

    handleSelectAudio: function(id) {
        this.setState({
            episode: _.extend(this.state.episode, {audio_id: id}),
            modified: true
        });
    },

    handleSelectImage: function(id) {
        this.setState({
            episode: _.extend(this.state.episode, {image_id: id}),
            modified: true
        });
    },

    componentDidMount: function() {
        var self = this;
        if (this.props.route.mode === Mode.UPDATE) {
            let xhr = new XMLHttpRequest();
            let url = '/episode/{s}/{e}'
                    .replace('{s}', this.props.route.showId)
                    .replace('{e}', this.props.routeParams.episodeId);
            xhr.open('get', url, true);
            xhr.onload = function() {
                if (this.status == 200) {
                    let data = JSON.parse(this.response);
                    self.setEpisode(data);
                } else {
                    console.error(this.statusText);
                }
            };
            xhr.send();
        }
    },

    setEpisode: function(data) {
        this.setState({
            originalEpisodeId: data.episode.audio_id,
            episode: data.episode,
            modified: false
        });
    },

    contextTypes: {
        router: React.PropTypes.object.isRequired
    },

    saveEpisode: function() {
        let self = this;
        let xhr = new XMLHttpRequest();
        xhr.open(this.props.route.mode == Mode.UPDATE ? 'put' : 'post', '/episode', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onload = function() {
            let data = JSON.parse(this.response);
            if (this.status == 200 || this.status == 201) {
                console.info(data);
                self.setEpisode(data);
                self.context.router.replace(episodePath(data.episode.id));
                self.setState({
                    modified: false,
                    activeAlert: {
                        style: 'success',
                        content: 'Saved! :D'
                    }
                });
            } else {
                self.setState({
                    activeAlert: {
                        style: 'danger',
                        content: 'Oops! Something went wrong. :('
                    }
                });
            }
        };
        xhr.send(
            JSON.stringify(_.extend(this.state.episode, {show_id: this.props.route.showId}))
        );
    },

    previewUrl: function() {
        let e = this.state.episode;
        let p = function(attr) {
            return '&' +
                (e[attr] === null ? '' : attr + '=' + encodeURIComponent(e[attr]));
        };

        return '/preview/site/?show_id=' + this.props.route.showId
            + p('title')
            + p('subtitle')
            + p('description')
            + p('audio_id')
            + p('image_id');
    },

    savable: function() {
        return this.state.modified || this.props.route.mode == Mode.CREATE;
    },

    render: function() {
        let alertBox = <div></div>;
        if (this.state.activeAlert) {
            alertBox = <AlertBox
            style={this.state.activeAlert.style}
            content={this.state.activeAlert.content} />;
        }
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
                             whitelistedId={this.state.originalEpisodeId}
                             handleSelect={this.handleSelectAudio} />
              <ImageSelector selectedImageId={this.state.episode.image_id}
                             handleSelect={this.handleSelectImage} />
              {alertBox}
              <ButtonToolbar>
                <Button bsStyle="default"
                        target="_blank"
                        href={this.previewUrl()}>
                  Preview
                </Button>
                <Button bsStyle="primary"
                        onClick={this.saveEpisode}
                        disabled={!this.savable()}>
                  Save
                </Button>
              </ButtonToolbar>
            </Form>
        );
    }
});

module.exports = {
    Episode: App
};
