# -*- coding: utf-8 -*-
import os, sys, platform, wget, shutil, subprocess
from dataclasses import dataclass
import zipfile, tarfile
from glob import glob
from .static import setup_app_dir


@dataclass
class _NodeInfo:
    node:str
    npm:str

def setup_node(version:str, target_dir:str = None) -> _NodeInfo:
    _, temp_dir, app_nodejs_dir = setup_app_dir()

    target_dir = node_dir = app_nodejs_dir if target_dir is None else os.path.realpath(target_dir)
    if not node_dir.endswith(version):
        node_dir = os.path.join(node_dir, version)

    if not os.path.exists(node_dir):
        if sys.platform == "win32":
            node_bin_zip = os.path.join(temp_dir, "node.zip")
            if platform.architecture()[0] == "32bit":
                wget.download(f"https://nodejs.org/dist/v{version}/node-v{version}-win-x86.zip", node_bin_zip)
                zipfile.ZipFile(node_bin_zip).extractall(temp_dir)
                shutil.move(os.path.join(temp_dir, f"node-v{version}-win-x86"), node_dir)
            else:
                wget.download(f"https://nodejs.org/dist/v{version}/node-v{version}-win-x64.zip", node_bin_zip)
                zipfile.ZipFile(node_bin_zip).extractall(temp_dir)
                shutil.move(os.path.join(temp_dir, f"node-v{version}-win-x64"), node_dir)
        elif sys.platform == "darwin":
            node_bin_zip = os.path.join(temp_dir, "node.tar.gz")
            if platform.processor() == "arm":
                wget.download(f"https://nodejs.org/dist/v{version}/node-v{version}-darwin-arm64.tar.gz", node_bin_zip)
                with tarfile.open(node_bin_zip, "r", encoding = "utf-8") as nbzr:
                    nbzr.extractall(temp_dir)

                shutil.move(os.path.join(temp_dir, f"node-v{version}-darwin-arm64"), node_dir)
            else:
                wget.download(f"https://nodejs.org/dist/v{version}/node-v{version}-darwin-x64.tar.gz", node_bin_zip)
                with tarfile.open(node_bin_zip, "r", encoding = "utf-8") as nbzr:
                    nbzr.extractall(temp_dir)

                shutil.move(os.path.join(temp_dir, f"node-v{version}-darwin-x64"), node_dir)
        else:
            node_bin_zip = os.path.join(temp_dir, "node.tar.xz")
            if platform.processor() == "arm":
                wget.download(f"https://nodejs.org/dist/v{version}/node-v{version}-linux-armv7l.tar.xz", node_bin_zip)
                with tarfile.open(node_bin_zip, "r", encoding = "utf-8") as nbzr:
                    nbzr.extractall(temp_dir)

                shutil.move(os.path.join(temp_dir, f"node-v{version}-linux-armv7l"), node_dir)
            else:
                wget.download(f"https://nodejs.org/dist/v{version}/node-v{version}-linux-x64.tar.xz", node_bin_zip)
                with tarfile.open(node_bin_zip, "r", encoding = "utf-8") as nbzr:
                    nbzr.extractall(temp_dir)

                shutil.move(os.path.join(temp_dir, f"node-v{version}-linux-x64"), node_dir)

        os.remove(node_bin_zip)

    if sys.platform == "win32":
        os.environ["PATH"] += f';{node_dir}'
    else:
        os.environ["PATH"] += f':{os.path.join(node_dir, "bin")}'

    return _NodeInfo(
        node = os.path.join(node_dir, "node.exe") if sys.platform == "win32" else os.path.join(node_dir, "bin", "node"),
        npm = os.path.join(node_dir, "npm.cmd") if sys.platform == "win32" else os.path.join(node_dir, "bin", "npm")
    )


