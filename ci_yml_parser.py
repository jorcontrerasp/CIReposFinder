import ci_yml_parser as ymlp
import aux_functions as aux
import ci_tools as ci
import shutil
from shutil import rmtree
import logging
import yaml
import io
import os

class FileObj:
    extension = ""
    content = ""

    # GETTER & SETTER
    def getExtension(self):
        return self.extension

    def setExtension(self, extension):
        self.extension = extension

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content

class CIJob:
    stage = ""
    tasks = [] 

    # GETTER & SETTER
    def getStage(self):
        return self.stage

    def setStage(self, stage):
        self.stage = stage

    def getTasks(self):
        return self.tasks

    def setTasks(self, tasks):
        self.tasks = tasks

class CIObj:
    stages = []
    jobs = []

    # GETTER & SETTER
    def getStages(self):
        return self.stages

    def setStages(self, stages):
        self.stages = stages

    def getJobs(self):
        return self.jobs

    def setJobs(self, jobs):
        self.jobs = jobs

def getParseObj(repo, path, CITool, boGitHub):
    ciObj = None
    ciObjList = []
    try:
        # Generamos el directorio 'tmp'
        if not os.path.exists(tmpDirectory):
            os.mkdir(tmpDirectory)

        doYMLParse = CITool.value == ci.HerramientasCI.CI2.value or CITool.value == ci.HerramientasCI.CI4.value or CITool.value == ci.HerramientasCI.CI8.value
        
        if doYMLParse:
            makeYMLTmpFile(repo, path, boGitHub)
            if os.path.exists(tmpFile):
                ciObj = CIObj()
                if CITool.value == ci.HerramientasCI.CI2.value:
                    ciObj = parseTravisYAML(tmpFile)
                    os.remove(tmpFile)
                elif CITool.value == ci.HerramientasCI.CI4.value:
                    ciObj = parseGitHubActionsYAML(tmpFile)
                    os.remove(tmpFile)
                elif CITool.value == ci.HerramientasCI.CI8.value:
                    ciObj = parseGitLabYAML(tmpFile)
                    os.remove(tmpFile)
            else:
                if os.path.exists(tmpDirectory):
                    ymlFiles = os.listdir(tmpDirectory)
                    for ymlF in ymlFiles:
                        ymlF = tmpDirectory + "/" + ymlF
                        ciObj = CIObj()
                        if CITool.value == ci.HerramientasCI.CI2.value:
                            ciObj = parseTravisYAML(ymlF)
                            os.remove(ymlF)
                        elif CITool.value == ci.HerramientasCI.CI4.value:
                            ciObj = parseGitHubActionsYAML(ymlF)
                            os.remove(ymlF)
                        elif CITool.value == ci.HerramientasCI.CI8.value:
                            ciObj = parseGitLabYAML(ymlF)
                            os.remove(ymlF)
                        ciObjList.append(ciObj)

    except:
        aux.printLog("No se ha podido parsear el fichero YML: '" + path + "'", logging.INFO)

    rmtree("./" + tmpDirectory)

    if len(ciObjList)>0:
        return ciObjList
    else:
        return ciObj

def parseGitLabYAML(yamlFile):
    try:
        dataLoaded = yaml.safe_load(open(yamlFile))
    except:
        return None

    jobs = []
    stages = []
    strdl = str(dataLoaded)
    if not strdl == "None":
        stagesContent = getValueArrayParam(dataLoaded, 'stages')
        if len(stagesContent)==0:
            stages.append("?")
        elif isinstance(stagesContent, list) or isinstance(stagesContent, dict):
            for w in stagesContent:
                stages.append(w)
        else:
            stages.append(stagesContent)
        
        for topLevel in dataLoaded:
            topLevelContent = dataLoaded[topLevel]
            stage = getValueArrayParam(topLevelContent, 'stage')
            script = getValueArrayParam(topLevelContent, 'script')

            if topLevel in getMainYMLStages():
                job = CIJob()
                job.setStage(topLevel)
                jobTasks = []
                if len(script)>0:
                    if isinstance(script, list):
                        for task in script:
                            jobTasks.append(task)
                    else:
                        jobTasks.append(script)
                else:
                    if isinstance(topLevelContent, list):
                        for task in topLevelContent:
                            jobTasks.append(task)
                    else:
                        jobTasks.append(topLevelContent)
                job.setTasks(jobTasks)
                jobs.append(job)
            elif len(script)>0:
                job = CIJob()
                job.setStage(stage)
                jobTasks = []
                if isinstance(script, list):
                    for task in script:
                        jobTasks.append(task)
                else:
                    jobTasks.append(script)
                job.setTasks(jobTasks)
                jobs.append(job)
    ciObj = CIObj()
    ciObj.setStages(stages)
    ciObj.setJobs(jobs)
    return ciObj
    
