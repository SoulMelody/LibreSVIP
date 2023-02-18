# Deprecated
import pathlib
import shlex
import winreg

import clr


def get_xstudio_library_path() -> pathlib.Path:
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Classes\svipfile\Shell\Open\Command') as key:
            open_command = winreg.QueryValueEx(key, "")[0]
            executable_path = pathlib.Path(shlex.split(open_command, posix=False)[0].strip('"'))
            return executable_path.parent
    except (FileNotFoundError, OSError):
        return None


dll_root = get_xstudio_library_path()
for dll_name in ['SingingTool.Model.dll', 'SingingTool.Const.dll', 'SingingTool.Library.dll']:
    dll_path = dll_root / dll_name
    if dll_path.exists():
        clr.AddReference(str(dll_path))
    else:
        raise FileNotFoundError(f'Cannot find {dll_name} in {dll_root}')


def read_xstudio_project(path: pathlib.Path):
    from System.IO import BinaryReader, BinaryWriter, FileStream, FileMode, FileAccess
    from System.Runtime.Serialization.Formatters.Binary import BinaryFormatter

    from SingingTool.Model import AppModel, ProjectModelFileMgr

    path = str(path)

    stream = FileStream(path, FileMode.Open, FileAccess.Read)
    reader = BinaryReader(stream)
    version = reader.ReadString()
    version_number = reader.ReadString()
    version += version_number
    formatter = BinaryFormatter()
    model = formatter.Deserialize(stream)
    stream.Close()
    reader.Close()
