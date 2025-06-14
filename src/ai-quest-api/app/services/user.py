import logging
import os
import uuid

from fastapi import Request, HTTPException

from app.clients import db_client
from app.entities.user import User
from app.repositories.user import UserRepository


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

APP_ENV = os.getenv("APP_ENV", "prod")


class UserInfo:
    """Class to hold user information from the authorizer"""
    def __init__(self, user_id: uuid.UUID, email: str, name: str = None, picture: str = None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.picture = picture


def get_user_info(request: Request) -> UserInfo:
    """
    Dependency to extract user information from the authorizer context.
    This works when the request comes through API Gateway with the Lambda authorizer.
    """
    try:
        # In local development, we might not have the authorizer context
        if APP_ENV == "local":
            logger.debug("Running in local environment, skipping user info extraction")
            test_uuid = uuid.UUID('00000000-0000-0000-0000-000000000000')
            return UserInfo(user_id=test_uuid, email="test@test.com", name="Test User")

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

            user = get_or_create_user_by_email(email)

            name = authorizer_context.get('name', None)
            picture = authorizer_context.get('picture', None)

            logger.info(f"User authenticated: {email}")
            return UserInfo(email=email, name=name, picture=picture, user_id=user.get_id())
        else:
            logger.error("No AWS event context found")
            raise HTTPException(status_code=401, detail="Authentication context not found")

    except Exception as e:
        logger.error(f"Error extracting user info: {str(e)}")
        raise HTTPException(status_code=401, detail="Failed to extract user information")


def get_or_create_user_by_email(email: str) -> User:
    """
    Retrieve a user by email.
    """
    with db_client.session() as session:
        user_repository = UserRepository(session)
        user = user_repository.get_by_email(email)
        if not user:
            logger.warning(f"User with email {email} not found, creating...")
            user = user_repository.add(User(email=email))

    return user

