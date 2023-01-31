# -*- coding: utf-8 -*-
import os, sys, shutil, json, platform, subprocess
from .utils import setup_node, setup_python, compile_to_pyc, clean_build_dist
from .static import index_js, package_json


def build(target_dir:str, dest_dir:str, build_type:str = "debug", python_version:str = f"{sys.version_info.major}.{sys.version_info.minor}", node_version = "18.12.1", icon:str = None, make_installer:bool = False):
    target_dir, dest_dir = os.path.realpath(target_dir), os.path.realpath(dest_dir)
    temp_build_dir = os.path.join(target_dir, ".build")
    build_type = build_type.lower()

    config_file = os.path.join(target_dir, "pyebuilder.json")
    if not os.path.exists(config_file):
        raise RuntimeError("no pyebuilder config file!")

    with open(config_file, "r", encoding = "utf-8") as cfr:
        configs = json.load(cfr)

    if not "name" in configs.keys() or not "version" in configs.keys():
        raise RuntimeError("`name` and `version` should be specified!")

    if " " in configs["name"]:
        raise NameError("`name` cannot contain spaces!")

    build_dest_dir = os.path.join(temp_build_dir, build_type)
    if not os.path.exists(build_dest_dir):
        os.makedirs(build_dest_dir)

    # node_info = setup_node(os.path.join(dest_dir, ".nodejs"))
    node_info = setup_node(node_version)

    with open(os.path.join(build_dest_dir, "package.json"), "w", encoding = "utf-8") as pkgw:
        author = configs.pop("author", platform.node()).split(".")[0]
        pkgw.write(
            package_json(
                configs["name"], configs["version"],
                configs.pop("description", ""),
                configs.pop("author", author),
                configs.pop("email", f"{author}@mail.com"),
                configs.pop("homepage", f"https://github.com/{author}/{configs['name']}"),
                icon,
                make_installer
            )
        )

    with open(os.path.join(build_dest_dir, "index.js"), "w", encoding = "utf-8") as ijw:
        ijw.write(index_js(configs.pop("entry", "main.py"), build_type))

    subprocess.call([ node_info.npm, "install" ], cwd = build_dest_dir)

    python_path = setup_python(os.path.join(build_dest_dir, "python"), python_version, False)
    require_file = os.path.join(target_dir, "requirements.txt")
    if os.path.exists(require_file):
        subprocess.call([ python_path, "-m", "pip", "install", "-r", require_file, "--no-warn-script-location" ])

    dest_script_dir = os.path.join(build_dest_dir, "scripts")
    if os.path.exists(dest_script_dir):
        shutil.rmtree(dest_script_dir)

    os.mkdir(dest_script_dir)

    exclude_files = configs.pop("excludes", []) + [ "pyebuilder.json", ".build" ]
    for sub_file in os.listdir(target_dir):
        if not sub_file in exclude_files:
            sub_file_path = os.path.join(target_dir, sub_file)
            if os.path.isdir(sub_file_path):
                shutil.copytree(sub_file_path, os.path.join(dest_script_dir, sub_file))
            elif os.path.isfile(sub_file_path):
                shutil.copyfile(sub_file_path, os.path.join(dest_script_dir, sub_file))

    compile_to_pyc(python_path, dest_script_dir)

    build_dist_dir = os.path.join(build_dest_dir, "dist")
    if os.path.exists(build_dist_dir):
        shutil.rmtree(build_dist_dir)

    subprocess.call([ node_info.npm, "run", "build" ], cwd = build_dest_dir)
    clean_build_dist(configs["name"], configs["version"], build_dist_dir)
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    shutil.move(build_dist_dir, dest_dir)
