from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from libresvip.model.option_mixins import (
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableStrengthImportationMixin,
    EnableVolumeImportationMixin,
)
from libresvip.utils.translation import gettext_lazy as _


class BinarySvipVersion(Enum):
    AUTO: Annotated[
        str,
        Field(
            title=_("Auto detect"),
            description=_(
                "Use the version of the project file corresponding to the X Studio installed on your current system."
            ),
        ),
    ] = "auto"
    SVIP7_0_0: Annotated[
        str,
        Field(
            title="SVIP 7.0.0",
            description=_("Use the project file version of X Studio 2.0."),
        ),
    ] = "7.0.0"
    SVIP6_0_0: Annotated[
        str,
        Field(
            title="SVIP 6.0.0",
            description=_("Use the project file version which is compatible with X Studio 1.8."),
        ),
    ] = "6.0.0"
    COMPAT: Annotated[
        str,
        Field(
            title=_("Max compatibility (read only)"),
            description=_("""Export project files that can be opened using any version of X Studio.
Warning: After saving with this option, the volume, breath, gender, and power parameters will not be recognized by X Studio (no data is lost).
To avoid irretrievable data loss, it is strongly recommended not to use X Studio to modify and save project files exported with this option. To restore the project file back to a safe editable state, select Save as SVIP 6.0.0 or later."""),
        ),
    ] = "0.0.0"


class InputOptions(
    EnableBreathImportationMixin,
    EnableGenderImportationMixin,
    EnableInstrumentalTrackImportationMixin,
    EnablePitchImportationMixin,
    EnableStrengthImportationMixin,
    EnableVolumeImportationMixin,
    BaseModel,
):
    pass


class OutputOptions(BaseModel):
    singer: str = Field(
        default="陈水若",
        title=_("Default singer"),
        description=_(
            "Please enter the singer's name in Chinese. If the specified singer does not exist, the default singer set in X Studio will be used. If you want to specify the conversion relationship between singer ID and name, or add a singer that has an ID but has not been publicly released, please modify singers.json in the plugin directory."
        ),
    )
    tempo: int = Field(
        default=60,
        title=_("Default tempo"),
        description="The allowed range of tempo in X Studio is 20 ~ 300. When the tempo is out of range, the absolute timeline will be used to ensure the alignment of notes. Please set this value to an integer multiple or integer fraction of the tempo in the source project file as much as possible; as long as it is within a reasonable range, the value of this option will not affect the alignment effect.",
    )
    version: BinarySvipVersion = Field(
        default=BinarySvipVersion.AUTO,
        title=_("Specify the version of the generated .svip file"),
        description=_("""This option only controls the header version information of the output project file.
Choosing an older project file version will not affect the integrity of the data, but using a lower version of X Studio to open, edit and save a higher version project file may cause data loss."""),
    )