def setup_python(python_dir:str, version:str, install_force:bool = False) -> str:
    if not version in ( "3.7", "3.8", "3.9", "3.10" ):
        raise RuntimeError("Unsupported python version!")

    python_dir = os.path.realpath(python_dir)
    download_python_version = "".join(version.split(".")[:2])
    temp_dir = setup_app_dir()[1]

    if os.path.exists(python_dir):
        if install_force:
            shutil.rmtree(python_dir)

    if not os.path.exists(python_dir):
        if sys.platform == "win32":
            python_install_file = os.path.join(temp_dir, "miniconda.exe")

            if sys.maxsize > 2**32: # 64bit
                wget.download(f"https://repo.anaconda.com/miniconda/Miniconda3-py{download_python_version}_22.11.1-1-Windows-x86_64.exe", python_install_file)
            else: # 32bit
                wget.download(f"https://repo.anaconda.com/miniconda/Miniconda3-py{download_python_version}_4.12.0-Windows-x86.exe", python_install_file)

            os.system(" ".join([ "start", "/wait", '""', python_install_file, "/InstallationType=JustMe", "/AddToPath=0", "/RegisterPython=0", "/S", f"/D={python_dir}" ]))
            python_path = os.path.join(python_dir, "python.exe")
        elif sys.platform == "darwin":
            python_install_file = os.path.join(temp_dir, "miniconda.sh")

            if platform.processor() == "arm": # if arm mac(m1, m2 ...)
                wget.download(f"https://repo.anaconda.com/miniconda/Miniconda3-py{download_python_version}_22.11.1-1-MacOSX-arm64.sh", python_install_file)
            else: # if intel mac
                wget.download(f"https://repo.anaconda.com/miniconda/Miniconda3-py{download_python_version}_22.11.1-1-MacOSX-x86_64.sh", python_install_file)

            subprocess.call([ "bash", python_install_file, "-b", "-p", python_dir ], cwd = temp_dir)
            python_path = os.path.join(python_dir, "bin", "python")
        else:
            python_install_file = os.path.join(temp_dir, "miniconda.sh")

            if platform.processor() == "arm":
                wget.download(f"https://repo.anaconda.com/miniconda/Miniconda3-py{download_python_version}_22.11.1-1-Linux-aarch64.sh", python_install_file)
            else:
                wget.download(f"https://repo.anaconda.com/miniconda/Miniconda3-py{download_python_version}_22.11.1-1-Linux-x86_64.sh", python_install_file)

            subprocess.call([ "bash", python_install_file, "-b", "-p", python_dir ], cwd = temp_dir)
            python_path = os.path.join(python_dir, "bin", "python")

        # remove install file
        os.remove(python_install_file)
    else:
        if sys.platform == "win32":
            python_path = os.path.join(python_dir, "python.exe")
        else:
            python_path = os.path.join(python_dir, "bin", "python")

    # upgrade pip
    subprocess.call([ python_path, "-m", "pip", "install", "pip", "--upgrade" ])

    return python_path

def compile_to_pyc(python_path:str, target_dir:str):
    compile_script_file = os.path.join(target_dir, "pyc_compile.py")
    with open(compile_script_file, "w", encoding = "utf-8-sig") as pcw:
        pcw.write(f"""
# -*- coding: utf-8 -*-
import os, py_compile
from glob import glob

__dirname = os.path.dirname(os.path.realpath(__file__))
for py_file in glob(os.path.join(__dirname, "**", "*.py"), recursive = True):
    if not os.path.basename(py_file) == "pyc_compile.py":
        py_compile.compile(py_file, py_file + "c")
        os.remove(py_file)
""")
    subprocess.call([ python_path, compile_script_file ], cwd = target_dir)
    os.remove(compile_script_file)

def clean_build_dist(app_name:str, app_version:str, dist_dir:str):
    can_proceed = False

    if sys.platform == "win32":
        if os.path.exists(os.path.join(dist_dir, "win-unpacked")):
            shutil.move(os.path.join(dist_dir, "win-unpacked"), os.path.join(dist_dir, app_name))
            files_to_left = ( app_name, f"{app_name} Setup {app_version}.exe", )
            can_proceed = True
    elif sys.platform == "darwin":
        if os.path.exists(os.path.join(dist_dir, "mac", f"{app_name}.app")):
            app_file_name = f"{app_name}-{app_version}"
            shutil.copytree(os.path.join(dist_dir, "mac", f"{app_name}.app"), os.path.join(dist_dir, f"{app_file_name}.app"))
            shutil.rmtree(os.path.join(dist_dir, "mac"))
            files_to_left = ( f"{app_file_name}.app", f"{app_file_name}.pkg", f"{app_file_name}.dmg" )
            can_proceed = True
    else:
        if os.path.exists(os.path.join(dist_dir, "linux-unpacked")):
            shutil.move(os.path.join(dist_dir, "linux-unpacked"), os.path.join(dist_dir, app_name))
            files_to_left = ( app_name, )
            can_proceed = True

    if can_proceed:
        for dist_file in os.listdir(dist_dir):
            if not dist_file in files_to_left:
                dist_file_path = os.path.join(dist_dir, dist_file)
                if os.path.isdir(dist_file_path):
                    shutil.rmtree(dist_file_path)
                elif os.path.isfile(dist_file_path):
                    os.remove(dist_file_path)
