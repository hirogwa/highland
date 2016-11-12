import React from "react";
import _ from "underscore";
import { Button, ButtonToolbar, Form, Modal, Radio } from 'react-bootstrap';
import { TextArea, TextInput, ExplicitSelector, AlertBox } from './common.js';
import { ImageSelector } from './image-util.js';
import { AudioSelector } from './audio-util.js';
import { episodePath } from './paths';
import { Texts } from './constants.js';
import Datetime from 'react-datetime';
import moment from 'moment';

const DraftStatus = {
    DRAFT: 'draft',
    PUBLISHED: 'published',
    SCHEDULED: 'scheduled'
};

const Mode = {
    UPDATE: 'update',
    CREATE: 'create'
};

const defaultScheduledDatetime = new Date().toISOString();

class SaveModal extends React.Component {
    constructor(props) {
        super(props);
        this.handleSetScheduledDatetime = this.handleSetScheduledDatetime.bind(this);
        this.handleExecute = this.handleExecute.bind(this);
    }

    handleSetScheduledDatetime(e) {
        this.props.handleSelect(DraftStatus.SCHEDULED, e.toISOString());
    }

    handleExecute() {
        this.props.handleSave();
        this.props.handleHide();
    }

    canExecute() {
        return this.props.draftStatus === DraftStatus.DRAFT
            || (this.props.draftStatus === DraftStatus.PUBLISHED && this.props.canPublish)
            || (this.props.draftStatus === DraftStatus.SCHEDULED && this.props.canSchedule);
    }

