# Command related to creation and execution: run, new, clean, test, auto-test

import sys
import os
import subprocess
import shutil
import getopt
import urllib2
import webbrowser
import time
import signal

from play.utils import *

COMMANDS = ['run', 'new', 'new-sbs', 'git-sbs', 'clean', 'test', 'autotest', 'auto-test', 'id', 'new,run', 'clean,run', 'modules']

HELP = {
    'id': "Define the framework ID",
    'new': "Create a new application",
    'new-sbs': "Create a new SBS Manager",
    'git-sbs': "Setup git environment for SBS Manager",
    'clean': "Delete temporary files (including the bytecode cache)",
    'run': "Run the application in the current shell",
    'test': "Run the application in test mode in the current shell",
    'auto-test': "Automatically run all application tests",
    'modules': "Display the computed modules list"
}

def execute(**kargs):
    command = kargs.get("command")
    app = kargs.get("app")
    args = kargs.get("args")
    env = kargs.get("env")
    cmdloader = kargs.get("cmdloader")

    if command == 'id':
        id(env)
    if command == 'new' or command == 'new,run':
        new(app, args, env, cmdloader)
    if command == 'new-sbs' or command == 'new-sbs,run':
        newSBS(app, args, env, cmdloader)
    if command == 'git-sbs':
        gitSBS(app, args, env, cmdloader)
    if command == 'clean' or command == 'clean,run':
        clean(app)
    if command == 'new,run' or command == 'clean,run' or command == 'run':
        run(app, args)
    if command == 'test':
        test(app, args)
    if command == 'auto-test' or command == 'autotest':
        autotest(app, args)
    if command == 'modules':
        show_modules(app, args)

def new(app, args, env, cmdloader=None):
    withModules = []
    application_name = None
    try:
        optlist, args = getopt.getopt(args, '', ['with=', 'name='])
        for o, a in optlist:
            if o in ('--with'):
                withModules = a.split(',')
            if o in ('--name'):
                application_name = a
    except getopt.GetoptError, err:
        print "~ %s" % str(err)
        print "~ Sorry, unrecognized option"
        print "~ "
        sys.exit(-1)
    if os.path.exists(app.path):
        print "~ Oops. %s already exists" % app.path
        print "~"
        sys.exit(-1)

    md = []
    for m in withModules:
        dirname = None
        if os.path.exists(os.path.join(env["basedir"], 'modules/%s' % m)) and os.path.isdir(os.path.join(env["basedir"], 'modules/%s' % m)):
            dirname = m
        else:
            for f in os.listdir(os.path.join(env["basedir"], 'modules')):
                if os.path.isdir(os.path.join(env["basedir"], 'modules/%s' % f)) and f.find('%s-' % m) == 0:
                    dirname = f
                    break
        
        if not dirname:
            print "~ Oops. No module %s found" % m
            print "~ Try to install it using 'play install %s'" % m
            print "~"
            sys.exit(-1)

        md.append(dirname)

    print "~ The new application will be created in %s" % os.path.normpath(app.path)
    if application_name is None:
        application_name = raw_input("~ What is the application name? [%s] " % os.path.basename(app.path))
    if application_name == "":
        application_name = os.path.basename(app.path)
    copy_directory(os.path.join(env["basedir"], 'resources/application-skel'), app.path)
    os.mkdir(os.path.join(app.path, 'app/models'))
    os.mkdir(os.path.join(app.path, 'lib'))
    app.check()
    replaceAll(os.path.join(app.path, 'conf/application.conf'), r'%APPLICATION_NAME%', application_name)
    replaceAll(os.path.join(app.path, 'conf/application.conf'), r'%SECRET_KEY%', secretKey())
    print "~"

    # Configure modules 
    runDepsAfter = False
    for m in md:
        # Check dependencies.yml of the module
        depsYaml = os.path.join(env["basedir"], 'modules/%s/conf/dependencies.yml' % m)
        if os.path.exists(depsYaml):
            deps = open(depsYaml).read()
            try:
                moduleDefinition = re.search(r'self:\s*(.*)\s*', deps).group(1)
                replaceAll(os.path.join(app.path, 'conf/dependencies.yml'), r'- play\n', '- play\n    - %s\n' % moduleDefinition )
                runDepsAfter = True
            except Exception:
                pass
                
    if runDepsAfter:
        cmdloader.commands['dependencies'].execute(command='dependencies', app=app, args=['--sync'], env=env, cmdloader=cmdloader)

    print "~ OK, the application is created."
    print "~ Start it with : play run %s" % sys.argv[2]
    print "~ Have fun!"
    print "~"

