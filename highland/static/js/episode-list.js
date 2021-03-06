import React from "react";
import { Button, Checkbox, Table } from 'react-bootstrap';
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
        this.props.authenticatedRequest.delete(
            '/episode', {
                show_id: this.props.showId,
                episode_ids: this.props.selectedIds
            })
            .then()
            .catch((args) => console.error(args));
    }

    render() {
        return (
            <Button bsStyle="danger"
                    onClick={this.handleDelete}
                    className={this.props.className}
                    disabled={this.props.selectedIds.length < 1} >
                    Delete Selected
            </Button>
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
        this.props.route.authenticatedRequest.get(
            `/episodes/${this.props.route.showId}`, true)
            .then(data => {
                this.setState({
                    episodes: data.episodes
                });
            })
            .catch((args) => console.error(args));
    },

    render: function() {
        return (
            <div>
              <AddNew showId={this.props.route.showId} />
              <Deleter showId={this.props.route.showId}
                       className="pull-right"
                       authenticatedRequest={this.props.route.authenticatedRequest}
                       selectedIds={this.state.selectedIds} />
              <EpisodeList episodes={this.state.episodes}
                           selectedIds={this.state.selectedIds}
                           handleSelect={this.handleSelectEpisode} />
            </div>
        );
    }
});

module.exports = {
    EpisodeList: App
};
