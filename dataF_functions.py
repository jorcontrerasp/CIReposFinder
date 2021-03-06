#AQUÍ se definirán las funciones relacionadas con los datos resultantes.

#Importamos las librerías necesarias.
import string
import pandas as pd
import aux_functions as aux
import ci_yml_parser as ymlp
import gitlab_search as gls
import github_search as ghs
import ci_tools as ci
import logging
import os
import json

def getResultDFColumns():
    _columns = []
    _columns.append("URL")
    _columns.append("Lenguaje Ppal.")
    _columns.append("Lenguajes")
    _columns.append("N_CI_+")
    for ciTool in ci.getCIToolsValueList():
        _columns.append(ciTool)

    _columns.append("STAGES")
    _columns.append("NUM_JOBS")
    _columns.append("TOTAL_TASKS")
    _columns.append("TASK_AVERAGE_PER_JOB")
    
    return _columns

def getStatisticsDFColumns():
    _columns = []
    _columns.append("Num_repos")
    _columns.append("Total_jobs")
    _columns.append("Min")
    _columns.append("Max")
    _columns.append("Media")
    _columns.append("Mediana")

    return _columns

def getStageStatisticsDFColumns():
    _columns = []
    _columns.append("Num_projects_using")
    _columns.append("Total_stages")

    return _columns

def initDF(df, id, columns, initValue):
    try:
        id_str = str(id)
        for c in columns:
            c_str = str(c)
            df.at[id_str, c_str] = initValue
    except:
        print("ERROR indexing " + str(id))

def initCIYamlColumns(id, df):
    id = id.lower()
    df.at[id, "STAGES"] = " "
    df.at[id, "NUM_JOBS"] = 0
    df.at[id, "TOTAL_TASKS"] = 0
    df.at[id, "TASK_AVERAGE_PER_JOB"] = round(0,2)

    return df

def existsDFRecord(id, df):
        try:
            str_id = str(id).lower()
            for index, row in df.iterrows():
                if str(index) == str_id:
                    return True
            return False
        except:
            return False

def existsDFRecord_2(id, df):
        try:
            str_id = str(id)
            df.loc[str_id.lower()]
            return True
        except:
            return False

def makeDataFrame(lRepositories, boGitHub):
    aux.printLog("Generando DataFrame...", logging.INFO)
    _columns = getResultDFColumns()
    repo1 = lRepositories[0]

    if boGitHub:
        id = repo1.full_name
        url1 = repo1.html_url
        language1 = repo1.language
        languages1 = repo1.languages_url
    else:
        id = repo1.attributes['path_with_namespace']
        url1 = repo1.attributes['web_url']
        language1 = gls.getFirstBackendLanguage(repo1.languages())
        languages1 = ','.join(gls.getBackendLanguages(repo1.languages()))

    id = id.lower()

    df = pd.DataFrame([],index=[id],columns=_columns)
    initDF(df, id, _columns, " ")
    df.at[id, "URL"] = url1
    df.at[id, "Lenguaje Ppal."] = str(language1).lower()
    df.at[id, "Lenguajes"] = languages1
    df.at[id, "N_CI_+"] = 0
    df.at[id, "STAGES"] = " "
    df.at[id, "NUM_JOBS"] = 0
    df.at[id, "TOTAL_TASKS"] = 0
    df.at[id, "TASK_AVERAGE_PER_JOB"] = round(0,2)

    for repo in lRepositories[1:len(lRepositories)]:
        if boGitHub:
            id = repo.full_name
            url = repo.html_url
            language = repo.language
            languages = repo.languages_url
        else:
            id = repo.attributes['path_with_namespace']
            url = repo.attributes['web_url']
            language = gls.getFirstBackendLanguage(repo.languages())
            languages = ','.join(gls.getBackendLanguages(repo.languages()))

        id = id.lower()

        df2 = pd.DataFrame([],index=[id],columns=_columns)
        initDF(df2, id, _columns, " ")
        df2.at[id, "URL"] = url
        df2.at[id, "Lenguaje Ppal."] = str(language).lower()
        df2.at[id, "Lenguajes"] = languages
        df2.at[id, "N_CI_+"] = 0
        df2.at[id, "STAGES"] = " "
        df2.at[id, "NUM_JOBS"] = 0
        df2.at[id, "TOTAL_TASKS"] = 0
        df2.at[id, "TASK_AVERAGE_PER_JOB"] = round(0,2)
        df = df.append(df2)

    return df

