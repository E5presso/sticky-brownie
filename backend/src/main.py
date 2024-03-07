import logging
from logging import Logger, getLogger

from fastapi import FastAPI
from spakky.aop.post_processor import AspectBeanPostProcessor
from spakky.bean.application_context import ApplicationContext
from spakky.bean.bean import BeanFactory
from spakky.extensions.logging import AsyncLoggingAdvisor
from spakky.extensions.transactional import AsyncTransactionalAdvisor
from spakky_fastapi.post_processor import FastAPIBeanPostProcessor


@BeanFactory(bean_name="logger")
def get_logger() -> Logger:
    logger = getLogger("uvicorn")
    logger.setLevel(logging.INFO)
    return logger


app: FastAPI = FastAPI()
app_context: ApplicationContext = ApplicationContext(package="src")
app_context.register_bean_post_processor(AspectBeanPostProcessor(get_logger()))
app_context.register_bean_post_processor(FastAPIBeanPostProcessor(app, get_logger()))
app_context.register_bean(AsyncLoggingAdvisor)
app_context.register_bean(AsyncTransactionalAdvisor)
app_context.start()
