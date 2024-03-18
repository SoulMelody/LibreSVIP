from pydantic import BaseModel

from libresvip.model.option_mixins import EnablePitchImportationMixin, EnableVibratoImportationMixin


class InputOptions(EnablePitchImportationMixin, EnableVibratoImportationMixin, BaseModel):
    pass


class OutputOptions(BaseModel):
    pass