def parseGitHubActionsYAML(yamlFile):
    # La etiqueta 'on' la detecta como True ¿?
    try:
        dataLoaded = yaml.safe_load(open(yamlFile))
    except:
        return None
    jobs = []
    when = []
    strdl = str(dataLoaded)
    if not strdl == "None":
        for topLevel in dataLoaded:
            topLevelContent = dataLoaded[topLevel]
            if topLevel == True: # on
                if isinstance(topLevelContent, list) or isinstance(topLevelContent, dict):
                    for w in topLevelContent:
                        when.append(w)
                else:
                    when.append(topLevelContent)
                    
            if 'jobs' == topLevel and len(topLevelContent)>0:
                for j in topLevelContent:
                    job = CIJob()
                    job.setStage(when)
                    jobSteps = []
                    jobContent = topLevelContent[j]
                    steps = getValueArrayParam(jobContent, 'steps')
                    if len(steps)>0:
                        for step in steps:
                            jobSteps.append(step)
                    job.setTasks(jobSteps)
                    jobs.append(job)
                    
    ciObj = CIObj()
    ciObj.setStages(when)
    ciObj.setJobs(jobs)
    return ciObj

def parseTravisYAML(yamlFile):
    try:
        dataLoaded = yaml.safe_load(open(yamlFile))
    except:
        return None
    jobs = []
    outJob = None
    when = []
    strdl = str(dataLoaded)
    if not strdl == "None":
        for topLevel in dataLoaded:
            topLevelContent = dataLoaded[topLevel]
            if 'stages' == topLevel:
                if isinstance(topLevelContent, list) or isinstance(topLevelContent, dict):
                    for w in topLevelContent:
                        when.append(w)
                else:
                    when.append(topLevelContent)

            if 'jobs' == topLevel:
                includeContent = getValueArrayParam(topLevelContent, 'include')
                for j in includeContent:
                    job = CIJob()
                    job.setStage(when)
                    jobSteps = []

                    install = getValueArrayParam(j, 'install')
                    if len(install)>0:
                        for task in install:
                            jobSteps.append(task)
                    
                    script = getValueArrayParam(j, 'script')
                    if len(script)>0:
                        for task in script:
                            jobSteps.append(task)
                    
                    job.setTasks(jobSteps)
                    jobs.append(job)

            elif topLevel in getMainYMLStages():
                if str(outJob) == 'None':
                    outJob = CIJob()
                    outJob.setStage(topLevel)
                jobSteps = []
                if isinstance(topLevelContent, list) or isinstance(topLevelContent, dict):
                    for tlc in topLevelContent:
                        jobSteps.append(tlc)
                else:
                    jobSteps.append(topLevelContent)
                jobTasks = outJob.getTasks()
                for step in jobSteps:
                    jobTasks.append(step)
                outJob.setTasks(jobTasks)

        if str(outJob) != 'None':
            jobs.append(outJob)

        if len(when)==0:
            when.append("?")
            
    ciObj = CIObj()
    ciObj.setStages(when)
    ciObj.setJobs(jobs)
    return ciObj
    
def getDataYAML(yamlContent):
    # Write YAML file
    with io.open('data.yaml', 'w', encoding='utf8') as outfile:
        yaml.dump(yamlContent, outfile, default_flow_style=False, allow_unicode=True)
        
    # Read YAML file
    with open("data.yaml", 'r') as stream:
        dataLoaded = yaml.safe_load(stream)
        
    return dataLoaded

def getValueArrayParam(level,param):
    try:
        value = level[param]
    except:
        value = ""
    return value

def getMainYMLStages():
    stages = []
    stages.append('before_install')
    stages.append('install')
    stages.append('after_install')
    stages.append('before_script')
    stages.append('script')
    stages.append('after_script')
    return stages

def parseConfigParam(l1, l2):
    dataLoaded = yaml.safe_load(open("config.yml"))
    l1Content = getValueArrayParam(dataLoaded, l1)
    l2Content = getValueArrayParam(l1Content, l2)
    return l2Content

def makeYMLTmpFile(repo, path, boGitHub):
    decoded = aux.getFileContent(repo, path, boGitHub)

    if isinstance(decoded, list):
        i = 0
        for d in decoded:
            if "yml" in d.getExtension() or "yaml" in d.getExtension():
                parts = aux.getStrToFile(d.getContent())
        
                try:
                    fileName = str(tmpFile + "_" + str(i)) + "." + str(d.getExtension())
                    with open(fileName, 'a') as f:
                        for part in parts:
                            f.write(part + "\n")
                finally:
                    i = i+1
                    f.close()
    else:
        parts = aux.getStrToFile(decoded)
    
        try:
            fileName = tmpFile + ".yml"
            with open(fileName, 'a') as f:
                for part in parts:
                    f.write(part + "\n")
        finally:
            f.close()

config = "process"
tmpDirectory = parseConfigParam(config, "tmpDirectory")
tmpFile = tmpDirectory + parseConfigParam(config, "tmpFile")

doTest = False
if doTest:
    print("Iniciando proceso.")

    #f = "yml_example_files/apple_turicreate_gitlab-ci.yml"
    #obj = parseGitLabYAML(f)

    #f = "yml_example_files/hacker-laws_build-on-pull-request.yaml"
    #obj = parseGitHubActionsYAML(f)

    #f = "yml_example_files/facebook_prophet_travis-ci.yml"
    #obj = parseTravisYAML(f)

    f = "yml_example_files/igListKit_travis.yml"
    obj = parseTravisYAML(f)

    #config = parseConfigParam("process", "execute")
    #print(config)

    print("Parseo finalizado.")