def makeEmptyDataFrame():
    aux.printLog("Generando DataFrame vacío...", logging.INFO)
    _columns = getResultDFColumns()
    df = pd.DataFrame([],index=[],columns=_columns)

    return df

def addDFRecord(repo, df, boGitHub):
    _columns = getResultDFColumns()
    if boGitHub:
        id = repo.full_name
        url = repo.html_url
        language = repo.language
        languages = repo.languages_url
    else:
        id = repo.attributes['path_with_namespace']
        url = repo.attributes['web_url']
        language = gls.getFirstBackendLanguage(repo.languages())
        languages = ','.join(gls.getBackendLanguages(repo.languages()))

    id = id.lower()

    df2 = pd.DataFrame([],index=[id],columns=_columns)
    initDF(df2, id, _columns, " ")
    df2.at[id, "URL"] = url
    df2.at[id, "Lenguaje Ppal."] = str(language).lower()
    df2.at[id, "Lenguajes"] = languages
    df2.at[id, "N_CI_+"] = 0
    df2.at[id, "STAGES"] = " "
    df2.at[id, "NUM_JOBS"] = 0
    df2.at[id, "TOTAL_TASKS"] = 0
    df2.at[id, "TASK_AVERAGE_PER_JOB"] = round(0,2)
    df = df.append(df2)

    return df

def updateDataFrameCiColumn(repo, literal, CITool, boGitHub, df):
    if boGitHub:
        id = repo.full_name
    else:
        id = repo.attributes['path_with_namespace']

    id = id.lower()

    df.at[id, CITool.value] = literal
    
    return df

