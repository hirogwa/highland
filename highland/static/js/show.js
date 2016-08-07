import React from "react";
import _ from "underscore";
import { Button, Form } from 'react-bootstrap';
import { TextArea, TextInput, OptionSelector, ExplicitSelector } from './common.js';
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
            }
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

    handleChangeTitle: function(event) {
        this.setState({
            show: _.extend(this.state.show, {title: event.target.value})
        });
    },

    handleChangeDescription: function(event) {
        this.setState({
            show: _.extend(this.state.show, {description: event.target.value})
        });
    },

    handleChangeSubtitle: function(event) {
        this.setState({
            show: _.extend(this.state.show, {subtitle: event.target.value})
        });
    },

    handleChangeLanguage: function(event) {
        this.setState({
            show: _.extend(this.state.show, {language: event.target.value})
        });
    },

    handleChangeAuthor: function(event) {
        this.setState({
            show: _.extend(this.state.show, {author: event.target.value})
        });
    },

    handleChangeCategory: function(event) {
        this.setState({
            show: _.extend(this.state.show, {category: event.target.value})
        });
    },

    handleChangeExplicit: function(event) {
        this.setState({
            show: _.extend(this.state.show, {explicit: event.target.value === 'yes'})
        });
    },

    handleChangeAlias: function(event) {
        this.setState({
            show: _.extend(this.state.show, {alias: event.target.value})
        });
    },

    handleSelectImage: function(id) {
        this.setState({
            show: _.extend(this.state.show, {image_id: id})
        });
    },

    saveShow: function() {
        let xhr = new XMLHttpRequest();
        xhr.open(this.props.route.mode == Mode.UPDATE ? 'put' : 'post', '/show', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onload = function() {
            let data = JSON.parse(this.response);
            if (this.status == 200 || 201) {
                console.info(data);
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send(JSON.stringify(this.state.show));
    },

    render: function() {
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
              <Button bsStyle="primary" onClick={this.saveShow}>Save</Button>
            </Form>
        );
    }
});

module.exports = {
    Show: App
};
