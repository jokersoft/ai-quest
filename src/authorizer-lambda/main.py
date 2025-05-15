import os
import json
import logging
import urllib.request
import jwt

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
ALLOWED_DOMAINS = os.environ.get('ALLOWED_DOMAINS', '').split(',')

# Google's public keys URL
GOOGLE_PUBLIC_KEYS_URL = 'https://www.googleapis.com/oauth2/v3/certs'


def get_google_public_keys():
    """Fetch Google's public keys used to verify the JWT token"""
    try:
        with urllib.request.urlopen(GOOGLE_PUBLIC_KEYS_URL) as response:
            keys_data = json.loads(response.read())
        return keys_data
    except Exception as e:
        logger.error(f"Error fetching Google public keys: {str(e)}")
        return None


def validate_token(token):
    """Validate the JWT token from Google"""
    try:
        # Get Google's public keys
        keys_data = get_google_public_keys()
        if not keys_data:
            return None

        # Decode and verify the token
        # Note: Google uses the 'kid' header to identify which key to use
        unverified_header = jwt.get_unverified_header(token)

        # Find the matching key
        public_keys = {}
        for jwk in keys_data['keys']:
            kid = jwk['kid']
            public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

        key_id = unverified_header['kid']
        if key_id not in public_keys:
            logger.error("Key ID not found in Google's public keys")
            return None

        # Decode and verify the token
        payload = jwt.decode(
            token,
            public_keys[key_id],
            algorithms=['RS256'],
            audience=GOOGLE_CLIENT_ID,
            options={'verify_exp': True}
        )

        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None


def check_domain(email):
    """Check if the email domain is in the allowed domains list"""
    if not ALLOWED_DOMAINS or ALLOWED_DOMAINS[0] == '':
        # If no domains are specified, allow all domains
        return True

    domain = email.split('@')[-1]
    return domain in ALLOWED_DOMAINS


def generate_policy(principal_id, effect, resource, context=None):
    """Generate an IAM policy document"""
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }

    if context:
        policy['context'] = context

    return policy


def handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")

    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID environment variable is not set")
        return generate_policy('user', 'Deny', event['methodArn'])

    # Extract the token from the Authorization header
    try:
        auth_header = event['headers'].get('Authorization') or event['headers'].get('authorization')
        if not auth_header:
            logger.error("No Authorization header found")
            return generate_policy('user', 'Deny', event['methodArn'])

        token = auth_header.split(' ')[1]  # Remove 'Bearer ' prefix
    except Exception as e:
        logger.error(f"Error extracting token: {str(e)}")
        return generate_policy('user', 'Deny', event['methodArn'])

    # Validate the token
    payload = validate_token(token)
    if not payload:
        logger.error("Invalid token")
        return generate_policy('user', 'Deny', event['methodArn'])

    # Check if the email is from an allowed domain
    email = payload.get('email')
    if not email:
        logger.error("No email found in token payload")
        return generate_policy('user', 'Deny', event['methodArn'])

    if not check_domain(email):
        logger.error(f"Email domain not allowed: {email}")
        return generate_policy('user', 'Deny', event['methodArn'])

    # User is authenticated and authorized
    # Create a context with user information to pass to the API
    context = {
        'email': email,
        'name': payload.get('name', ''),
        'picture': payload.get('picture', '')
    }

    return generate_policy(email, 'Allow', event['methodArn'], context)
