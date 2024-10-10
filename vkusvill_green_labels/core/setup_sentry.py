import sentry_sdk

from vkusvill_green_labels.core.settings import settings


def setup_sentry() -> None:
    if settings.sentry.dsn:
        sentry_sdk.init(
            dsn=settings.sentry.dsn,
            environment=settings.sentry.environment,
            traces_sample_rate=settings.sentry.traces_sample_rate,
            profiles_sample_rate=settings.sentry.profiles_sample_rate,
        )
