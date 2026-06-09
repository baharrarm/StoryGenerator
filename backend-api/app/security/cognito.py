import os, hmac, hashlib, base64
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

USER_POOL_ID   = os.getenv("COGNITO_USER_POOL_ID")
CLIENT_ID      = os.getenv("COGNITO_CLIENT_ID")
CLIENT_SECRET  = os.getenv("COGNITO_CLIENT_SECRET", "")

AWS_REGION     = os.getenv("AWS_REGION", "ap-southeast-2")
_cfg = Config(retries={"max_attempts": 5, "mode": "standard"}, connect_timeout=5, read_timeout=10)
cognito = boto3.client("cognito-idp", region_name=AWS_REGION, config=_cfg)
if os.getenv("APP_ENV") == "prod" and (not USER_POOL_ID or not CLIENT_ID):
    raise RuntimeError("COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID must be set in prod")

def _secret_hash(username: str) -> str | None:
    if not CLIENT_SECRET:
        return None
    msg = (username + CLIENT_ID).encode()
    key = CLIENT_SECRET.encode()
    return base64.b64encode(hmac.new(key, msg, hashlib.sha256).digest()).decode()

def sign_up(username: str, password: str, email: str):
    kwargs = {
        "ClientId": CLIENT_ID,
        "Username": username,
        "Password": password,
        "UserAttributes": [{"Name": "email", "Value": email}],
    }
    sh = _secret_hash(username)
    if sh: kwargs["SecretHash"] = sh
    return cognito.sign_up(**kwargs)

def confirm_sign_up(username: str, code: str):
    kwargs = {"ClientId": CLIENT_ID, "Username": username, "ConfirmationCode": code}
    sh = _secret_hash(username)
    if sh: kwargs["SecretHash"] = sh
    return cognito.confirm_sign_up(**kwargs)

def login(username: str, password: str):
    auth_params = {"USERNAME": username, "PASSWORD": password}
    sh = _secret_hash(username)
    if sh: auth_params["SECRET_HASH"] = sh
    resp = cognito.initiate_auth(
        ClientId=CLIENT_ID,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters=auth_params,
    )
    # tokens: IdToken (user identity), AccessToken
    return resp["AuthenticationResult"]

def update_email(access_token: str, new_email: str):
    cognito.update_user_attributes(
        AccessToken=access_token,
        UserAttributes=[{"Name": "email", "Value": new_email}],
    )
    cognito.get_user_attribute_verification_code(
        AccessToken=access_token, AttributeName="email"
    )

def confirm_email(access_token: str, code: str):
    cognito.verify_user_attribute(
        AccessToken=access_token, AttributeName="email", Code=code
    )

def change_password(access_token: str, old_password: str, new_password: str):
    return cognito.change_password(
        AccessToken=access_token,
        PreviousPassword=old_password,
        ProposedPassword=new_password,
    )

def admin_delete_cognito_user(username: str):
    """Delete a user from the Cognito user pool (admin API)."""
    try:
        cognito.admin_delete_user(UserPoolId=USER_POOL_ID, Username=username)
    except ClientError as e:
        # ignore if already gone. re-raise other errors
        if e.response["Error"]["Code"] != "UserNotFoundException":
            raise