def newSBS(app, args, env, cmdloader=None):
    withModules = []
    application_name = None
    try:
        optlist, args = getopt.getopt(args, '', ['with=', 'name='])
        for o, a in optlist:
            if o in ('--with'):
                withModules = a.split(',')
            if o in ('--name'):
                application_name = a
    except getopt.GetoptError, err:
        print "~ %s" % str(err)
        print "~ Sorry, unrecognized option"
        print "~ "
        sys.exit(-1)
    if os.path.exists(app.path):
        print "~ Oops. %s already exists" % app.path
        print "~"
        sys.exit(-1)

    md = []
    for m in withModules:
        dirname = None
        if os.path.exists(os.path.join(env["basedir"], 'modules/%s' % m)) and os.path.isdir(os.path.join(env["basedir"], 'modules/%s' % m)):
            dirname = m
        else:
            for f in os.listdir(os.path.join(env["basedir"], 'modules')):
                if os.path.isdir(os.path.join(env["basedir"], 'modules/%s' % f)) and f.find('%s-' % m) == 0:
                    dirname = f
                    break
        
        if not dirname:
            print "~ Oops. No module %s found" % m
            print "~ Try to install it using 'play install %s'" % m
            print "~"
            sys.exit(-1)

        md.append(dirname)

    print "~ The new application will be created in %s" % os.path.normpath(app.path)
    if application_name is None:
        application_name = raw_input("~ What is the application name? [%s] " % os.path.basename(app.path))
    if application_name == "":
        application_name = os.path.basename(app.path)

    default_email = raw_input("~ Default email address? [staff@digiplant.se] ")
    if default_email == "":
        default_email = "staff@digiplant.se"
    srv_user = raw_input("~ Server user name? [serverUser] ")
    if srv_user == "":
        srv_user = "serverUser"
    db_name = raw_input("~ Name of the database? [sbsmgr_x] ")
    if srv_user == "":
        srv_user = "sbsmgr_x"
    server_host = raw_input("~ Domain name of the deployment server? [ansok.server.se] ")
    if server_host == "":
        server_host = "ansok.server.se"
    git_repo = raw_input("~ Name of the git repository (used in deployment)? [git@github.com:digiPlant/dummy.git] ")
    if git_repo == "":
        git_repo = "git@github.com:digiPlant/dummy.git"
    service_name = raw_input("~ Name of the service on the deployment server? [play] ")
    if service_name == "":
        service_name = "play"

    copy_directory(os.path.join(env["basedir"], 'resources/sbs-skel'), app.path)
    os.mkdir(os.path.join(app.path, 'app/models'))
    os.mkdir(os.path.join(app.path, 'lib'))
    app.check()
    replaceAll(os.path.join(app.path, 'conf/application.conf'), r'%APPLICATION_NAME%', application_name)
    replaceAll(os.path.join(app.path, 'conf/application.conf'), r'%SECRET_KEY%', secretKey())
    replaceAll(os.path.join(app.path, 'conf/application.conf'), r'%SRV_USER%', srv_user)
    replaceAll(os.path.join(app.path, 'conf/application.conf'), r'%DB_NAME%', db_name)
    replaceAll(os.path.join(app.path, 'conf/application.conf'), r'%DEFAULT_EMAIL%', default_email)

    replaceAll(os.path.join(app.path, 'deploy/deploy.rb'), r'%SRV_USER%', srv_user)
    replaceAll(os.path.join(app.path, 'deploy/deploy.rb'), r'%GIT_REPO%', git_repo)
    replaceAll(os.path.join(app.path, 'deploy/deploy.rb'), r'%SERVICE_NAME%', service_name)

    replaceAll(os.path.join(app.path, 'deploy/deploy/production.rb'), r'%SRV_USER%', srv_user)
    replaceAll(os.path.join(app.path, 'deploy/deploy/production.rb'), r'%SRV_HOST%', server_host)

    replaceAll(os.path.join(app.path, 'deploy/server/play-service.conf'), r'%APPLICATION_NAME%', application_name)
    replaceAll(os.path.join(app.path, 'deploy/server/play-service.conf'), r'%SRV_USER%', srv_user)

    replaceAll(os.path.join(app.path, 'deploy/server/nginx-site.conf'), r'%SRV_HOST%', server_host)

    print "~"

    # Configure modules 
    runDepsAfter = False
    for m in md:
        # Check dependencies.yml of the module
        depsYaml = os.path.join(env["basedir"], 'modules/%s/conf/dependencies.yml' % m)
        if os.path.exists(depsYaml):
            deps = open(depsYaml).read()
            try:
                moduleDefinition = re.search(r'self:\s*(.*)\s*', deps).group(1)
                replaceAll(os.path.join(app.path, 'conf/dependencies.yml'), r'- play\n', '- play\n    - %s\n' % moduleDefinition )
                runDepsAfter = True
            except Exception:
                pass
                
    if runDepsAfter:
        cmdloader.commands['dependencies'].execute(command='dependencies', app=app, args=['--sync'], env=env, cmdloader=cmdloader)

    print "~ You created a new SBS Manager (but there are still some things to do):"
    print "~   1. Create databases"
    print "~   2. Add database user and passwords to conf/application.conf"
    print "~   3. Create a repository in gitolite-admin"
    print "~   4. Setup Git: from app dir run: play git-sbs"
    print "~   5. Start the app and go to http://localhost:9000/sbs/skrivbord/login/sysadmin and initialize the manager"
    print "~"
    print "~ Server presumptions:"
    print "~   Play installed in: /opt/sbs-play"
    print "~   Certificate + private key installed in (named [hostname].key and [hostname].cer): /etc/ssl/certs"
    print "~   Application home beeing: /home/[username]/sbsmgr"
    print "~"
    print "~ Start it with : play run %s" % sys.argv[2]
    print "~ Have fun!"
    print "~"

