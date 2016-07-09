import React from "react";
import { ControlLabel, Radio, Table } from 'react-bootstrap';

class ImageNone extends React.Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect() {
        this.props.handleSelect(null);
    }

    render() {
        return(
            <tr>
              <td>
                <Radio checked={this.props.selected}
                       onChange={this.handleSelect} />
              </td>
              <td>None</td>
            </tr>
        );
    }
}

class ImageSingle extends React.Component {
    constructor(props) {
        super(props);
        this.handleSelect = this.handleSelect.bind(this);
    }

    handleSelect() {
        this.props.handleSelect(this.props.image.id);
    }

    render() {
        return(
            <tr>
              <td>
                <Radio checked={this.props.selected}
                       onChange={this.handleSelect} />
              </td>
              <td>
                <a href={this.props.image.url}>
                  {this.props.image.filename}
                </a>
              </td>
            </tr>
        );
    }
}

class ImageList extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        let rows = [];
        let self = this;
        rows.push(
            <ImageNone key={-1}
                       selected={self.props.selectedId === null}
                       handleSelect={self.props.handleSelect} />
        );
        this.props.images.forEach(function(image) {
            rows.push(
                <ImageSingle image={image} key={image.id}
                             selected={self.props.selectedId === image.id}
                             handleSelect={self.props.handleSelect} />
            );
        });
        return(
            <Table striped bordered condensed hover>
              <thead>
                <tr>
                  <th></th>
                  <th>File</th>
                </tr>
              </thead>
              <tbody>
                {rows}
              </tbody>
            </Table>
        );
    }
}

class ImageSelector extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            images: []
        };
    }

    componentDidMount() {
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
    }

    render() {
        return(
            <div>
              <ControlLabel>Image</ControlLabel>
              <ImageList selectedId={this.props.selectedImageId}
                         images={this.state.images}
                         handleSelect={this.props.handleSelect} />
            </div>
        );
    }
}

module.exports = {
    ImageSelector: ImageSelector
};
