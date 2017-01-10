import React from "react";
import _ from "underscore";
import { Button, Form } from 'react-bootstrap';
import {
    TextArea, TextInput, OptionSelector, ExplicitSelector, AlertBox
} from './common.js';
import { ImageSelector } from './image-util.js';

class CategorySelector extends React.Component {
    render() {
        let options = [{
            value: 'Arts',
            caption: 'Arts'
        }, {
            value: 'Technology',
            caption: 'Technology'
        }];

        return (
            <OptionSelector name='Category'
                            value={this.props.category}
                            options={options}
                            handleChange={this.props.handleChange} />
        );
    }
}

class LanguageSelector extends React.Component {
    render() {
        let options = [{
            value: 'en-US',
            caption: 'English(US)'
        }, {
            value: 'ja',
            caption: 'Japanese'
        }];

        return (
            <OptionSelector name='Language'
                            value={this.props.language}
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
            show: {
                title: '',
                description: '',
                subtitle: '',
                language: '',
                author: '',
                category: '',
                explicit: false,
                alias: '',
                image_id: null
            },
            modified: false,
            activeAlert: null
        };
    },

    componentDidMount: function() {
        if (this.props.route.mode == Mode.UPDATE) {
            const self = this;
            this.props.route.authenticatedRequest
                .get(`/show/${this.props.route.showId}`)
                .then((resp) => {
                    const data = JSON.parse(resp);
                    self.setState({
                        show: data.show
                    });
                })
                .catch((args) => console.error(args));
        }
    },

    handleChangeTitle: function(text) {
        this.setState({
            show: _.extend(this.state.show, {title: text}),
            modified: true
        });
    },

    handleChangeDescription: function(event) {
        this.setState({
            show: _.extend(this.state.show, {description: event.target.value}),
            modified: true
        });
    },

    handleChangeSubtitle: function(text) {
        this.setState({
            show: _.extend(this.state.show, {subtitle: text}),
            modified: true
        });
    },

    handleChangeLanguage: function(event) {
        this.setState({
            show: _.extend(this.state.show, {language: event.target.value}),
            modified: true
        });
    },

    handleChangeAuthor: function(text) {
        this.setState({
            show: _.extend(this.state.show, {author: text}),
            modified: true
        });
    },

    handleChangeCategory: function(event) {
        this.setState({
            show: _.extend(this.state.show, {category: event.target.value}),
            modified: true
        });
    },

    handleChangeExplicit: function(event) {
        this.setState({
            show: _.extend(this.state.show, {explicit: event.target.value === 'yes'}),
            modified: true
        });
    },

    handleChangeAlias: function(text) {
        this.setState({
            show: _.extend(this.state.show, {alias: text}),
            modified: true
        });
    },

    handleSelectImage: function(id) {
        this.setState({
            show: _.extend(this.state.show, {image_id: id}),
            modified: true
        });
    },

    saveShow: function() {
        this.setState({
            activeAlert: {
                style: 'info',
                content: 'Saving...'
            }
        });

        const req = this.props.route.authenticatedRequest;
        const func = this.props.route.mode === Mode.UPDATE ?
                  (url, data) => req.put(url, data) :
                  (url, data) => req.post(url, data);

        const self = this;
        func('/show', this.state.show)
            .then(() => {
                self.setState({
                    modified: false,
                    activeAlert: {
                        style: 'success',
                        content: 'Saved! :D'
                    }
                });
            })
            .catch(() => self.setState({
                activeAlert: {
                    style: 'danger',
                    content: 'Oops! Something went wrong. :('
                }
            }));
    },

    savable: function() {
        return this.state.modified || this.props.route.mode == Mode.CREATE;
    },

    handleAlertDismiss: function() {
        this.setState({
            activeAlert: null
        });
    },

    render: function() {
        let alertBox = <div></div>;
        if (this.state.activeAlert) {
            alertBox = <AlertBox
            handleAlertDismiss={this.handleAlertDismiss}
            style={this.state.activeAlert.style}
            content={this.state.activeAlert.content} />;
        }
        return (
            <div>
              {alertBox}
              <Button bsStyle="primary"
                      onClick={this.saveShow}
                      disabled={!this.savable()}>
                Save
              </Button>
              <hr />

              <Form>
                <TextInput name='Alias'
                           value={this.state.show.alias}
                           disabled={this.props.route.mode != Mode.CREATE}
                           handleChange={this.handleChangeAlias} />
                <TextInput name='Title'
                           value={this.state.show.title}
                           handleChange={this.handleChangeTitle} />
                <TextArea name='Description'
                          value={this.state.show.description}
                          handleChange={this.handleChangeDescription} />
                <TextInput name='Subtitle'
                           value={this.state.show.subtitle}
                           handleChange={this.handleChangeSubtitle} />
                <LanguageSelector language={this.state.show.language}
                                  handleChange={this.handleChangeLanguage}
                                  />
                <TextInput name='Author'
                           value={this.state.show.author}
                           handleChange={this.handleChangeAuthor} />
                <CategorySelector category={this.state.show.category}
                                  handleChange={this.handleChangeCategory}
                                  />
                <ExplicitSelector explicit={this.state.show.explicit}
                                  handleChange={this.handleChangeExplicit}
                                  />
                <ImageSelector selectedImageId={this.state.show.image_id}
                               handleSelect={this.handleSelectImage}
                               authenticatedRequest={this.props.route.authenticatedRequest} />
              </Form>
            </div>
        );
    }
});

module.exports = {
    Show: App
};
