# -*- coding: utf-8 -*-
import os, sys, json
from typing import Tuple
from . import __path__


def setup_app_dir() -> Tuple[str, str, str]:
    app_dir = os.path.join(__path__[0], ".pyebuilder_app")
    if not os.path.exists(app_dir):
        os.mkdir(app_dir)

    temp_dir, app_nodejs_dir =\
        os.path.join(app_dir, "temp"), os.path.join(app_dir, "nodejs")

    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    if not os.path.exists(app_nodejs_dir):
        os.mkdir(app_nodejs_dir)

    return app_dir, temp_dir, app_nodejs_dir

def index_js(main_file:str, build_type:str) -> str:
    return """
const { app } = require("electron"),
    os = require("os"),
    path = require("path"),
    { PythonShell } = require("python-shell");


app.whenReady().then(() => {
    let is_release = {$is_release}
    let appDir = __dirname.endsWith(".asar") ? __dirname + ".unpacked" : __dirname;
    let pythonPath;

    if (os.platform() == "win32") {
        pythonPath = path.join(appDir, "python", is_release ? "pythonw.exe" : "python.exe");
    }
    else {
        pythonPath = path.join(appDir, "python", "bin", "python");
    }

    if (process.platform == "darwin" && is_release) {
        app.dock.hide();
    }

    const ps = new PythonShell(
        "{$main_file}",
        {
            pythonOptions: [ "-u" ],
            pythonPath: pythonPath,
            scriptPath: path.join(appDir, "scripts")
        }
    );
    ps.on("message", (message) => { console.log(message); });
    ps.on("error", (err) => { throw err; });
    ps.end((err, code, res) => { app.quit(); });
});
""".replace(
    "{$main_file}", main_file + "c"
).replace(
    "{$is_release}", "true" if build_type == "release" else "false"
)

def package_json(name:str, version:str = "0.0.1", description:str = "", author:str = "", email:str = "", homepage:str = "", icon:str = None, make_installer:bool = False) -> str:
    package_dict = {
        "name": name,
        "version": version,
        "description": description,
        "main": "index.js",
        "author": f"{author} <{email}>",
        "homepage": homepage,

        "scripts": {
            "start": "electron .",
            "build": "electron-builder"
        },

        "build": {
            "productName": name,
            "files": [
                {
                    "from": "./scripts",
                    "to": "scripts"
                },
                {
                    "from": "./python",
                    "to": "python"
                },
                "index.js",
                "package.json"
            ],
            "mac": {
                "target": [ "dir" ],
                "category": "Application"
            },
            "linux": {
                "target": [ "dir" ],
                "category": "Application"
            },
            "win": {
                "target": [ "portable" ]
            },
            "asar": True,
            "asarUnpack": [
                "node_modules",
                "python",
                "scripts",
                "index.js",
                "package.json"
            ]
        },

        "dependencies": {
            "fs-extra": "^11.1.0",
            "python-shell": "^3.0.1",
        },
        "devDependencies": {
            "electron": "^22.0.0",
            "electron-builder": "^23.6.0"
        }
    }

    if icon is not None:
        if sys.platform == "win32":
            package_dict["build"]["win"]["icon"] = icon
        elif sys.platform == "darwin":
            package_dict["build"]["mac"]["icon"] = icon
        else:
            package_dict["build"]["linux"]["icon"] = icon

    if make_installer:
        if sys.platform == "win32":
            package_dict["build"]["win"]["target"] = [ { "target": "nsis", "arch": [ "x64", "ia32" ] } ]
        elif sys.platform == "darwin":
            package_dict["build"]["mac"]["target"] = [ "pkg", "dmg" ]
        else:
            # check deb or rpm
            package_dict["build"]["linux"]["target"] = [ "deb", "rpm" ]

    return json.dumps(package_dict, indent = 4)