def updateDataFrameCiObj(repo, ciObj, boGitHub, df, df6, lStagesProjectAdded):
    if boGitHub:
        id = repo.full_name
    else:
        id = repo.attributes['path_with_namespace']

    id = id.lower()

    ciObjType = type(ciObj)
    if isinstance(ciObj, ymlp.CIObj):
        lStages = []
        stages = ciObj.getStages()
        emptyCase = len(stages) == 1 and "?" in stages
        if not emptyCase:
            if isinstance(stages, list) or isinstance(stages, dict):
                for stage in stages:
                    lStages.append(str(stage).lower())
            elif isinstance(stages, str):
                lStages.append(str(stages).lower())
        ciJobs = ciObj.getJobs()
        for job in ciJobs:
            stagesJob = job.getStage()
            if isinstance(stagesJob, list) or isinstance(stagesJob, dict):
                for stageJob in stagesJob:
                    lStages.append(str(stageJob).lower())
            elif isinstance(stagesJob, str):
                lStages.append(str(stagesJob).lower())

        ciStages = ""
        dfStages = df.at[id, "STAGES"]
        if dfStages != " ":
            for stageJson in dfStages:
                if ciObj.getCiTool().lower() == stageJson:
                    ciStages = dfStages[stageJson]
                    ciStages = ciStages.replace(" ","")
                    break
        else:
            dfStages = dict()
        if ciStages != '' and len(ciStages)>0:
            ciStages = ciStages.replace("[","")
            ciStages = ciStages.replace("]","")
            ciStages = ciStages.replace("'","")
            dfStagesList = ciStages.split(",")
            for stg in dfStagesList:
                lStages.append(str(stg).lower())
            
        dataSetStages = list(set(lStages))

        key = ciObj.getCiTool().lower()

        dfStages[str(key)] = str(dataSetStages)
        df.at[id, "STAGES"] = dfStages

        df6,lStagesProjectAdded = updateStageStatisticsDF(ciObj, df6, lStagesProjectAdded)

        dfNJobs = df.at[id, "NUM_JOBS"]
        ciJobs = 0
        if dfNJobs != 0:
            for nJobsJson in dfNJobs:
                if ciObj.getCiTool().lower() == nJobsJson:
                    ciJobs = int(dfNJobs[nJobsJson])
                    break
        else:
            dfNJobs = dict()

        dfNJobs[str(key)] = ciJobs + len(ciObj.getJobs())
        df.at[id, "NUM_JOBS"] = dfNJobs

        nTasks = 0
        for job in ciObj.getJobs():
            nTasks += len(job.getTasks())

        dfNTasks= df.at[id, "TOTAL_TASKS"]
        ciTasks= 0
        if dfNTasks != 0:
            for nTasksJson in dfNTasks:
                if ciObj.getCiTool().lower() == nTasksJson:
                    ciTasks= int(dfNTasks[nTasksJson])
                    break
        else:
            dfNTasks = dict()

        vTasks = ciTasks + nTasks
        dfNTasks[str(key)] = vTasks
        df.at[id, "TOTAL_TASKS"] = dfNTasks

        tasks = dfNTasks[str(key)]
        jobs = dfNJobs[str(key)]
        if jobs == 0:
            taskAverage = -1
        else:
            taskAverage = tasks/jobs

        dfNTasksAVG= df.at[id, "TASK_AVERAGE_PER_JOB"]
        if dfNTasksAVG == 0:
            dfNTasksAVG = dict()
        dfNTasksAVG[str(key)] = round(taskAverage,2)
        df.at[id, "TASK_AVERAGE_PER_JOB"] = dfNTasksAVG
            
    
    return df,df6,lStagesProjectAdded

def doAuxWithResultsDF(df, df2, languagesDF, boGitHub):
    counterColumn = ""
    if boGitHub:
        counterColumn = "Encontrados_GitHub"
    else:
        counterColumn = "Encontrados_GitLab"
    df = updateDataFrameNumPositivesCIs(df)
    df2 = updateTotalCounterDataFrame(counterColumn, df, df2)
    df4,df5 = makeLanguageAndCIStatisticsDF(df,languagesDF,boGitHub)

    return df,df2,df4,df5

def makeCounterDataFrame():
    aux.printLog("Generando DataFrame contadores...", logging.INFO)
    columna1 = "Encontrados_GitHub"
    columna2 = "Encontrados_GitLab"
    _index = []
    rows = ci.getCIToolsValueList()
    rows.append("Totales")
    for row in rows:
        rLow = row.lower()
        _index.append(rLow)
    df = pd.DataFrame([],index=_index,columns=[columna1, columna2])

    for i in _index:
        df.at[i, columna1] = 0

    for i in _index:
        df.at[i, columna2] = 0

    return df

def add1CounterDFRecord(fila, column, df):
    fila = fila.lower()
    df.at[fila, column] += 1
    return df

def countRepos1FoundUnless(df):
    cont = 0
    pValue = "***"
    for index, row in df.iterrows():
        if row[ci.HerramientasCI.CI1.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI2.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI3.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI4.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI5.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI6.value] == pValue:
            cont += 1
        #elif row[ci.HerramientasCI.CI7.value] == pValue:
            #cont += 1
        elif row[ci.HerramientasCI.CI8.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI9.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI10.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI11.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI12.value] == pValue:
            cont += 1
        elif row[ci.HerramientasCI.CI13.value] == pValue:
            cont += 1

    return cont

def updateTotalCounterDataFrame(column,df,df2):
    totales = countRepos1FoundUnless(df)
    row = "Totales".lower()
    df2.at[row, column] = totales
    return df2

