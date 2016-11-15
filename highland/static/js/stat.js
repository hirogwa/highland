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
        const self = this;
        const url = `/episodes/${this.props.route.showId}?public=yes`;
        this.props.route.authenticatedRequest.get(url)
            .then((resp) => {
                const data = JSON.parse(resp);
                self.setState({
                    episodes: data.episodes
                });
            })
            .catch((args) => console.error(args));
    },

    loadStatEpisodeByDay: function() {
        this.loadStat('/stat/episode_by_day', 'statByDay');
    },

    loadStatEpisodeWeek: function() {
        this.loadStat('/stat/episode_past_week', 'statWeek');
    },

    loadStatEpisodeCumulative: function() {
        this.loadStat('/stat/episode_cumulative', 'statCumulative');
    },

    loadStat: function(endpoint, stateKey) {
        const self = this;
        const showId = encodeURIComponent(this.props.route.showId);
        this.props.route.authenticatedRequest.get(`${endpoint}?show_id=${showId}`)
            .then((resp) => {
                const data = JSON.parse(resp);
                self.setState({
                    [stateKey]: data.stat
                });
            })
            .catch((args) => console.error(args));
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
