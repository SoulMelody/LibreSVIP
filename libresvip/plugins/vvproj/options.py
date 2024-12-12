from pydantic import BaseModel

from libresvip.model.option_mixins import EnablePitchImportationMixin


class InputOptions(EnablePitchImportationMixin, BaseModel):
    pass


class OutputOptions(BaseModel):
    pass
