import React from "react";
import { Table } from 'react-bootstrap';
import { NavLink } from './common.js';

class StatTableRow extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        let episode_link = "/episode/" + this.props.episode.id;
        return (
            <tr>
              <td>
                <NavLink to={episode_link}>
                  {this.props.episode.title}
                </NavLink>
              </td>
              <td>{this.props.episode.published_datetime}</td>
              <td>{this.props.statToday}</td>
              <td>{this.props.statWeek}</td>
              <td>{this.props.statCumulative}</td>
            </tr>
        );
    }
}

class StatTable extends React.Component {
    constructor(props) {
        super(props);
        this.getToday = this.getToday.bind(this);
        this.getWeek = this.getWeek.bind(this);
        this.getCumulative = this.getCumulative.bind(this);
        this.todayString = this.getTodayString();
    }

    getTodayString() {
        let today = new Date();
        let month = today.getMonth() + 1;
        month = (month < 10 ? '' : '0') + month;
        return '' + today.getFullYear() +
            (month < 10 ? '0' : '') + month + today.getDate();
    }

    getToday(episode) {
        let stat = this.props.statByDay[episode.id];
        if (stat) {
            let s = stat[this.todayString];
            return s ? s.users : 0;
        } else {
            return 0;
        }
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
            let today = self.getToday(episode);
            let week = self.getWeek(episode);
            let cumulative = self.getCumulative(episode);

            rows.push(
                <StatTableRow episode={episode}
                              key={episode.id}
                              statToday={today}
                              statWeek={week}
                              statCumulative={cumulative} />
            );
        });

        return (
            <Table>
              <thead>
                <tr>
                  <th>Episode</th>
                  <th>Published</th>
                  <th>Today</th>
                  <th>Past Week</th>
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
        xhr.open('get', '/episodes/' + this.props.route.showId + '?public=yes', true);
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
                 + encodeURIComponent(this.props.route.showId));
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
                 + encodeURIComponent(this.props.route.showId));
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
                 + encodeURIComponent(this.props.route.showId));
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
                         statByDay={this.state.statByDay}
                         statWeek={this.state.statWeek}
                         statCumulative={this.state.statCumulative} />
            </div>
        );
    }
});

module.exports = {
    Stat: App
};
