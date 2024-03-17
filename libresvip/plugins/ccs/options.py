from pydantic import BaseModel, Field

from libresvip.model.option_mixins import EnablePitchImportationMixin


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(BaseModel):
    default_singer_name: str = Field("さとうささら", title="Default Singer Name")
    default_singer_id: str = Field("A", title="Default Voicebank ID")
    default_singer_version: str = Field("1.0.0", title="Default Voicebank Version")