    render() {
        return (
            <Modal show={this.props.showModal} onHide={this.props.handleHide}>
              <Modal.Header>
                <Modal.Title>Save options</Modal.Title>
              </Modal.Header>
              <Modal.Body>
                <Radio checked={this.props.draftStatus === DraftStatus.DRAFT}
                       onChange={() => this.props.handleSelect(DraftStatus.DRAFT)}>
                  Draft
                </Radio>
                <Radio checked={this.props.draftStatus === DraftStatus.PUBLISHED}
                       disabled={!this.props.canPublish}
                       onChange={() => this.props.handleSelect(DraftStatus.PUBLISHED)}>
                  Publish right away
                </Radio>
                <Radio checked={this.props.draftStatus === DraftStatus.SCHEDULED}
                       disabled={!this.props.canSchedule}
                       onChange={() => this.props.handleSelect(DraftStatus.SCHEDULED)}>
                  Schedule to publish at
                </Radio>
                <Datetime value={new Date(this.props.scheduledDatetime)}
                          inputProps={{disabled: !this.props.canSchedule}}
                          onChange={this.handleSetScheduledDatetime} />
              </Modal.Body>
              <Modal.Footer>
                  <Button bsStyle="primary"
                          onClick={this.handleExecute}
                          disabled={!this.canExecute()}>
                    Save
                  </Button>
                  <Button bsStyle="default"
                          onClick={this.props.handleHide}>
                    Cancel
                  </Button>
              </Modal.Footer>
            </Modal>
        );
    }
}

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
                draft_status: this.props.route.mode === Mode.CREATE ? DraftStatus.DRAFT : '',
                scheduled_datetime: defaultScheduledDatetime,
                explicit: false,
                alias: ''
            },
            savedDraftStatus: '',
            modified: false,
            activeAlert: null,
            showPublishModal: false
        };
    },

    handleChangeTitle: function(text) {
        this.setState({
            episode: _.extend(this.state.episode, {title: text}),
            modified: true
        });
    },

    handleChangeSubtitle: function(text) {
        this.setState({
            episode: _.extend(this.state.episode, {subtitle: text}),
            modified: true
        });
    },

    handleChangeDescription: function(event) {
        this.setState({
            episode: _.extend(this.state.episode, {description: event.target.value}),
            modified: true
        });
    },

    handleChangeAlias: function(text) {
        this.setState({
            episode: _.extend(this.state.episode, {alias: text}),
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

    handleAlertDismiss: function() {
        this.setState({
            activeAlert: null
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
            savedDraftStatus: data.episode.draft_status,
            modified: false
        });
        if (!this.state.episode.scheduled_datetime) {
            this.setState({
                episode: _.extend(this.state.episode, {
                    scheduled_datetime: defaultScheduledDatetime
                })
            });
        }
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
                        content: Texts.NOTIFY_SAVED
                    }
                });
            } else {
                self.setState({
                    activeAlert: {
                        style: 'danger',
                        content: Texts.NOTIFY_ERROR
                    }
                });
            }
        };

        if (this.state.episode.draft_status != DraftStatus.SCHEDULED) {
            this.setState({
                episode: _.extend(this.state.episode, {scheduled_datetime: ''}),
                modified: true
            });
        }
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

    canPublish: function() {
        return this.state.episode.title
            && this.state.episode.description
            && this.state.episode.audio_id;
    },

    canSchedule: function() {
        return this.canPublish();
    },

    render: function() {
        let alertBox = <div></div>;
        if (this.state.activeAlert) {
            alertBox = (
                <AlertBox
                   style={this.state.activeAlert.style}
                   content={this.state.activeAlert.content}
                   handleAlertDismiss={this.handleAlertDismiss} />
            );
        }

        let alertDraftStatus;
        if (this.state.savedDraftStatus === DraftStatus.DRAFT) {
            alertDraftStatus = (
                <AlertBox style="warning"
                          content={Texts.EPISODE_STATUS_STATEMENT_DRAFT}
                          nondismissible={true} />
            );
        } else if (this.state.savedDraftStatus === DraftStatus.PUBLISHED) {
            alertDraftStatus = (
                <AlertBox style="info"
                          content={Texts.EPISODE_STATUS_STATEMENT_PUBLISHED}
                          nondismissible={true} />
            );
        } else if (this.state.savedDraftStatus === DraftStatus.SCHEDULED) {
            const statement = '{0} {1}'
                      .replace('{0}', Texts.EPISODE_STATUS_STATEMENT_SCHEDULED)
                      .replace('{1}', moment(this.state.episode.scheduled_datetime)
                               .format('MMMM Do YYYY, h:mm a'));
            alertDraftStatus = (
                <AlertBox style="info"
                          content={statement}
                          nondismissible={true} />
            );
        }

        const self = this;
        const handleModalSelect = function(status, scheduledDatetime) {
            self.setState({
                episode: _.extend(self.state.episode, {
                    draft_status: status,
                    scheduled_datetime: scheduledDatetime
                        || self.state.episode.scheduled_datetime
                })
            });
        };

        return (
            <div className="container">
              {alertDraftStatus}
              {alertBox}
              <ButtonToolbar>
                <Button bsStyle="primary"
                        onClick={() => {this.setState({showPublishModal: true});}}>
                  Save...
                </Button>
                <Button bsStyle="default"
                        target="_blank"
                        className="pull-right"
                        href={this.previewUrl()}>
                  Preview
                </Button>
              </ButtonToolbar>
              <hr />

              <Form>
                <h3>Required</h3>
                <TextInput name='Title'
                           value={this.state.episode.title}
                           handleChange={this.handleChangeTitle} />
                <TextArea name='Description'
                          value={this.state.episode.description}
                          handleChange={this.handleChangeDescription} />
                <AudioSelector selectedAudioId={this.state.episode.audio_id}
                               whitelistedId={this.state.originalEpisodeId}
                               handleSelect={this.handleSelectAudio} />
                <hr />

                <h3>Optional</h3>
                <TextInput name='Subtitle'
                           value={this.state.episode.subtitle}
                           handleChange={this.handleChangeSubtitle} />
                <TextInput name='Alias'
                           value={this.state.episode.alias}
                           handleChange={this.handleChangeAlias} />
                <ExplicitSelector explicit={this.state.episode.explicit}
                                  handleChange={this.handleChangeExplicit} />
                <ImageSelector selectedImageId={this.state.episode.image_id}
                               handleSelect={this.handleSelectImage} />
                <hr />
              </Form>

              <SaveModal showModal={this.state.showPublishModal}
                         draftStatus={this.state.episode.draft_status}
                         scheduledDatetime={this.state.episode.scheduled_datetime}
                         canPublish={this.canPublish()}
                         canSchedule={this.canSchedule()}
                         handleSave={this.saveEpisode}
                         handleSelect={handleModalSelect}
                         handleHide={() => {this.setState({showPublishModal: false});}}/>
            </div>
        );
    }
});

module.exports = {
    Episode: App
};
