import React from "react";
import {
    Button, Checkbox, Form, Table
} from 'react-bootstrap';
import { NavLink } from './common.js';
import { episodePath } from './paths';

class AddNew extends React.Component {
    render() {
        return(
            <NavLink className="btn btn-default" to="/episode/new">
              Add New
            </NavLink>
        );
    }
}

class Deleter extends React.Component {
    constructor(props) {
        super(props);
        this.handleDelete = this.handleDelete.bind(this);
    }

    handleDelete() {
        let xhr = new XMLHttpRequest();
        xhr.open('delete', '/episode', true);
        xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                console.info(data);
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send(
            JSON.stringify({
                show_id: this.props.showId,
                episode_ids: this.props.selectedIds
            })
        );
    }

    render() {
        return (
            <Form>
              <Button bsStyle="danger" onClick={this.handleDelete}
                      type="submit"
                      disabled={this.props.selectedIds.length < 1}>
                      Delete Selected
              </Button>
            </Form>
        );
    }
}

class SingleEpisode extends React.Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect(event) {
        this.props.handleSelect(this.props.episode.id, event.target.checked);
    }

    render() {
        return(
            <tr>
              <td>
                <Checkbox checked={this.props.selected}
                          onChange={this.handleSelect} />
              </td>
              <td>
                {this.props.episode.title}
              </td>
              <td>{this.props.episode.subtitle}</td>
              <td>{this.props.episode.draft_status}</td>
              <td>{this.props.episode.published_datetime}</td>
              <td>{this.props.episode.create_datetime}</td>
              <td>
                <NavLink className="btn btn-default btn-sm"
                         to={episodePath(this.props.episode.id)}>
                  Edit
                </NavLink>
              </td>
            </tr>
        );
    }
}

class EpisodeList extends React.Component {
    render() {
        let rows = [];
        let self = this;
        this.props.episodes.forEach(function(episode) {
            rows.push(
                <SingleEpisode episode={episode}
                               key={episode.id}
                               selected={self.props.selectedIds.indexOf(episode.id) > -1}
                               handleSelect={self.props.handleSelect} />
            );
        });

        return(
            <Table>
              <thead>
                <tr>
                  <th></th>
                  <th>Title</th>
                  <th>Subtitle</th>
                  <th>Draft status</th>
                  <th>Published</th>
                  <th>Created</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows}
              </tbody>
            </Table>
        );
    }
}

var App = React.createClass({
    getInitialState: function() {
        return {
            episodes: [],
            selectedIds: []
        };
    },

    handleSelectEpisode(id, checked) {
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
    },

    componentDidMount: function() {
        var self = this;
        var xhr = new XMLHttpRequest();
        xhr.open('get', '/episodes/' + this.props.route.showId, true);
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                self.setState({
                    episodes: data.episodes
                });
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send();
    },

    render: function() {
        return (
            <div>
              <AddNew showId={this.props.route.showId} />
              <EpisodeList episodes={this.state.episodes}
                           selectedIds={this.state.selectedIds}
                           handleSelect={this.handleSelectEpisode} />
              <Deleter showId={this.props.route.showId}
                       selectedIds={this.state.selectedIds} />
            </div>
        );
    }
});

module.exports = {
    EpisodeList: App
};
