import React from "react";
import ReactDOM from "react-dom";
import $ from "jquery";
import _ from "underscore";

class TitleText extends React.Component {
    render() {
        return (
            <div>
              <h3>Title</h3>
              <input type="text"
                     value={this.props.title}
                     onChange={this.props.handleChange}
                     />
            </div>
        );
    }
}

class DescriptionText extends React.Component {
    render() {
        return (
            <div>
              <h3>Description</h3>
              <input type="text"
                     value={this.props.description}
                     onChange={this.props.handleChange}
                     />
            </div>
        );
    }
}

class SubtitleText extends React.Component {
    render() {
        return (
            <div>
              <h3>Subtitle</h3>
              <input type="text"
                     value={this.props.subtitle}
                     onChange={this.props.handleChange}
                     />
            </div>
        );
    }
}

class LanguageSelector extends React.Component {
    render() {
        return (
            <div>
              <h3>Language</h3>
              <select value={this.props.language}
                      onChange={this.props.handleChange}>
                <option value="en-US">English(US)</option>
                <option value="ja">Japanese</option>
              </select>
            </div>
        );
    }
}

class AuthorText extends React.Component {
    render() {
        return (
            <div>
              <h3>Author</h3>
              <input
                 type="text"
                 value={this.props.author}
                 onChange={this.props.handleChange}
                 />
            </div>
        );
    }
}

class CategorySelector extends React.Component {
    render() {
        return (
            <div>
              <h3>Category</h3>
              <select value={this.props.category}
                      onChange={this.props.handleChange}>
                <option value="Technology">Technology</option>
                <option value="Arts">Arts</option>
              </select>
            </div>
        );
    }
}

class ExplicitSelector extends React.Component {
    render() {
        return (
            <div>
              <h3>Explicit</h3>
              <select value={this.props.explicit ? 'yes' : 'no'}
                      onChange={this.props.handleChange}>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
        );
    }
}

class Image extends React.Component {
    constructor(props) {
        super(props);
        this.state = {url: ''};
        this.componentWillReceiveProps = this.componentWillReceiveProps.bind(this);
    }

    componentWillReceiveProps(nextProps) {
        if (this.props.imageId === nextProps.imageId) {
            return;
        }

        this.serverRequest = $.get('/image/' + nextProps.imageId, function (data) {
            console.info(data);
            this.setState({
                url: data.image.url
            });
        }.bind(this));

        this.serverRequest.fail(function(data) {
            console.error(data);
        });
    }

    render() {
        return (
            <div>
              <h3>(Thumbnail)</h3>
              <img src={this.state.url} />
            </div>
        );
    }
}

class AliasText extends React.Component {
    render() {
        return (
            <div>
              <h3>(Alias)</h3>
              <input value={this.props.alias}
                     onChange={this.props.handleChange}
                     />
            </div>
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
                image_id: 0
            }
        };
    },

    componentDidMount: function() {
        if (this.props.mode == Mode.UPDATE) {
            this.serverRequest = $.get('/show/' + this.props.show_id, function (data) {
                console.info(data);
                this.setState({
                    show: data.show
                });
            }.bind(this));

            this.serverRequest.fail(function(data) {
                console.error(data);
            });
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

    saveShow: function() {
        $.ajax({
            type: this.props.mode == Mode.UPDATE ? 'PUT' : 'POST',
            url: '/show',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify(this.state.show),
            success: function() {
                console.info(arguments);
            },
            error: function(xhr, status, error) {
                console.error(arguments);
            }
        });
    },

    render: function() {
        return (
            <div>
              <Image imageId={this.state.show.image_id}
                     />
              <AliasText alias={this.state.show.alias}
                         handleChange={this.handleChangeAlias}
                         />
              <TitleText title={this.state.show.title}
                         handleChange={this.handleChangeTitle}
                         />
              <DescriptionText description={this.state.show.description}
                               handleChange={this.handleChangeDescription}
                               />
              <SubtitleText subtitle={this.state.show.subtitle}
                            handleChange={this.handleChangeSubtitle}
                            />
              <LanguageSelector language={this.state.show.language}
                              handleChange={this.handleChangeLanguage}
                              />
              <AuthorText author={this.state.show.author}
                          handleChange={this.handleChangeAuthor}
                          />
              <CategorySelector category={this.state.show.category}
                              handleChange={this.handleChangeCategory}
                              />
              <ExplicitSelector explicit={this.state.show.explicit}
                                handleChange={this.handleChangeExplicit}
                                />
              <input type="submit" value="Save" onClick={this.saveShow} />
            </div>
        );
    }
});

ReactDOM.render(<App show_id={showId} mode={mode} />,
                document.querySelector(".mainContainer"));
