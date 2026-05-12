from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    import_tempo: bool = Field(default=True, title="Import tempo changes")
    import_dynamics: bool = Field(default=True, title="Import dynamics as volume curve")
    apply_fermata_stretch: bool = Field(
        default=True, title="Extend fermata-bearing notes (matches MuseScore playback)"
    )


class OutputOptions(BaseModel):
    pass
