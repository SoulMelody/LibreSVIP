from pydantic import BaseModel, Field


class InputOptions(BaseModel):
    wave_to_singing: bool = Field(True, title="将音频片段导入为演唱轨")
    use_edited_pitch: bool = Field(True, title="使用已编辑的音高曲线")
    use_edited_dynamics: bool = Field(True, title="使用已编辑的动态曲线")
    import_dynamics: bool = Field(False, title="导入动态曲线")
    import_formant: bool = Field(False, title="导入共振峰曲线")
    import_breath: bool = Field(False, title="导入呼吸曲线")
