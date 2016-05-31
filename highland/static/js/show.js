import React from "react";
import ReactDOM from "react-dom";
console.log('hello console');

var App = React.createClass({
    render: function() {
        return <h1>Hello front-end!</h1>
    }
});

ReactDOM.render(<App />, document.querySelector(".mainContainer"))
