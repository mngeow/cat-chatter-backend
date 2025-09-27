from core_utils.sso.base import BaseSSOClient
from core_utils.sso.schema import User
from .config import AzureSSOConfig
from aiohttp import ClientSession
from loguru import logger
from msal.oauth2cli.oidc import decode_id_token
from core_utils.exceptions.exceptions_http import Unauthorized_401
from core_utils.exceptions.exceptions_internal import Unauthorized
import jwt
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from uuid import uuid4


class AzureSSOClient(BaseSSOClient):
    def __init__(self, config: AzureSSOConfig) -> None:
        self._config = config

    async def validate_token(self, token: str) -> User:
        async with ClientSession() as session:
            async with session.get(
                url=self._config.user_info_endpoint(),
                headers={"Authorization": token},
            ) as response:
                if response.status != 200:
                    response_error_dict = await response.json()
                    raise Unauthorized_401(
                        ex=Unauthorized(
                            message=f"{response_error_dict['error']['code']}: {response_error_dict['error']['message']}"
                        )
                    )

        try:
            decoded_id_token_dict = decode_id_token(
                id_token=token, issuer=self._config.issuer
            )

            assert decoded_id_token_dict["appid"] == self._config.client_id

        except RuntimeError as ex:
            logger.error(
                f"Something failed when trying to decode the OIDC jwt token: {str(ex)}"
            )
            raise

        # TODO: This is a temporary hack, so as not to block frontend work. Proper fix should be implemented once root cause is determined.
        email = (
            decoded_id_token_dict["email"]
            if "email" in decoded_id_token_dict
            else decoded_id_token_dict["upn"]
        )

        return User(email=email, id=decoded_id_token_dict["oid"])

    async def validate_id_token(self, token: str) -> User:
        async with ClientSession() as session:
            async with session.get(
                url=self._config.public_keys_endpoints_url,
            ) as response:
                if response.status != 200:
                    response_error_dict = await response.json()
                    raise Unauthorized_401(
                        ex=Unauthorized(
                            message=f"{response_error_dict['error']['code']}: {response_error_dict['error']['message']}"
                        )
                    )

                try:
                    decoded_token = jwt.get_unverified_header(token)
                except jwt.exceptions.DecodeError as ex:
                    raise Unauthorized_401(
                        ex=Unauthorized(message=f"TokenDecodeFailed: {ex}")
                    )
                except Exception as ex:
                    raise Unauthorized_401(
                        ex=Unauthorized(message=f"Error Decoding Token: {ex}")
                    )

                kid = decoded_token["kid"]

                result = await response.json()
                keys = result["keys"]

                key = next((key for key in keys if key["kid"] == kid), None)

                if not key:
                    raise Unauthorized_401(
                        ex=Unauthorized(message="Public key not found")
                    )

                # Verify the token
                public_key = load_pem_x509_certificate(
                    f"-----BEGIN CERTIFICATE-----\n{key['x5c'][0]}\n-----END CERTIFICATE-----".encode(),
                    default_backend(),
                ).public_key()

                try:
                    verified_decoded_token = jwt.decode(
                        token,
                        public_key,
                        algorithms=["RS256"],
                        audience=self._config.client_id,
                    )
                except jwt.exceptions.InvalidTokenError as e:
                    raise Unauthorized_401(
                        ex=Unauthorized(message=f"Invalid ID Token: {e}")
                    )
                except Exception as ex:
                    raise Unauthorized_401(
                        ex=Unauthorized(message=f"Error Verifying Token: {ex}")
                    )


                # Following UUID will only be used for the inital create user call.
                return User(
                    email=verified_decoded_token["upn"],
                    uid=verified_decoded_token["sub"],
                    id=str(uuid4()),
                    scopes=verified_decoded_token["roles"] if "roles" in verified_decoded_token else []
                )