process = None

def handle_git_sigterm(signum, frame):
    global process
    if 'process' in globals():
        process.terminate()
        sys.exit(0)

def gitSBS(app, args, env, cmdloader=None):
    global process
    print "~ Setting up git environment"
    print "~ "
    git_uri = raw_input("~ Git remote repository URI (git@store.digiplant.se:[customer]/sbsmanager.git)? ")
    git_core_uri = raw_input("~ Git Core repository URI? [git@github.com:digiPlant/sbsmanager.git] ")
    if git_core_uri == "":
        git_core_uri = "git@github.com:digiPlant/sbsmanager.git"
    git_commands = [
        ["git", "init"], # Skapa git
        ["git", "remote", "add", "--track", "master", "origin", git_uri], # Koppla mot remote
        ["git", "submodule", "add", git_core_uri, "repository/core/"], # Koppla core submodule
        ["git", "submodule", "update", "--init"]
        #["cd", "repository/core"], 
        #["git", "checkout", "`git describe --tags`"] # Checka ut den senaste taggade versionen av core
    ]

    for git_cmd in git_commands:   
        try:
            process = subprocess.Popen (git_cmd, env=os.environ)
            signal.signal(signal.SIGTERM, handle_git_sigterm)
            return_code = process.wait()
            if 0 != return_code:
                sys.exit(return_code)
        except OSError, e:
            print "Could not execute git command: %s " % git_cmd
            print e
            sys.exit(-1)
        print

    print "~ Run git checkout `git describe --tags` manually from repository/core"

def handle_sigterm(signum, frame):
    global process
    if 'process' in globals():
        process.terminate()
        sys.exit(0)

def run(app, args):
    global process
    app.check()
    
    print "~ Ctrl+C to stop"
    print "~ "
    java_cmd = app.java_cmd(args)
    try:
        process = subprocess.Popen (java_cmd, env=os.environ)
        signal.signal(signal.SIGTERM, handle_sigterm)
        return_code = process.wait()
        if 0 != return_code:
            sys.exit(return_code)
    except OSError:
        print "Could not execute the java executable, please make sure the JAVA_HOME environment variable is set properly (the java executable should reside at JAVA_HOME/bin/java). "
        sys.exit(-1)
    print

def clean(app):
    app.check()
    print "~ Deleting %s" % os.path.normpath(os.path.join(app.path, 'tmp'))
    if os.path.exists(os.path.join(app.path, 'tmp')):
        shutil.rmtree(os.path.join(app.path, 'tmp'))
    print "~"

def show_modules(app, args):
    app.check()
    modules = app.modules()
    if len(modules):
        print "~ Application modules are:"
        print "~ "
        for module in modules:
            print "~ %s" % module
    else:
        print "~ No modules installed in this application"
    print "~ "
    sys.exit(0)

def test(app, args):
    app.check()
    java_cmd = app.java_cmd(args)
    print "~ Running in test mode"
    print "~ Ctrl+C to stop"
    print "~ "

    try:
        return_code = subprocess.call(java_cmd, env=os.environ)
        if 0 != return_code:
            sys.exit(return_code)
    except OSError:
        print "Could not execute the java executable, please make sure the JAVA_HOME environment variable is set properly (the java executable should reside at JAVA_HOME/bin/java). "
        sys.exit(-1)
    print

