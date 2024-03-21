import sys

from cx_Freeze import Executable, setup

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    'zip_include_packages': ['PySide6'],
}

# base="Win32GUI" should be used only for Windows GUI app
base = 'Win32GUI' if sys.platform == 'win32' else None

setup(
    name='qconcursos_questoes_db',
    version='0.1',
    options={'build_exe': build_exe_options},
    executables=[Executable('main.py', base=base)],
)
