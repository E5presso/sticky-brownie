from spakky.bean.autowired import autowired
from spakky.bean.bean import Bean
from spakky.cryptography.jwt import JWT

from src.apps.user.domain.models.user import User
from src.apps.user.domain.ports.service.token_service import IAsyncTokenService
from src.common.config import Config, TokenSetting


@Bean()
class AsyncTokenService(IAsyncTokenService):
    __token_setting: TokenSetting

    @autowired
    def __init__(self, config: Config) -> None:
        self.__token_setting = config.token

    async def generate_token(self, user: User) -> JWT:
        return (
            JWT()
            .set_expiration(self.__token_setting.expire_after)
            .set_payload(sub=str(user.uid))
            .sign(self.__token_setting.secret_key)
        )
