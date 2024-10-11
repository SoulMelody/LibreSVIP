from typing import Optional

from pydantic import BaseModel, ConfigDict
from xsdata_pydantic.fields import field


class Rootfile(BaseModel):
    """The rootfile element describes each top-level file in the MusicXML
    container.

    A MusicXML file used as a rootfile may have score-partwise, score-
    timewise, or opus as its document element. The required full-path
    attribute provides the path relative to the root folder of the zip
    file. The optional media-type attribute identifies the media type of
    different top-level root files. It is an error to have a non-
    MusicXML media-type value in the first rootfile in a rootfiles
    element. If no media-type value is present, a MusicXML file is
    assumed.
    """

    class Meta:
        name = "rootfile"

    model_config = ConfigDict(defer_build=True)
    full_path: str = field(
        metadata={
            "name": "full-path",
            "type": "Attribute",
            "required": True,
        }
    )
    media_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "media-type",
            "type": "Attribute",
        },
    )


class Rootfiles(BaseModel):
    """The rootfiles element includes the starting points for the different
    representations of a MusicXML score.

    The MusicXML root must be described in the first rootfile element.
    Additional rootfile elements can describe alternate versions such as
    PDF and audio files. When a MusicXML file contains both a score file
    and separate files for individual parts, the score file is the one
    that is referenced in the first rootfile element. The part files can
    be linked from within the score file and need not be listed here.
    """

    class Meta:
        name = "rootfiles"

    model_config = ConfigDict(defer_build=True)
    rootfile: list[Rootfile] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "min_occurs": 1,
        },
    )


class Container(BaseModel):
    """
    The container element with a container type is the root element of the META-
    INF/container.xml file.
    """

    class Meta:
        name = "container"

    model_config = ConfigDict(defer_build=True)
    rootfiles: Rootfiles = field(
        metadata={
            "type": "Element",
            "required": True,
        }
    )
