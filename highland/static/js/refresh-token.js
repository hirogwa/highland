import { CognitoUserPool } from 'amazon-cognito-identity-js';
import { postAccessToken } from './auth-utils.js';

const userPool = new CognitoUserPool({
    UserPoolId: cognitoUserPoolId,
    ClientId: cognitoClientId
});
const cognitoUser = userPool.getCurrentUser();

if (cognitoUser) {
    cognitoUser.getSession(function(err, session) {
        if (err) {
            // give up. redirect to login
        } else {
            postAccessToken(session.getAccessToken().getJwtToken())
                .then(() => {
                    // redirect to the requested page
                })
                .catch(() => {
                    // give up. redirect to login
                });
        }
    });
} else {
    // give up. redirect to login
}
