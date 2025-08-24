#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\backup.py
# JUMLAH BARIS : 28
#######################################################################

import os
import logging
from tools.backup_system.archiver import Archiver
from tools.guardian_angel.guardian import GuardianAngel
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
def main():
    """
    The main entry point to start the backup guardian angel.
    This script's single responsibility is to launch the system.
    """
    try:
        logging.info("Initializing backup system...") # ADDED: Log the start of the process
        project_root = os.getcwd()
        archiver_instance = Archiver(project_root=project_root)
        guardian = GuardianAngel(project_root=project_root, archiver_instance=archiver_instance)
        logging.info("Guardian Angel is starting. Watching for file changes...") # ADDED: More informative log
        guardian.start()
    except Exception as e:
        logging.critical(f"A critical error occurred while starting the backup system: {e}", exc_info=True)
if __name__ == "__main__":
    main()