def makeEmptyLanguageDataFrame():
    aux.printLog("Generando DataFrame por lenguajes vacío...", logging.INFO)
    _columns = ci.getCIToolsValueList()
    df = pd.DataFrame([],index=[],columns=_columns)

    return df

def addLanguageDFRecord(language, df):
    _columns = ci.getCIToolsValueList()
    language = language.lower()
    df2 = pd.DataFrame([],index=[language],columns=_columns)
    initDF(df2, language, _columns, 0)
    df = df.append(df2)

    return df

def updateDataFrameNumPositivesCIs(df):
    pValue = "***"
    for index, row in df.iterrows():
        cont = 0
        if row[ci.HerramientasCI.CI1.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI2.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI3.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI4.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI5.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI6.value] == pValue:
            cont += 1
        #if row[ci.HerramientasCI.CI7.value] == pValue:
            #cont += 1
        if row[ci.HerramientasCI.CI8.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI9.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI10.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI11.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI12.value] == pValue:
            cont += 1
        if row[ci.HerramientasCI.CI13.value] == pValue:
            cont += 1
        
        df.at[index, "N_CI_+"] = cont

    return df

def makeLanguageAndCIStatisticsDF(resultsDF, languagesDF, boGitHub):
    pValue = "***"

    aux.printLog("Generando DataFrame de estadísticas por lenguaje...", logging.INFO)
    _columns = getStatisticsDFColumns()
    df1 = pd.DataFrame([],index=[],columns=_columns)

    aux.printLog("Generando DataFrame de estadísticas por CI...", logging.INFO)
    _columns = getStatisticsDFColumns()
    df2 = pd.DataFrame([],index=[],columns=_columns)
    df2 = addStatisticsDFRecord(df2, ci.HerramientasCI.CI2.value)
    df2 = addStatisticsDFRecord(df2, ci.HerramientasCI.CI4.value)
    df2 = addStatisticsDFRecord(df2, ci.HerramientasCI.CI8.value)

    for index,row in resultsDF.iterrows():
        language = row["Lenguaje Ppal."]

        if not isinstance(language, str):
            language = "None"
            aux.writeInLogFile("> makeLanguageAndCIStatisticsDF(resultsDF, languagesDF, boGitHub) - EMPTY language in proyect: " + index)

        if boGitHub:
            id = language
        else:
            id = gls.getFirstBackendLanguage(language.split(","))

        id = id.lower()
        if len(str(id))>0 and id != ' ':

            if not existsDFRecord(id, df1):
                df1 = addStatisticsDFRecord(df1, id)
            
            df1 = updateDataFrameStatistics(df1, id, row)

        boTravis = row[ci.HerramientasCI.CI2.value] == pValue
        boGitHubActions = row[ci.HerramientasCI.CI4.value] == pValue
        boGitLabCI = row[ci.HerramientasCI.CI8.value] == pValue
        
        if boTravis:
            id = ci.HerramientasCI.CI2.value.lower()
            df2 = updateDataFrameStatistics(df2, id, row)
        
        if boGitHubActions:
            id = ci.HerramientasCI.CI4.value.lower()
            df2 = updateDataFrameStatistics(df2, id, row)
        
        if boGitLabCI:
            id = ci.HerramientasCI.CI8.value.lower()
            df2 = updateDataFrameStatistics(df2, id, row)
    
    # CALCULAR MEDIA.
    df1 = updateStaticsDFJobAverage(df1)
    df2 = updateStaticsDFJobAverage(df2)
    
    # CALCULAR MEDIANA.
    df1,df2 = updateStaticsDFJobMean(df1,df2,resultsDF,languagesDF)

    return df1,df2

