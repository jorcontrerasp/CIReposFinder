import aux_functions as aux
import gitlab_search as gls
import ci_yml_parser as ymlp
import shutil
from shutil import rmtree
import os


doCleanProject = True
config = "process"
tmpDirectory = ymlp.parseConfigParam(config, "tmpDirectory")
tmpFile = tmpDirectory + ymlp.parseConfigParam(config, "tmpFile")

def cleanProject():
    try:
        print("Limpiando proyecto...")

        #ELIMINAR CARPETAS Y FICHEROS BASURA
        if os.path.exists(tmpDirectory):
            rmtree("./" + tmpDirectory)
        if os.path.exists("results"):
            rmtree("results")
        if os.path.exists("/logs"):
            rmtree("/logs")
        if os.path.exists("github_repos.pickle"):
            os.remove("github_repos.pickle")
        if os.path.exists("gitlab_repos.pickle"):
            os.remove("gitlab_repos.pickle")

        #CREAR CARPETAS
        if not os.path.exists("results"):
            os.mkdir("results")
        if not os.path.exists("logs"):
            os.mkdir("logs")

        print("Proceso terminado...")
    except:
        raise

if doCleanProject:
    cleanProject()