from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    wave_to_singing: bool = Field(True, title="Convert wave pattern to singing pattern")
    use_edited_pitch: bool = Field(True, title="Use edited pitch curve")
    use_edited_dynamics: bool = Field(True, title="Use edited dynamics curve")
    import_dynamics: bool = Field(False, title="Import dynamics curve")
    import_formant: bool = Field(False, title="Import formant curve")
    import_breath: bool = Field(False, title="Import breath curve")