def updateStaticsDFJobMean(df1,df2,dfResults,dfLanguages):
    for index,row in dfLanguages.iterrows():
        dfResultsLanguageMask = dfResults["Lenguaje Ppal."] == index
        dfResultsLanguage = dfResults[dfResultsLanguageMask]

        dfAux = pd.DataFrame([],index=[],columns=["NUM_JOBS"])
        for index2,row in dfResultsLanguage.iterrows():
            dictNJobs = dfResultsLanguage.at[index2, "NUM_JOBS"]
            tJobs = 0

            json_acceptable_string = str(dictNJobs).replace("'", "\"")
            try:
                loaded_json = json.loads(json_acceptable_string)
            except:
                aux.printLog("No ha sido posible cargar el contenido JSON de " + str(dictNJobs), logging.INFO)

            if isinstance(dictNJobs,dict):
                for ciNJobs in dictNJobs:
                    nJobs = dictNJobs[ciNJobs]
                    tJobs += int(nJobs)
            elif isinstance(loaded_json,dict):
                for ciNJobs in loaded_json:
                    nJobs = loaded_json[ciNJobs]
                    tJobs += int(nJobs)
            else:
                tJobs += int(dictNJobs)
            dfAux2 = pd.DataFrame([],index=[index2],columns=["NUM_JOBS"])
            dfAux2.at[index2, "NUM_JOBS"] = tJobs
            dfAux = dfAux.append(dfAux2)

        median = dfAux["NUM_JOBS"].median()
        df1.at[index.lower(), "Mediana"] = round(median,2)

    c = 'Travis'
    dfResultsTravisMask = dfResults[c] == '***'
    dfResultsTravis = dfResults[dfResultsTravisMask]

    dfAux = pd.DataFrame([],index=[],columns=["NUM_JOBS"])
    for index,row in dfResultsTravis.iterrows():
        dictNJobs = dfResultsTravis.at[index, "NUM_JOBS"]
        dfAux2 = pd.DataFrame([],index=[index],columns=["NUM_JOBS"])

        json_acceptable_string = str(dictNJobs).replace("'", "\"")
        try:
            loaded_json = json.loads(json_acceptable_string)
        except:
            aux.printLog("No ha sido posible cargar el contenido JSON de " + str(dictNJobs), logging.INFO)
        
        if isinstance(dictNJobs, dict):
            # Esta validación en realidad es innecesaria, siempre va a venir c.lower() en el Dict. Se añade por seguridad.
            if c.lower() in dictNJobs.keys():
                dfAux2.at[index, "NUM_JOBS"] = dictNJobs[c.lower()]
        elif isinstance(loaded_json, dict):
            # Esta validación en realidad es innecesaria, siempre va a venir c.lower() en el Dict. Se añade por seguridad.
            if c.lower() in loaded_json.keys():
                dfAux2.at[index, "NUM_JOBS"] = loaded_json[c.lower()]
        else:
            dfAux2.at[index, "NUM_JOBS"] = 0

        dfAux = dfAux.append(dfAux2)

    median = dfAux["NUM_JOBS"].median()
    df2.at[c.lower(), "Mediana"] = round(median,2)
    
    c = 'GitHub Actions'
    dfResultsGitHubActionsMask = dfResults[c] == '***'
    dfResultsGitHubActions = dfResults[dfResultsGitHubActionsMask]

    dfAux = pd.DataFrame([],index=[],columns=["NUM_JOBS"])
    for index,row in dfResultsGitHubActions.iterrows():
        dictNJobs = dfResultsGitHubActions.at[index, "NUM_JOBS"]
        dfAux2 = pd.DataFrame([],index=[index],columns=["NUM_JOBS"])

        json_acceptable_string = str(dictNJobs).replace("'", "\"")
        try:
            loaded_json = json.loads(json_acceptable_string)
        except:
            aux.printLog("No ha sido posible cargar el contenido JSON de " + str(dictNJobs), logging.INFO)
        
        if isinstance(dictNJobs, dict):
            # Esta validación en realidad es innecesaria, siempre va a venir c.lower() en el Dict. Se añade por seguridad.
            if c.lower() in dictNJobs.keys():
                dfAux2.at[index, "NUM_JOBS"] = dictNJobs[c.lower()]
        elif isinstance(loaded_json, dict):
            # Esta validación en realidad es innecesaria, siempre va a venir c.lower() en el Dict. Se añade por seguridad.
            if c.lower() in loaded_json.keys():
                dfAux2.at[index, "NUM_JOBS"] = loaded_json[c.lower()]
        else:
            dfAux2.at[index, "NUM_JOBS"] = 0

        dfAux = dfAux.append(dfAux2)

    median = dfAux["NUM_JOBS"].median()
    df2.at[c.lower(), "Mediana"] = round(median,2)

    c = 'GitLab CI'
    dfResultsGitLabMask = dfResults[c] == '***'
    dfResultsGitLab = dfResults[dfResultsGitLabMask]

    dfAux = pd.DataFrame([],index=[],columns=["NUM_JOBS"])
    for index,row in dfResultsGitLab.iterrows():
        dictNJobs = dfResultsGitLab.at[index, "NUM_JOBS"]
        dfAux2 = pd.DataFrame([],index=[index],columns=["NUM_JOBS"])

        json_acceptable_string = str(dictNJobs).replace("'", "\"")
        try:
            loaded_json = json.loads(json_acceptable_string)
        except:
            aux.printLog("No ha sido posible cargar el contenido JSON de " + str(dictNJobs), logging.INFO)
        
        if isinstance(dictNJobs, dict):
            # Esta validación en realidad es innecesaria, siempre va a venir c.lower() en el Dict. Se añade por seguridad.
            if c.lower() in dictNJobs.keys():
                dfAux2.at[index, "NUM_JOBS"] = dictNJobs[c.lower()]
        elif isinstance(loaded_json, dict):
            # Esta validación en realidad es innecesaria, siempre va a venir c.lower() en el Dict. Se añade por seguridad.
            if c.lower() in loaded_json.keys():
                dfAux2.at[index, "NUM_JOBS"] = loaded_json[c.lower()]
        else:
            dfAux2.at[index, "NUM_JOBS"] = 0

        dfAux = dfAux.append(dfAux2)

    median = dfAux["NUM_JOBS"].median()
    df2.at[c.lower(), "Mediana"] = round(median,2)

    return df1,df2
        

