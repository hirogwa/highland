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
import { ResetPassword } from './reset-password.js';
import { AuthenticatedRequest } from './auth-utils.js';
import { Identity } from './identity';

const App = React.createClass({
    logout: function() {
        this.props.route.authenticatedRequest.logout()
            .then(() => window.location = '/login');
    },

    render: function() {
        return (
            <div className="container">
              <h1>Dashboard</h1>
              <ul role="nav">
                <li><IndexLink to="/">Stats</IndexLink></li>
                <li><NavLink to="/episode">Episode</NavLink></li>
                <li><NavLink to="/audio">Audio</NavLink></li>
                <li><NavLink to="/image">Image</NavLink></li>
                <li><NavLink to="/show">Show Settings</NavLink></li>
              </ul>
              <h4>Account</h4>
              <ul>
                <li><NavLink to="/resetpassword">Reset Password</NavLink></li>
                <li><a href="" onClick={this.logout}>Logout</a></li>
              </ul>
              <hr />

              <div className="container">
                {this.props.children}
              </div>
            </div>
        );
    }
});

const identity = new Identity(
    cognitoUserPoolId, cognitoClientId,
    cognitoIdentityPoolId, cognitoIdentityProvider);

const authenticatedRequest = new AuthenticatedRequest(
    identity, {
        imageBucket: imageBucket,
        audioBucket: audioBucket
    });

ReactDOM.render(
    <Router history={hashHistory}>
      <Route path="/"
             authenticatedRequest={authenticatedRequest}
             component={App}>
        <IndexRoute showId={showId}
                    authenticatedRequest={authenticatedRequest}
                    component={Stat} />
        <Route path="/episode"
               showId={showId}
               authenticatedRequest={authenticatedRequest}
               component={EpisodeList} />
        <Route path="/episode/new"
               showId={showId}
               authenticatedRequest={authenticatedRequest}
               mode="create"
               component={Episode} />
        <Route path="/episode/:episodeId"
               showId={showId}
               authenticatedRequest={authenticatedRequest}
               mode="update"
               component={Episode} />
        <Route path="/audio"
               authenticatedRequest={authenticatedRequest}
               component={Audio} />
        <Route path="/image"
               authenticatedRequest={authenticatedRequest}
               component={Image} />
        <Route path="/show"
               showId={showId}
               authenticatedRequest={authenticatedRequest}
               mode="update"
               component={Show} />
        <Route path="/resetpassword"
               cognitoUserPoolId={cognitoUserPoolId}
               cognitoClientId={cognitoClientId}
               component={ResetPassword} />
      </Route>
    </Router>,
    document.querySelector(".mainContainer"));
