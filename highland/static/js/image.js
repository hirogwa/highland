import React from "react";
import ReactDOM from "react-dom";
import { Checkbox, Table } from 'react-bootstrap';
import { Deleter, Uploader } from './common.js';

class SingleImage extends React.Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect(event) {
        this.props.handleSelect(this.props.image.id, event.target.checked);
    }

    render() {
        return (
            <tr>
              <td>
                <Checkbox checked={this.props.selected}
                          onChange={this.handleSelect} />
              </td>
              <td>
                <a href={this.props.image.url}>
                  {this.props.image.filename}
                </a>
              </td>
              <td>{this.props.image.create_datetime}</td>
              <td>{this.props.image.guid}</td>
            </tr>
        );
    }
}

class ImageList extends React.Component {
    render() {
        let rows = [];
        let self = this;
        this.props.images.forEach(function(image) {
            rows.push(
                <SingleImage image={image} key={image.id}
                             selected={self.props.selectedIds.indexOf(image.id) > -1}
                             handleSelect={self.props.handleSelect} />
            );
        });
        return (
            <Table>
              <thead>
                <tr>
                  <th></th>
                  <th>File</th>
                  <th>Created</th>
                  <th>Guid</th>
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
            images: [],
            selectedIds: []
        };
    },

    handleSelectImage: function(id, checked) {
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
        xhr.open('get', '/image', true);
        xhr.onload = function() {
            if (this.status == 200) {
                let data = JSON.parse(this.response);
                self.setState({
                    images: data.images
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
              <Uploader label="New Image"
                        url="/image" />
              <ImageList images={this.state.images}
                         selectedIds={this.state.selectedIds}
                         handleSelect={this.handleSelectImage} />
              <Deleter selectedIds={this.state.selectedIds}
                       url="/image" />
            </div>
        );
    }
});

ReactDOM.render(<App/>,
                document.querySelector(".mainContainer"));