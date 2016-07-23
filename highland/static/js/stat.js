import React from "react";
import ReactDOM from "react-dom";
import { Table } from 'react-bootstrap';

class StatTableRow extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        let episode_url = "/page/episode/{s}/{e}"
                .replace('{s}', this.props.episode.show_id)
                .replace('{e}', this.props.episode.id);

        return (
            <tr>
              <td>
                <a href={episode_url}>{this.props.episode.title}</a>
              </td>
              <td>{this.props.episode.create_datetime}</td>
              <td>{this.props.statWeek}</td>
              <td>{this.props.statCumulative}</td>
            </tr>
        );
    }
}

class StatTable extends React.Component {
    constructor(props) {
        super(props);
        this.getWeek = this.getWeek.bind(this);
        this.getCumulative = this.getCumulative.bind(this);
    }

    getWeek(episode) {
        let s = this.props.statWeek[episode.id];
        return s ? s.users : 0;
    }

    getCumulative(episode) {
        let s = this.props.statCumulative[episode.id];
        return s ? s.users : 0;
    }

    render() {
        let rows = [];
        let self = this;

        this.props.episodes.forEach(function(episode) {
            let week = self.getWeek(episode);
            let cumulative = self.getCumulative(episode);

            rows.push(
                <StatTableRow episode={episode}
                              key={episode.id}
                              statWeek={week}
                              statCumulative={cumulative} />
            );
        });

        return (
            <Table>
              <thead>
                <tr>
                  <th>Episode</th>
                  <th>Created</th>
                  <th>Week</th>
                  <th>Cumulative</th>
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
            statByDay: {},
            statWeek: {},
            statCumulative: {}
        };
    },

    loadEpisodes: function() {
        let self = this;
        let xhr = new XMLHttpRequest();
        xhr.open('get', '/episodes/' + this.props.showId + '?public=yes', true);
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

    loadStatEpisodeByDay: function() {
        let self = this;
        let xhr = new XMLHttpRequest();
        xhr.open('get', '/stat/episode_by_day?show_id='
                 + encodeURIComponent(this.props.showId));
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                self.setState({
                    statByDay: data.stat
                });
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send();
    },

    loadStatEpisodeWeek: function() {
        let self = this;
        let xhr = new XMLHttpRequest();
        xhr.open('get', '/stat/episode_past_week?show_id='
                 + encodeURIComponent(this.props.showId));
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                self.setState({
                    statWeek: data.stat
                });
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send();
    },

    loadStatEpisodeCumulative: function() {
        let self = this;
        let xhr = new XMLHttpRequest();
        xhr.open('get', '/stat/episode_cumulative?show_id='
                 + encodeURIComponent(this.props.showId));
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                self.setState({
                    statCumulative: data.stat
                });
            } else {
                console.error(this.statusText);
            }
        };
        xhr.send();
    },

    componentDidMount: function() {
        this.loadEpisodes();
        this.loadStatEpisodeByDay();
        this.loadStatEpisodeWeek();
        this.loadStatEpisodeCumulative();
    },

    render: function() {
        return (
            <div>
              <StatTable episodes={this.state.episodes}
                         statWeek={this.state.statWeek}
                         statCumulative={this.state.statCumulative} />
            </div>
        );
    }
});

ReactDOM.render(<App showId={showId} />,
                document.querySelector(".mainContainer"));
