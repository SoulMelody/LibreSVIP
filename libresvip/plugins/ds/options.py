from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnablePitchImportationMixin,
    SelectSingleTrackMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(SelectSingleTrackMixin, BaseModel):
    dict_name: str = Field(default="opencpop-extension", title=_("Dictionary Name"))
    split_threshold: float = Field(
        default=5,
        title=_("Split threshold (in seconds)"),
        description=_(
            "This option controls the segmentation strategy during conversion. When the value of this option is negative, no segmentation is performed; when the value of this option is 0, segmentation is performed at the threshold where the interval between all notes reaches the threshold; when the value of this option is positive, the minimum length of each segment can be controlled on the basis of segmentation. Setting a reasonable segmentation strategy can reduce the memory usage during synthesis while maximizing the utilization of performance and improving the synthesis effect."
        ),
    )
    min_interval: int = Field(
        default=400,
        title=_("Minimum interval (in milliseconds)"),
        description=_(
            "This option controls the minimum interval between notes. It is recommended to set it to a value greater than 300 milliseconds."
        ),
    )
    seed: int = Field(
        default=-1,
        title=_("Seed"),
        description=_(
            "A fixed random seed can get a stable and reproducible synthesis effect. This option takes effect when the non-negative value is set."
        ),
    )
    export_gender: bool = Field(
        default=False,
        title=_("Export gender parameter"),
    )
    indent: int = Field(
        default=2,
        title=_("Indentation"),
        description=_(
            "The number of spaces used for indentation. When the value is negative, no formatting is performed."
        ),
    )