def addStatisticsDFRecord(df, id):
    id = id.lower()
    _columns = getStatisticsDFColumns()
    df2 = pd.DataFrame([],index=[id],columns=_columns)
    initDF(df2, id, _columns, 0)
    df = df.append(df2)

    return df

def updateDataFrameStatistics(df, id, row):
    boIsCiDF = id == ci.HerramientasCI.CI2.value.lower() or id == ci.HerramientasCI.CI4.value.lower() or id == ci.HerramientasCI.CI8.value.lower()
    df.at[id, "Num_repos"] += 1
    nJobs = 0
    ciDict = row["NUM_JOBS"]
    json_acceptable_string = str(ciDict).replace("'", "\"")
    try:
        loaded_json = json.loads(json_acceptable_string)
    except:
        aux.printLog("No ha sido posible cargar el contenido JSON de " + str(ciDict), logging.INFO)
    if isinstance(ciDict, dict):
        if boIsCiDF:
            if id in ciDict.keys():
                nJobs = ciDict[id]
        else:
            for ciD in ciDict:
                if ciD in ciDict.keys():
                    nJobs += ciDict[ciD]
    elif isinstance(loaded_json, dict):
        if boIsCiDF:
            if id in loaded_json.keys():
                nJobs = loaded_json[id]
        else:
            for ciD in loaded_json:
                if ciD in loaded_json.keys():
                    nJobs += loaded_json[ciD]
    else:
        nJobs = int(ciDict)
    
    df.at[id, "Total_jobs"] += nJobs

    minJobs = df.at[id, "Min"]
    if minJobs == 0:
        df.at[id, "Min"] = nJobs
    elif(nJobs > 0 and nJobs < minJobs):
        df.at[id, "Min"] = nJobs
    
    maxJobs = df.at[id, "Max"]
    if(nJobs > 0 and nJobs > maxJobs):
        df.at[id, "Max"] = nJobs

    df.at[id, "Media"] = round(0,2)
    df.at[id, "Mediana"] = round(0,2)

    return df