def autotest(app, args):
    app.check()
    print "~ Running in test mode"
    print "~ Ctrl+C to stop"
    print "~ "

    print "~ Deleting %s" % os.path.normpath(os.path.join(app.path, 'tmp'))
    if os.path.exists(os.path.join(app.path, 'tmp')):
        shutil.rmtree(os.path.join(app.path, 'tmp'))
    print "~"

    # Kill if exists
    http_port = 9000
    protocol = 'http'
    if app.readConf('https.port'):
        http_port = app.readConf('https.port')
        protocol = 'https'
    else:
        http_port = app.readConf('http.port')
    try:
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        opener.open('http://localhost:%s/@kill' % http_port)
    except Exception, e:
        pass

    # Do not run the app if SSL is configured and no cert store is configured
    keystore = app.readConf('keystore.file')
    if protocol == 'https' and not keystore:
      print "https without keystore configured. play auto-test will fail. Exiting now."
      sys.exit(-1)
    # Run app
    test_result = os.path.join(app.path, 'test-result')
    if os.path.exists(test_result):
        shutil.rmtree(test_result)
    sout = open(os.path.join(app.log_path(), 'system.out'), 'w')
    java_cmd = app.java_cmd(args)
    try:
        play_process = subprocess.Popen(java_cmd, env=os.environ, stdout=sout)
    except OSError:
        print "Could not execute the java executable, please make sure the JAVA_HOME environment variable is set properly (the java executable should reside at JAVA_HOME/bin/java). "
        sys.exit(-1)
    soutint = open(os.path.join(app.log_path(), 'system.out'), 'r')
    while True:
        if play_process.poll():
            print "~"
            print "~ Oops, application has not started?"
            print "~"
            sys.exit(-1)
        line = soutint.readline().strip()
        if line:
            print line
            if line.find('Go to ') > -1: # This line is written out by the test runner to system.out and is not log file dependent
                soutint.close()
                break

    # Run FirePhoque
    print "~"

    headless_browser = ''
    if app.readConf('headlessBrowser'):
        headless_browser = app.readConf('headlessBrowser')

    fpcp = [os.path.join(app.play_env["basedir"], 'modules/testrunner/lib/play-testrunner.jar')]
    fpcp_libs = os.path.join(app.play_env["basedir"], 'modules/testrunner/firephoque')
    for jar in os.listdir(fpcp_libs):
        if jar.endswith('.jar'):
           fpcp.append(os.path.normpath(os.path.join(fpcp_libs, jar)))
    cp_args = ':'.join(fpcp)
    if os.name == 'nt':
        cp_args = ';'.join(fpcp)    
    java_cmd = [app.java_path(), '-classpath', cp_args, '-Dapplication.url=%s://localhost:%s' % (protocol, http_port), '-DheadlessBrowser=%s' % (headless_browser), 'play.modules.testrunner.FirePhoque']
    if protocol == 'https':
        java_cmd.insert(-1, '-Djavax.net.ssl.trustStore=' + app.readConf('keystore.file'))
    try:
        subprocess.call(java_cmd, env=os.environ)
    except OSError:
        print "Could not execute the headless browser. "
        sys.exit(-1)

    print "~"
    time.sleep(1)
    
    # Kill if exists
    try:
        proxy_handler = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy_handler)
        opener.open('%s://localhost:%s/@kill' % (protocol, http_port))
    except Exception, e:
        pass
 
    if os.path.exists(os.path.join(app.path, 'test-result/result.passed')):
        print "~ All tests passed"
        print "~"
        testspassed = True
    if os.path.exists(os.path.join(app.path, 'test-result/result.failed')):
        print "~ Some tests have failed. See file://%s for results" % test_result
        print "~"
        sys.exit(1)

def id(play_env):
    if not play_env["id"]:
        print "~ framework ID is not set"
    new_id = raw_input("~ What is the new framework ID (or blank to unset)? ")
    if new_id:
        print "~"
        print "~ OK, the framework ID is now %s" % new_id
        print "~"
        open(play_env["id_file"], 'w').write(new_id)
    else:
        print "~"
        print "~ OK, the framework ID is unset"
        print "~"
        if os.path.exists(play_env["id_file"]):
            os.remove(play_env["id_file"])

# ~~~~~~~~~ UTILS

def kill(pid):
    if os.name == 'nt':
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(1, False, int(pid))
        if not ctypes.windll.kernel32.TerminateProcess(handle, 0):
            print "~ Cannot kill the process with pid %s (ERROR %s)" % (pid, ctypes.windll.kernel32.GetLastError())
            print "~ "
            sys.exit(-1)
    else:
        try:
            os.kill(int(pid), 15)
        except OSError:
            print "~ Play was not running (Process id %s not found)" % pid
            print "~"
            sys.exit(-1)
