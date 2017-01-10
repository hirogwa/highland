import React from "react";
import { AlertBox, Deleter, Uploader } from './common.js';
import { Texts } from './constants.js';

class Media extends React.Component {
    constructor(props) {
        super(props);
        this.handleAlertDismiss = this.handleAlertDismiss.bind(this);
        this.handleUpload = this.handleUpload.bind(this);
        this.onDeleting = this.onDeleting.bind(this);
        this.onDeleted = this.onDeleted.bind(this);
        this.onDeletionFailed = this.onDeletionFailed.bind(this);
        this.state = {
            activeAlert: null
        };
    }

    onDeleting() {
        this.setState({
            activeAlert: {
                content: Texts.NOTIFY_DELETING
            }
        });
    }

    onDeleted() {
        this.setState({
            activeAlert: {
                style: 'success',
                content: Texts.NOTIFY_DELETED
            }
        });
        this.props.reloadList();
    }

    onDeletionFailed() {
        this.setState({
            activeAlert: {
                style: 'danger',
                content: Texts.NOTIFY_ERROR
            }
        });
    }

    handleAlertDismiss() {
        this.setState({
            activeAlert: null
        });
    }

    handleUpload(file, type) {
        this.setState({
            activeAlert: {
                content: Texts.NOTIFY_UPLOADING
            }
        });

        return this.props.handleUpload(file, type)
            .then(() => {
                this.setState({
                    activeAlert: {
                        style:'success',
                        content: Texts.NOTIFY_UPLOADED
                    }
                });
                this.props.reloadList();
            })
            .catch(e => {
                console.error(e);
                this.setState({
                    activeAlert: {
                        style:'danger',
                        content: Texts.NOTIFY_ERROR
                    }
                });
            });
    }

    render() {
        let alertBox = <div></div>;
        if (this.state.activeAlert) {
            alertBox = (
                <AlertBox
                   style={this.state.activeAlert.style}
                   content={this.state.activeAlert.content}
                   handleAlertDismiss={this.handleAlertDismiss} />
            );
        }

        return (
            <div>
              {alertBox}
              <Deleter selectedIds={this.props.selectedIds}
                       url={this.props.url}
                       className="pull-right"
                       onDeleting={this.onDeleting}
                       onDeleted={this.onDeleted}
                       onDeletionFailed={this.onDeletionFailed}
                       authenticatedRequest={this.props.authenticatedRequest} />
              <Uploader label={this.props.uploaderLabel}
                        handleSubmit={this.handleUpload} />
              {this.props.mediaList}
            </div>
        );
    }
}

module.exports = {
    Media: Media
};
