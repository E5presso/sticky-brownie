from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.cryptography.jwt import JWT

from apps.user.domain.interfaces.service.token_service import IAsyncTokenService
from apps.user.domain.models.user import User
from common.settings.config import Config, TokenSetting


@Bean()
class AsyncTokenService(IAsyncTokenService):
    __token_setting: TokenSetting

    @autowired
    def __init__(self) -> None:
        self.__token_setting = Config().token

    async def generate_token(self, user: User) -> JWT:
        return (
            JWT()
            .set_expiration(self.__token_setting.expire_after)
            .set_payload(sub=str(user.uid))
            .set_payload(role=user.role)
            .sign(self.__token_setting.secret_key)
        )
