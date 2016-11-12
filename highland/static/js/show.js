import React from "react";
import _ from "underscore";
import { Button, Form } from 'react-bootstrap';
import { TextArea, TextInput, OptionSelector, ExplicitSelector, AlertBox } from './common.js';
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
            let self = this;
            let xhr = new XMLHttpRequest();
            xhr.open('get', '/show/' + this.props.route.showId, true);
            xhr.onload = function() {
                if (this.status == 200) {
                    let data = JSON.parse(this.response);
                    self.setState({
                        show: data.show
                    });
                } else {
                    console.error(this.statusText);
                }
            };
            xhr.send();
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
        let xhr = new XMLHttpRequest();
        let self = this;
        xhr.open(this.props.route.mode == Mode.UPDATE ? 'put' : 'post', '/show', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onload = function() {
            let data = JSON.parse(this.response);
            if (this.status == 200 || this.status == 201) {
                console.info(data);
                self.setState({
                    modified: false,
                    activeAlert: {
                        style: 'success',
                        content: 'Saved! :D'
                    }
                });
            } else {
                console.error(this.statusText);
                self.setState({
                    activeAlert: {
                        style: 'danger',
                        content: 'Oops! Something went wrong. :('
                    }
                });
            }
        };
        xhr.send(JSON.stringify(this.state.show));
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
              <TextInput name='Alias'
                         value={this.state.show.alias}
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
                             handleSelect={this.handleSelectImage} />
              {alertBox}
              <Button bsStyle="primary"
                      onClick={this.saveShow}
                      disabled={!this.savable()}>
                Save
              </Button>
            </Form>
        );
    }
});

module.exports = {
    Show: App
};
