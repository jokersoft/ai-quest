import logging

from fastapi import Request, HTTPException


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class UserInfo:
    """Class to hold user information from the authorizer"""
    def __init__(self, email: str, name: str = None, picture: str = None):
        self.email = email
        self.name = name
        self.picture = picture


def get_user_info(request: Request) -> UserInfo:
    """
    Dependency to extract user information from the authorizer context.
    This works when the request comes through API Gateway with the Lambda authorizer.
    """
    try:
        # Access the Lambda event context through Mangum
        # The authorizer context is available in the event
        if hasattr(request.scope, 'aws_event'):
            aws_event = request.scope['aws_event']
        else:
            # Alternative way to access the event
            aws_event = getattr(request.state, 'aws_event', None)

        if not aws_event:
            # Try to get it from the ASGI scope
            aws_event = request.scope.get('aws.event')

        if aws_event and 'requestContext' in aws_event:
            authorizer_context = aws_event['requestContext'].get('authorizer', {})

            email = authorizer_context.get('email')
            if not email:
                logger.error("No email found in authorizer context")
                raise HTTPException(status_code=401, detail="No user email found")

            name = authorizer_context.get('name', '')
            picture = authorizer_context.get('picture', '')

            logger.info(f"User authenticated: {email}")
            return UserInfo(email=email, name=name, picture=picture)
        else:
            logger.error("No AWS event context found")
            raise HTTPException(status_code=401, detail="Authentication context not found")

    except Exception as e:
        logger.error(f"Error extracting user info: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to extract user information")

