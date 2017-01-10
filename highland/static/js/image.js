import React from "react";
import { Checkbox, Table } from 'react-bootstrap';
import { Media } from './media.js';

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

class Image extends React.Component {
    constructor(props) {
        super(props);
        this.handleUpload = this.handleUpload.bind(this);
        this.handleSelectImage = this.handleSelectImage.bind(this);
        this.reloadImageList = this.reloadImageList.bind(this);
        this.state = {
            images: [],
            selectedIds: []
        };
    }

    handleSelectImage(id, checked) {
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
    }

    reloadImageList() {
        return this.props.route.authenticatedRequest.get('/image')
            .then(data => {
                this.setState({
                    images: data.images
                });
            })
            .catch(args => console.error(args));
    }

    componentDidMount() {
        return this.reloadImageList();
    }

    handleUpload(file, type) {
        const authReq = this.props.route.authenticatedRequest;
        return authReq.post('/image', {
            filename: file.name,
            filetype: type
        })
            .then(response => authReq.postImage(
                file, response.image.guid, type));
    }

    render() {
        const imageList = (
            <ImageList images={this.state.images}
                       selectedIds={this.state.selectedIds}
                       handleSelect={this.handleSelectImage} />
        );

        return (
            <Media selectedIds={this.state.selectedIds}
                   url="/image"
                   authenticatedRequest={this.props.route.authenticatedRequest}
                   uploaderLabel="New Image"
                   handleUpload={this.handleUpload}
                   mediaList={imageList}
                   reloadList={this.reloadImageList}
                   />
        );
    }
}

module.exports = {
    Image: Image
};
