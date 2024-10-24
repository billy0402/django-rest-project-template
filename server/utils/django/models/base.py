import typing as t

from server.utils.django.middlewares.request_user import get_request_user
from server.utils.django.models import utils as util_models


class BaseModel(
    util_models.UUIDModel,
    util_models.TimestampModel,
    util_models.EditorModel,
):
    def save(self, *args: t.Any, **kwargs: t.Any) -> None:
        request_user = get_request_user()
        if not self.created_at:
            self.creator = request_user
        self.editor = request_user
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ("-created_at",)
