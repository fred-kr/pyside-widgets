def run():
    import os
    import subprocess
    from pathlib import Path

    plugin_path = Path(__file__).parent.parent.joinpath("plugins")
    os.environ["PYSIDE_DESIGNER_PLUGINS"] = str(plugin_path)
    subprocess.run("pyside6-designer", cwd=plugin_path)


if __name__ == "__main__":
    run()
