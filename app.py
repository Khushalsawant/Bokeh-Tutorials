# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 14:11:12 2019

@author: KS5046082
"""

from flask import Flask, render_template, request, jsonify, abort, Response, redirect, current_app, send_file
from flask import Flask, render_template, request, jsonify, abort, Response, redirect, current_app, send_file
import requests
from requests.auth import HTTPBasicAuth
import json
import pycyberark
import os
import configparser
import logging.handlers
from logging.config import fileConfig
from collections import defaultdict
import sqlalchemy
import pandas as pd
from flask import Blueprint
from werkzeug.utils import secure_filename
import redis
from rq import Queue, Connection
import uuid
import datetime
import csv
import traceback
import DataRoleCompare
import DomainCompare
import re
import functools
import time
import inspect
from annotations import try_this, timer, debug_announce
from LineChartBokeh import Line_chart_generation

main_blueprint = Blueprint("main", __name__)
cwd = os.path.dirname(os.path.abspath(__file__))
logging.logfile_suffix = os.environ.get('LOGFILE_SUFFIX', "")
fileConfig(cwd+'/config/logging_config.ini')
logger = logging.getLogger()
logger.info("[app.py] Starting STT...")
logger.debug("[app.py] Logging config file: "+cwd+"/config/logging_config.ini")

config = configparser.ConfigParser()
logger.debug("[app.py] Application config file: " + cwd + "/config/config.ini")
config.read(cwd+'/config/config.ini')
env = os.environ.get('ENV', "DEV")
logger.info("[app.py] Config: Environment: " + env)
feature_name = os.environ.get('FEATURE_NAME', "")
logger.info("[app.py] Config: Feature name: " + feature_name)

cyberark_db_config = config[env]['CYBERARK_DB_CONFIG']
cyberark_dpauth_config = config[env]['CYBERARK_DPAUTH_CONFIG']
cyberark_enabled = (config[env]['CYBERARK_ENABLED'] == "True")
cyberark_use_ssl = (config[env]['CYBERARK_USE_SSL'] == "True")
cyberark_ssl_cert = 'certs/ca-bundle.crt'
ad_auth_enabled = (config[env]['AD_AUTH_ENABLED'] == "True")
toggle_mass_notes_enabled = (config[env]['TOGGLE_MASS_NOTES_ENABLED'] == "True")
apitoken = config[env]['APITOKEN'] #TODO: Do we need this
# snapshot_files_path = '/stt/snapshots/'
snapshot_files_path= '/stt/domain-content/'
working_files_path = '/stt/workingfiles/'
data_role_files_path = '/stt/datarole-content/'

logger.debug("[app.py] Config: CyberArk Enabled?: " + str(cyberark_enabled))
logger.debug("[app.py] Config: CyberArk Using SSL?: " + str(cyberark_use_ssl))
logger.debug("[app.py] Config: CyberArk DB Config File: " + cyberark_db_config)
with open(cyberark_db_config, 'r') as config_file:
    logger.debug(f"[app.py] DB CyberArk Config: {config_file.read()}")
logger.debug("[app.py] Config: CyberArk DP Proxy Config File: " + cyberark_dpauth_config)
with open(cyberark_dpauth_config, 'r') as config_file:
    logger.debug(f"[app.py] DPAuth CyberArk Config: {config_file.read()}")
logger.debug("[app.py] Config: STT API Token Length: " + str(apitoken.__len__()))
logger.debug("[app.py] Config: Working files path: " + working_files_path)
logger.debug("[app.py] Config: Snapshot files path: " + snapshot_files_path)
logger.debug("[app.py] Config: AD Auth Enabled?: " + str(ad_auth_enabled))
logger.debug("[app.py] Toggle: Mass Notes?: " + str(toggle_mass_notes_enabled))


@try_this
def check_stt_bearer_token(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'apitoken' in request.headers:
            if request.headers['apitoken'] != apitoken:
                logger.error(f"[{func.__name__}()] API token from request header does not match application API token! Aborting... 403")
                abort(403)
        else:
            logger.error(f"[{func.__name__}()] No API token found in the request headers! Aborting... 401")
            abort(401)
        value = func(*args, **kwargs)
        return value
    return wrapper

@try_this
def stt_api_call(env="", uri="", method="GET", data=""):
    caller = inspect.stack()[1].function
    if caller == "wrapper_trythis": caller = inspect.stack()[2].function
    thisfunction = inspect.stack()[0].function

    if env == "":
        env = os.environ.get('ENV', "DEV")
    apitoken = config[env]['APITOKEN']
    stt_api_host = config[env]['STT_API_ENDPOINT']
    url = stt_api_host + uri
    headers = {'apitoken': apitoken}
    logger.info(f"[{caller}() : {thisfunction}()] STT API Request: {url}")

    if method == "GET":
        sttresponse = requests.get(url, headers=headers)
    elif method == "POST":
        sttresponse = requests.get(url, headers=headers, data=data)
    elif method == "PUT":
        sttresponse = requests.put(url, headers=headers, data=data)
    else:
        return False

    if sttresponse.status_code >= 200 and sttresponse.status_code <= 299:
        logger.debug(f"[{caller}() : {thisfunction}()] " + str(sttresponse.status_code) + " : " + url)
    else:
        logger.debug(f"[{caller}() : {thisfunction}()] " + str(sttresponse.status_code) + " : " + url)

    return sttresponse

#TODO: Pull docupace_call() into a utilities class
@try_this
def docupace_call(env="", uri="", method="GET", data="", contenttype="application/json"):
    caller = inspect.stack()[1].function
    if caller == "wrapper_trythis": caller = inspect.stack()[2].function
    thisfunction = inspect.stack()[0].function
    logger.debug(f"[{thisfunction}] environment received: {env}")
    if env == "":
        env = os.environ.get('ENV', "DEV")
    athuser = config[env]['ATHUSER']
    uri_endpoint = config[env]['DP_ENDPOINT']
    url = uri_endpoint + uri
    logger.info(f"[{caller}() : {thisfunction}()] DP Request: {method} {str(url).strip()}")

    dpproxy_user = ""
    dpproxy_pass = ""
    try:
        if cyberark_enabled:
            logger.debug(f"[{caller}() : {thisfunction}()] Using CyberArk to fetch DP Proxy credentials...")
            cyberark_dpauth_config = config[env]['CYBERARK_DPAUTH_CONFIG']
            caconfig = pycyberark.get_config(cyberark_dpauth_config)
            if cyberark_use_ssl:
                ssl_value = cyberark_ssl_cert
            else:
                ssl_value = cyberark_use_ssl
            response = pycyberark.get_credentials(caconfig, ssl_value)
            dpproxy_user = response.get("user_name")
            dpproxy_pass = response.get("password")
            logger.debug(f"[{caller}() : {thisfunction}()] Received DP Proxy user name with length of " + str(dpproxy_user.__len__()))
            logger.debug(f"[{caller}() : {thisfunction}()] Received DP Proxy pass with length of " + str(dpproxy_pass.__len__()))
        else:
            logger.warning(f"[{caller}() : {thisfunction}()] CyberArk disabled, using DP Proxy credentials from config file...")
            dpproxy_user = config[env]("DPPROXY_USERNAME")
            dpproxy_pass = config[env]("DPPROXY_PASSWORD")
    except Exception as ex:
        logger.critical(f"[{caller}() : {thisfunction}()] " + traceback.format_exc())
        return False

    if method == "GET":
        dpresponse = requests.get(url, headers={"athuser": athuser}, auth=HTTPBasicAuth(dpproxy_user, dpproxy_pass))
    elif method == "POST":
        dpresponse = requests.post(url, headers={"athuser": athuser, "Content-Type": contenttype}, auth=HTTPBasicAuth(dpproxy_user, dpproxy_pass), data=data)
    elif method == "PUT":
        dpresponse = requests.put(url, headers={"athuser": athuser, "Content-Type": contenttype}, auth=HTTPBasicAuth(dpproxy_user, dpproxy_pass), data=data)
    else:
        return False

    if dpresponse.status_code >= 200 and dpresponse.status_code <= 299:
        logger.debug(f"[{caller}() : {thisfunction}()] {str(dpresponse.status_code)} : {method} {url} \n{data}")
    else:
        logger.error(f"[{caller}() : {thisfunction}()] {str(dpresponse.status_code)} : {method} {url} \n{data}\n{dpresponse.text}")
    return dpresponse

@timer
@try_this
def create_connection(env="", user="", passwd="", server="", port="", database="", schema=""):
    caller = inspect.stack()[1].function
    if caller == "wrapper_trythis": caller = inspect.stack()[2].function
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{caller}() : {thisfunction}()] Creating DB connection...")
    if env == "":
        env = os.environ.get('ENV', "DEV")
    server = config[env]['DB_SERVER']
    database = config[env]['DB_DATABASE']
    schema = config[env]['DB_SCHEMA']
    port = config[env]['DB_PORT']

    try:
        if cyberark_enabled:
            logger.debug(f"[{caller}() : {thisfunction}()] Using CyberArk to fetch Postgres DB credentials...")

            caconfig = pycyberark.get_config(cyberark_db_config)
            if cyberark_use_ssl:
                ssl_value = cyberark_ssl_cert
            else:
                ssl_value = cyberark_use_ssl
            response = pycyberark.get_credentials(caconfig, ssl_value)
            user = response.get("user_name")
            passwd = response.get("password")
            logger.debug(f"[{caller}() : {thisfunction}()] Received DB user name with length of " + str(user.__len__()))
            logger.debug(f"[{caller}() : {thisfunction}()] Received DB pass with length of " + str(passwd.__len__()))
        else:
            logger.warning(f"[{caller}() : {thisfunction}()] CyberArk disabled, using DB credentials from config file...")
            user = config[env]['DB_USERNAME']
            passwd = config[env]['DB_PASSWORD']
    except Exception as ex:
        logger.critical(f"[{caller}() : {thisfunction}()] " + traceback.format_exc())

    connection_string = 'postgresql://' + user + ':' + passwd + '@' + server + ':' + port + '/' + database
    logger.debug(f"[{caller}() : {thisfunction}()] DB connection string: postgresql://{user}:*******@{server}:{port}/{database}")
    try:
        test_engine = sqlalchemy.create_engine(connection_string)
        logger.info(f"[{caller}() : {thisfunction}()] Connecting to the DB engine...")
        test_engine.connect()
    except Exception:
        logger.fatal(f"[{caller}() : {thisfunction}()] Cannot establish connection to {server}:{port}/{database} with user {user} " + traceback.format_exc())
        exit(1)
    else:
        global engine
        engine = test_engine
        logger.debug(f"[{caller}() : {thisfunction}()] Connection to {server}:{port}/{database} with user {user} established")
    return engine

@main_blueprint.route("/callback/")
@timer
def index():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}] Request made to '/callback' endpoint...")
    global env
    # referer = request.referrer
    if env=="PROD":
        referer = 'https://stt.onintranet.com/'
    else:
        referer = 'https://stt-' + env.lower() + '.onintranet.com/'
    logger.info(f"[{thisfunction}()] Redirecting user to " + referer + " with status code 302...")
    return redirect(referer, code=302)

@main_blueprint.route("/")
@timer
def landing():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/' endpoint...")
    global env
    global ad_auth_enabled
    global feature_name
    githash = ""
    buildno = ""
    if feature_name != "":
        environment = feature_name
    else:
        environment = env.lower()

    with open('static/git-commit', 'r') as githashfile:
        githash = githashfile.read().strip()
    with open('static/build-no', 'r') as buildnofile:
        buildno = buildnofile.read().strip()

    logger.debug(f"[{thisfunction}()] Rendering 'landing.html' template with environment as {environment} and authcheck as {str(ad_auth_enabled)}")
    return render_template("landing.html", env=environment, githash=githash, buildno=buildno, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/skillsassignment")
@timer
def skillsassignment():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/skillsassignment' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    logger.debug(f"[{thisfunction}()] Rendering 'skillsassignment.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    return render_template('skillsassignment.html', env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/skillsbundlemanager")
@timer
def bundlemanagement():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/skillsbundlemanager' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    logger.debug(f"[{thisfunction}()] Rendering 'skillsbundlemanager.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    return render_template('skillsbundlemanager.html', env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/wipriorityupdater")
@timer
def wipriorityupdate():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/wipriorityupdater' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    logger.debug(f"[{thisfunction}()] Rendering 'wipriorityupdater.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    return render_template('wipriorityupdater.html', env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/notesbatchuploader")
@timer
def notesbatchuploader():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/notesbatchuploader' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    files = os.listdir('static/xlstemplates_massnotes/')
    files.sort()
    logger.debug(f"[{thisfunction}()] Rendering 'notesbatchuploader.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    return render_template("notesbatchuploader.html", templates=map(json.dumps, files), env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/wibatchuploader")
@timer
def wibatchuploader():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/wibatchuploader' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    files = os.listdir('static/xlstemplates_wiupload/')
    files.sort()
    logger.debug(f"[{thisfunction}()] Rendering 'wibatchuploader.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    return render_template("wibatchuploader.html", templates=map(json.dumps, files), env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/domaincompare")
@timer
def domaincompare():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/domaincompare' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    dirs = os.listdir(snapshot_files_path)
    data = []
    dr_list = []
    for dir in dirs:
        if os.path.isdir(snapshot_files_path + "/" + dir):
            json = {}
            list = os.listdir(snapshot_files_path + "/" + dir)
            json['env'] = dir
            files = []
            for file in list:
                if len(file.split('_')) > 2:
                    file_json = {}
                    file_json['text'] = file
                    file_json['value'] = file
                    file_json['domain'] = file.split('_')[1]
                    files.append(file_json)
                    dr_list.append(file.split('_')[1])
            json['files'] = files
            data.append(json)
    data.append({"env": "DOMAINS", "domains": sorted(set(dr_list))})
    logger.debug(f"[{thisfunction}()] Rendering 'domaincompare.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    return render_template("domaincompare.html", snapshots=data, env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/datarolecompare")
@timer
@try_this
def datarolecompare():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/datarolecompare' endpoint...")
    global env
    environment = env.lower()
    dirs = os.listdir(data_role_files_path)
    data = []
    dr_list = []
    for dir in dirs:
        json = {}
        list = os.listdir(data_role_files_path + "/" + dir)
        json['env'] = dir
        files = []
        for file in list:
            if len(file.split('_')) > 2:
                file_json = {}
                file_json['text'] = file
                file_json['value'] = file
                file_json['dataRole'] = file.split('_')[1]
                files.append(file_json)
                dr_list.append(file.split('_')[1])
        json['files'] = files
        data.append(json)
    data.append({"env": "DATAROLES", "dataRoles": sorted(set(dr_list)) })
    logger.debug(f"[{thisfunction}()] Rendering 'datarolecompare.html' template with environment as " + environment + "...")
    return render_template("datarolecompare.html", snapshots=data, env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/domainsnapshot")
@timer
@try_this
def domainsnapshot():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/domainsnapshot' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    logger.debug("[domainsnapshot()] Rendering 'domainsnapshot.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    return render_template("domainsnapshot.html", env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)

@main_blueprint.route("/metricsreports")
@timer
@try_this
def metricsreport():
    thisfunction = inspect.stack()[0].function
    logger.info(f"[{thisfunction}()] Request made to '/metricsreports' endpoint...")
    global env
    global ad_auth_enabled
    environment = env.lower()
    logger.debug("[metricsreport()] Rendering 'metricsreport.html' template with environment as " + environment + " and authcheck as " + str(ad_auth_enabled))
    # Updated By khushal Start
    script_line_chart, div_line_chart = Line_chart_generation()
    # Updated By khushal End
    return render_template("metricsreport.html", env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled,
                           script_line_chart=script_line_chart, div_line_chart=div_line_chart)
    #return render_template("metricsreport.html", env=environment, authcheck=ad_auth_enabled, mass_notes_enabled=toggle_mass_notes_enabled)
    # Updated By khushal End

@main_blueprint.route("/api/v1/users", methods=['GET'])
@timer
@debug_announce
@check_stt_bearer_token
@try_this
def get_all_users():
    # Retrieves all valid users and returns them in a simplified list

    thisfunction = inspect.stack()[0].function
    users = []
    returnobject = defaultdict(dict)
    dpresponse = docupace_call(uri='domains/300/records/data.json?attrSet=9501', method="GET")
    if dpresponse.status_code >= 300 or dpresponse.status_code < 200:
        logger.error(f"[{thisfunction}()] Received {str(dpresponse.status_code)} status code from domains/300/records/data.json?attrSet=9501 " )
        abort(500)
    dpjson = dpresponse.json()
    for user in dpjson['records']:
        useri = defaultdict(dict)
        id_value = user['id']
        username_value = ""
        for attrvalue in user['attrValues']:
            field_number = attrvalue["attrId"]
            if field_number == 9501:
                username_value = attrvalue['value']
        useri["userid"] = id_value
        useri["username"] = username_value
        useri["fullname"] = str(id_value) + "." + username_value
        users.append(useri)
    logger.debug(f"[{thisfunction}()] Success. Returning user data for " + str(len(users)) + " users")
    returnobject["users"] = users
    return Response(response=json.dumps(returnobject), status=200, mimetype='text/json')

@main_blueprint.route("/api/v1/users/<int:userid>/skills", methods=['GET'])
@timer
@debug_announce
@check_stt_bearer_token
@try_this
def retrieve_user_skills(userid):
    # Retrieves all the skills associated with a particular user

    thisfunction = inspect.stack()[0].function
    returnobject = defaultdict(dict)
    dpresponse = docupace_call(uri='domains/300/records/' + str(userid) + '/data.json?attrSet=84001:840-100201', method="GET")
    if dpresponse.status_code < 200 or dpresponse.status_code > 299:
        logger.error(f"[{thisfunction}()] Received non-2xx status code from domains/300/records/data.json?attrSet=9501 ... " + str(dpresponse.status_code))
        abort(500)
    dpjson = dpresponse.json()
    skills = []
    logger.debug(f"[{thisfunction}()] Creating skills array from response data...")
    for attrValue in dpjson['attrValues']:
        if attrValue['attrId'] == 84001:
            skill = defaultdict(dict)
            skill["docupaceid"] = str(attrValue['value'])
            for childAttrValue in attrValue['attrValues']:
                if childAttrValue["attrId"] == 100201:
                    skill["skillname"] = str(childAttrValue["value"])
            skills.append(skill)

    skills = sorted(skills, key=lambda k: k['docupaceid'])
    returnobject["skills"] = skills
    logger.debug(f"[{thisfunction}()] Success. Returning skills data for " + str(len(skills)) + " skills")
    return Response(response=json.dumps(returnobject), status=200, mimetype='text/json')

@main_blueprint.route("/api/v1/users/<int:userid>/skillsbundle/<int:skillsbundleid>", methods=['POST'])
@timer
@debug_announce
@check_stt_bearer_token
@try_this
def assign_skill_bundle_to_user(userid, skillsbundleid):
    # Assigns a skill bundle to a particular user

    thisfunction = inspect.stack()[0].function
    payload = defaultdict(dict)
    skills = []
    headers = {'apitoken': request.headers['apitoken']} # just pass the apitoken on through

    existingskillcontents = stt_api_call(uri="/api/v1/users/" + str(userid) + "/skills", method="GET")
    if existingskillcontents.status_code == 200:
        existingskillcontentsjson = existingskillcontents.json()
        for skilli in existingskillcontentsjson["skills"]:
            skill = defaultdict(dict)
            skill["@type"] = "list"
            skill["attrId"] = 84001
            skill["value"] = skilli["docupaceid"]
            skill["@valueType"] = "num"
            skill["domainId"] = 840
            skill["attrValues"] = []
            skills.append(skill)
        logger.debug("f[{thisfunction}()] Existing skills for user " + str(userid) + ": " + str(len(skills)) + " skills")
    else:
        logger.error(f"[{thisfunction}()] Request returned a " + str(existingskillcontents.status_code) + " status code. Returning response with a status code of 500...")
        returnobject = defaultdict(dict)
        returnobject["existingskillcontentsresultcode"] = existingskillcontents.status_code
        returnobject["payloadskills"] = json.dumps(skills)
        return Response(response=json.dumps(returnobject), status=500, mimetype='text/json')

    skillbundlecontents = stt_api_call(uri="/api/v1/skillsbundles/" + str(skillsbundleid) + "/skills", method="GET")
    if skillbundlecontents.status_code == 200:
        skillbundlecontentsjson = skillbundlecontents.json()
        for skilli in skillbundlecontentsjson["skills"]:
            skill = defaultdict(dict)
            skill["@type"] = "list"
            skill["attrId"] = 84001
            skill["value"] = skilli["docupaceid"]
            skill["@valueType"] = "num"
            skill["domainId"] = 840
            skill["attrValues"] = []
            skills.append(skill)
        logger.debug("f[{thisfunction}()] After adding skills bundle " + str(skillsbundleid) + ", total skills: " + str(len(skills)) + " skills")
    else:
        logger.error("f[{thisfunction}()] Request returned a " + str(skillbundlecontents.status_code) + " status code. Returning response with a status code of 500...")
        returnobject = defaultdict(dict)
        returnobject["skillbundlecontentsresultcode"] = skillbundlecontents.status_code
        returnobject["payloadskills"] = json.dumps(skills)
        return Response(response=json.dumps(returnobject), status=500, mimetype='text/json')

    payload["record"]["attrValues"] = skills
    logger.debug(f"[{thisfunction}()] Payload is " + json.dumps(payload))

    dpresponse = docupace_call(uri='domains/300/records/' + str(userid) + '/data.json', method="PUT", data=json.dumps(payload))
    returnobject = defaultdict(dict)
    returnobject["dpresponse_code"] = dpresponse.status_code
    if dpresponse.status_code == 204:
        returnobject["result"] = "Success"
        statuscode=200
    else:
        returnobject["result"] = "Fail"
        statuscode=500
    logger.debug(f"[{thisfunction}()] Returning response data with a status code of " + str(statuscode) + "...")
    return Response(response=json.dumps(returnobject), status=statuscode, mimetype='text/json')

@main_blueprint.route("/api/v2/users/<int:userid>/skillsbundle/<int:skillsbundleid>", methods=['POST'])
@timer
@debug_announce
@check_stt_bearer_token
@try_this
def assign_skill_bundle_to_user_v2(userid, skillsbundleid):
    # Assigns a skill bundle to a particular user

    thisfunction = inspect.stack()[0].function
    deletefirst = False
    if request.args.get('deletefirst') is not None and is_int(request.args.get('deletefirst')):
        if (int(request.args.get('deletefirst')) == 1):
            deletefirst = True

    payload = defaultdict(dict)
    skills = []
    headers = {'apitoken': request.headers['apitoken']} # just pass the apitoken on through

    if not deletefirst:
        # get current skills
        # TODO: pull into separate function
        existingskillcontents = stt_api_call(uri="/api/v1/users/" + str(userid) + "/skills", method="GET")
        if existingskillcontents.status_code == 200:
            for skilli in existingskillcontents.json()["skills"]:
                skill = defaultdict(dict)
                skill["@type"] = "list"
                skill["attrId"] = 84001
                skill["value"] = skilli["docupaceid"]
                skill["@valueType"] = "num"
                skill["domainId"] = 840
                skill["attrValues"] = []
                skills.append(skill)
            logger.debug(f"[{thisfunction}()] Existing skills for user " + str(userid) + ": " + str(len(skills)) + " skills")
        else:
            returnobject = defaultdict(dict)
            returnobject["existingskillcontentsresultcode"] = existingskillcontents.status_code
            returnobject["payloadskills"] = json.dumps(skills)
            return Response(response=json.dumps(returnobject), status=500, mimetype='text/json')
    else:
        logger.debug(f"[{thisfunction}()] deletefirst is true, skipping query for user's existing skills...")

    # get bundle contents
    # TODO: pull into separate function
    skillbundlecontents = stt_api_call(uri="/api/v1/skillsbundles/" + str(skillsbundleid) + "/skills", method="GET")
    if skillbundlecontents.status_code == 200:
        for skilli in skillbundlecontents.json()["skills"]:
            skill = defaultdict(dict)
            skill["@type"] = "list"
            skill["attrId"] = 84001
            skill["value"] = skilli["docupaceid"]
            skill["@valueType"] = "num"
            skill["domainId"] = 840
            skill["attrValues"] = []
            skills.append(skill)
        logger.debug(f"[{thisfunction}()] After adding skills bundle " + str(skillsbundleid) + ", total skills: " + str(len(skills)) + " skills")
    else:
        returnobject = defaultdict(dict)
        returnobject["skillbundlecontentsresultcode"] = skillbundlecontents.status_code
        returnobject["payloadskills"] = json.dumps(skills)
        return Response(response=json.dumps(returnobject), status=500, mimetype='text/json')

    payload["record"]["attrValues"] = skills
    logger.debug(f"[{thisfunction}()] Payload is " + json.dumps(payload))

    # assigning compiled skills list
    dpresponse = docupace_call(uri='domains/300/records/' + str(userid) + '/data.json', method="PUT", data=json.dumps(payload))

    returnobject = defaultdict(dict)
    returnobject["dpresponse_code"] = dpresponse.status_code
    if dpresponse.status_code >= 200 and dpresponse.status_code < 300:
        returnobject["result"] = "Success"
        statuscode=200
    else:
        returnobject["result"] = "Fail"
        statuscode=500
    logger.debug(f"[{thisfunction}()] Returning response data with a status code of " + str(statuscode) + "...")
    return Response(response=json.dumps(returnobject), status=statuscode, mimetype='text/json')

@main_blueprint.route("/api/v1/skills", methods=['GET'])
@timer
@debug_announce
@check_stt_bearer_token
@try_this
def retrieve_skills():
    # Retrieves all the skills

    thisfunction = inspect.stack()[0].function
    if request.args.get('limit') is not None and is_int(request.args.get('limit')):
        limit = int(request.args.get('limit'))
    else:
        limit = 0
    create_connection()
    returnobject = defaultdict(dict)
    skills = []
    sql = 'select * from stt.skills order by stt.skills.docupace_id;'
    logger.info(f"[{thisfunction}()] SQL: " + sql + " ...")
    try:
        skills_df = pd.read_sql(sql, engine)
        i = 0
        for index, row in skills_df.iterrows():
            skill = defaultdict(dict)
            skill["skillid"] = row['skill_id']
            skill["skillname"] = row['skill_name']
            skill["docupaceid"] = row['docupace_id']
            skills.append(skill)
            i = i + 1
            if limit > 0 and i >= limit:
                break
        logger.debug(f"[{thisfunction}()] Received " + str(len(skills)) + " skills from DB")
        returnobject["skills"] = skills
        logger.debug(f"[{thisfunction}()] Success. Returning response data.")
        return Response(response=json.dumps(returnobject), status=200, mimetype='text/json')
    except Exception as ex:
        logger.critical(f"[{thisfunction}()] " + traceback.format_exc())
        abort(500)

@main_blueprint.route("/api/v1/skillsbundles", methods=['GET'])
@timer
@debug_announce
@check_stt_bearer_token
@try_this
def retrieve_skill_bundles():
    # Retrieves all active skill bundles and returns them in a simplified list

    thisfunction = inspect.stack()[0].function
    active = sqlsafe(request.args.get('active', default='*', type=str))
    if str.lower(active) == "true":
        active = "TRUE"
    elif str.lower(active) == "false":
        active = "FALSE"

    if active == "TRUE" or active == "FALSE":
        whereclause = " where is_active = " + active + " "
    else:
        whereclause = ''

    create_connection()
    returnobject = defaultdict(dict)
    bundles = []
    sql = 'select * from stt.bundles ' + whereclause + ' order by bundles.bundle_id asc;'
    logger.info(f"[{thisfunction}()] SQL: " + sql )
    try:
        bundles_df = pd.read_sql(sql, engine)
        for index, row in bundles_df.iterrows():
            bundle = defaultdict(dict)
            bundle["bundleid"] = row['bundle_id']
            bundle["bundlename"] = row['bundle_name']
            bundle["is_active"] = row['is_active']
            bundles.append(bundle)