def updateStaticsDFJobAverage(df):
    for index,row in df.iterrows():
        if index != "pd_empty_record":
            nRepos = row["Num_repos"]
            tJobs = row["Total_jobs"]
            jobAverage = 0
            if nRepos>0:
                jobAverage = tJobs/nRepos
            df.at[index, "Media"] = round(jobAverage,2)
    
    return df

def makeEmptyStageStatisticsDataFrame():
    aux.printLog("Generando DataFrame vacío de estadísticas de 'stages'...", logging.INFO)
    _columns = getStageStatisticsDFColumns()
    df = pd.DataFrame([],index=[],columns=_columns)

    return df

def addStageStatisticsDFRecord(df, id):
    id = id.lower()
    _columns = getStageStatisticsDFColumns()
    df2 = pd.DataFrame([],index=[id],columns=_columns)
    initDF(df2, id, _columns, 0)
    df = df.append(df2)

    return df

def updateStageStatisticsDF(ciObj, df, lStagesProjectAdded):
    lJobs = ciObj.getJobs()
    dfAux = makeEmptyStageStatisticsDataFrame()
    for job in lJobs:
        lStage = job.getStage()
        if len(lStage)==0:
            lStage = ciObj.getStages()

        if isinstance(lStage, list) or isinstance(lStage, dict):
            for stage in lStage:
                stage = stage.lower() + "[" + ciObj.getCiTool().lower() + "]"
                if not existsDFRecord(stage, dfAux):
                    dfAux = addStageStatisticsDFRecord(dfAux, stage)
                    dfAux.at[stage, "Num_projects_using"] += 1
                    dfAux.at[stage, "Total_stages"] += 1
                else:
                    dfAux.at[stage, "Total_stages"] += 1
        elif isinstance(lStage, str):
            lStage = lStage.lower() + "[" + ciObj.getCiTool().lower() + "]"
            if not existsDFRecord(lStage, dfAux):
                dfAux = addStageStatisticsDFRecord(dfAux, lStage)
                dfAux.at[lStage, "Num_projects_using"] += 1
                dfAux.at[lStage, "Total_stages"] += 1
            else:
                dfAux.at[lStage, "Total_stages"] += 1
    
    for index, row in dfAux.iterrows():
        if not existsDFRecord(index, df):
            df = addStageStatisticsDFRecord(df, index)
            df.at[index, "Num_projects_using"] += 1
            lStagesProjectAdded.append(index)
        else:
            if not (index in lStagesProjectAdded):
                df.at[index, "Num_projects_using"] += 1
                lStagesProjectAdded.append(index)

        df.at[index, "Total_stages"] += dfAux.at[index, "Total_stages"]
    
    return df,lStagesProjectAdded

def makeEXCEL(df, pFile):
    aux.printLog("Generando fichero Excel...", logging.INFO)
    folder = "results"
    makeDirectories(folder,pFile)
    df.to_excel(folder + "/" + pFile + ".xlsx")

def makeCSV(df, pFile):
    aux.printLog("Generando fichero Csv...", logging.INFO)
    folder = "results"
    makeDirectories(folder,pFile)
    df.to_csv(folder + "/" + pFile + ".csv")

def makeDirectories(folder, pFile):
    if not os.path.exists(folder):
        os.mkdir(folder)
    fileDirectories = pFile.split("/")
    i = 0
    for directory in fileDirectories:
        if i == len(fileDirectories)-1:
            break
        else:
            folder = folder + "/" + directory
            if not os.path.exists(folder):
                os.mkdir(folder)
            i = i+1

def printDF(df):
    print("----------------------------------------------------------------------------------------------------")
    print(df)
    print("----------------------------------------------------------------------------------------------------")