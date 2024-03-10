from spakky.bean.bean import BeanFactory
from spakky.cryptography.key import Key

from common.settings.config import Config


@BeanFactory(bean_name="key")
def get_key() -> Key:
    return Config().token.secret_key
