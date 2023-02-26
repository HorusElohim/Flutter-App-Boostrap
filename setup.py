import os
import platform
import logging
import subprocess
from pathlib import Path
from colorlog import ColoredFormatter

BANNER = \
""" 
  ______ _       _   _                                     ____                  _                   
 |  ____| |     | | | |                /\                 |  _ \                | |                  
 | |__  | |_   _| |_| |_ ___ _ __     /  \   _ __  _ __   | |_) | ___   ___  ___| |_ _ __ __ _ _ __  
 |  __| | | | | | __| __/ _ \ '__|   / /\ \ | '_ \| '_ \  |  _ < / _ \ / _ \/ __| __| '__/ _` | '_ \ 
 | |    | | |_| | |_| ||  __/ |     / ____ \| |_) | |_) | | |_) | (_) | (_) \__ \ |_| | | (_| | |_) |
 |_|    |_|\__,_|\__|\__\___|_|    /_/    \_\ .__/| .__/  |____/ \___/ \___/|___/\__|_|  \__,_| .__/ 
                                            | |   | |                                         | |    
                                            |_|   |_|                                         |_|     
"""

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white"
    },
    secondary_log_colors={},
    style='%'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def _run_command(command):
    """Runs a command in the shell and returns the result code and text."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.debug(f"_run_command: SUCESS\t{result.returncode}:{result.stdout}")
        return result.returncode, result.stdout
    except subprocess.CalledProcessError as e:
        logger.debug(f"_run_command: FAILED\t{e.returncode}:{e.stderr}")
        return e.returncode, e.stderr


def linux():
    logger.info("Linux bootstrap")

    # install flutter
    r,m = _run_command("snap install flutter --classic")
    if r == 0:
        logger.info("flutter installed")
        
        # flutter configure 
        r, m = _run_command("flutter sdk-path")
        
        if r == 0:
            flutter_path = m.strip("\n")
            logger.info(f"flutter configured on {flutter_path}")
            
            # flutter doctor
            r, m_doctor =_run_command("flutter doctor")

            home_dir = Path(os.path.expanduser( '~' ))
            studio_dir = home_dir / 'android-studio'

            if "[!] Android toolchain" in m_doctor:
                # missing android studio
                if not studio_dir.exists():
                    logger.warning("missing android-studio")
                    logger.info("trying local install")
                    logger.info(f"installing android-studio-sdk to: {studio_dir}")
                    r, m = _run_command(f"tar -xf linux/android-studio-2022.1.1.20-linux.tar.gz --directory {home_dir}")
                    
                    if r == 0:
                        logger.info("android studio extraction success")
                        logger.info(f"add to your path -> PATH=$PATH:{studio_dir / 'bin'}")
                        logger.info(f"then start Android-Studio with studio.sh")
                    else:               
                        logger.error("(local install not-found) please download Android Studio from: https://developer.android.com/studio")
                        logger.error("and place it in the linux folder --> linux/android-studio-2022.1.1.20-linux.tar.gz")
                else:
                    studio_dir_jre = studio_dir / 'jre'
                    if not studio_dir_jre.exists():
                        logger.warning("patching android-studio java jre folder")
                        studio_dir_jre.mkdir()
                        _run_command(f"cp -rf {studio_dir/ 'jbr/*'} {studio_dir_jre}")
                        logger.info("java patched")
                    logger.info("android studio ok")
                
                # missing command line tools 
                if "cmdline-tools component is missing" in m_doctor:
                    logger.info("install from android-studio->SDK-Manger->Tools-Command-Line-Tools")
    return 0

def darwin():
    logger.info("Darwin bootstrap")
    return 0

def windows():
    logger.info("Windows bootstrap")
    return 0

def main():
    p = platform.system().lower()
    if p == "linux":
        return linux()
    if p == "darwin":
        return darwin()
    if p == "windwos":
        return windows()

if __name__ == "__main__":
    print(BANNER)
    main()