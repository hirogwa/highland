import { CognitoUserPool } from 'amazon-cognito-identity-js';
import { postAccessToken } from './auth-utils.js';

const userPool = new CognitoUserPool({
    UserPoolId: cognitoUserPoolId,
    ClientId: cognitoClientId
});
const cognitoUser = userPool.getCurrentUser();

const redirect = () => window.location = redirectUrl;
const fallback = () => window.location = fallbackUrl;

if (cognitoUser) {
    cognitoUser.getSession(function(err, session) {
        if (err) {
            fallback();
        } else {
            postAccessToken(session.getAccessToken().getJwtToken())
                .then(redirect)
                .catch(fallback);
        }
    });
} else {
    fallback();
}
