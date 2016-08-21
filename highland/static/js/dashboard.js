import React from "react";
import ReactDOM from "react-dom";
import {
    IndexLink, IndexRoute, Router, Route, hashHistory
} from 'react-router';
import { NavLink } from './common.js';
import { Stat } from './stat.js';
import { Audio } from './audio.js';
import { Image } from './image.js';
import { EpisodeList } from './episode-list.js';
import { Episode } from './episode.js';
import { Show } from './show.js';

var App = React.createClass({
    render: function() {
        return (
            <div>
              <h1>Dashboard</h1>
              <ul role="nav">
                <li><IndexLink to="/">Stats</IndexLink></li>
                <li><NavLink to="/episode">Episode</NavLink></li>
                <li><NavLink to="/audio">Audio</NavLink></li>
                <li><NavLink to="/image">Image</NavLink></li>
                <li><NavLink to="/show">Show Settings</NavLink></li>
              </ul>
              {this.props.children}
            </div>
        );
    }
});

ReactDOM.render(
    <Router history={hashHistory}>
      <Route path="/" component={App}>
        <IndexRoute showId={showId} component={Stat} />
        <Route path="/episode" showId={showId} component={EpisodeList} />
        <Route path="/episode/new" showId={showId} mode="create" component={Episode} />
        <Route path="/episode/:episodeId" showId={showId} mode="update" component={Episode} />
        <Route path="/audio" component={Audio} />
        <Route path="/image" component={Image} />
        <Route path="/show" showId={showId} mode="update" component={Show} />
      </Route>
    </Router>,
    document.querySelector(".mainContainer"));