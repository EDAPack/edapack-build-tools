#!/usr/bin/env python3
#****************************************************************************
#* install.py
#*
#* Generic installer script to be packed with EDAPack packages
#****************************************************************************
import argparse
import tarfile
import os
import shutil

#********************************************************************
#* read_pkginfo()
#*
#* Reads the <key>=<val> package.info file
#********************************************************************
def read_pkginfo(pkginfo):
    info = dict()
    f = open(pkginfo, "r")
    
    for line in f.readlines():
        if line.find("#") != -1:
            line = line[:line.find("#")]
            
        line = line.strip()
        
        if line == "":
            continue
        
        if line.find("=") != -1:
            key = line[:line.find("=")]
            value = line[line.find("=")+1:]
            print("key=" + key + " value=" + value)
            info[key] = value
        
        print("Process line: " + line)
    
    f.close()
    return info

#********************************************************************
#* install()
#*
#* Runs the installation process
#********************************************************************
def install(args):
    # Obtain the path to the etc directory    
    etc_dir = os.path.dirname(os.path.abspath(__file__))
    edapack = args.edapack
    tf = None
    
    if args.archive != None:
        print("archive=" + args.archive);
        # Running in archive mode. Must open the archive and extract the package.info file
        tf = tarfile.open(args.archive, "r:gz")
        tf.extract("etc/package.info", os.path.dirname(etc_dir));
    else:
        # Running in local-install mode. Expect the package.info file to be in the etc_dir
        print("no archive specified")
        
    # TODO: Need to read the package.info file
    package_info = os.path.join(etc_dir, "package.info")
    pkginfo = read_pkginfo(package_info)
    
    if "name" in pkginfo.keys() == False:
        print("Error: no 'name' specified")
        
    if "version" in pkginfo.keys() == False:
        print("Error: no 'version' specified")

    # Okay, we have a name, a version, and a target directory
    tooldir = os.path.join(edapack, pkginfo["name"])
    destdir = os.path.join(tooldir, pkginfo["version"])
    print("Install to: " + destdir)
    
    if os.path.exists(destdir):
        if args.force:
            print("TODO: delete old installation")
            shutil.rmtree(destdir)
        else:
            print("Error: package " + pkginfo["name"] + 
                  " version " + pkginfo["version"] + " is already installed")
            exit(1)
            
    os.makedirs(destdir)
    
    # Copy or unpack 
    if args.archive == None:
        # Copy the directory
        srcdir = os.path.dirname(etc_dir)
        for d in os.listdir(srcdir):
            shutil.copytree(
                os.path.join(srcdir, d), 
                os.path.join(destdir, d), 
                True)
    else:
        print("TODO: unpack the archive")
        tf.extractall(destdir)
    
   
    modulefile = os.path.join(destdir, "etc", "modulefile")
   
    if os.path.exists(modulefile):
        modulefiles_dir = os.path.join(
            edapack, 
            "modulesfiles", 
            pkginfo["name"])
        if os.path.exists(modulefiles_dir) == False:
            os.makedirs(modulefiles_dir)
        shutil.copy(modulefile, os.path.join(
            modulefiles_dir, 
            pkginfo["version"])
        )
        update_modulefile_latest(modulefiles_dir, pkginfo["version"])

    # TODO: must determine whether this is the latest version
    if tf != None:
        tf.close()

def update_modulefile_latest(modulefiles_dir, version):
    print("update_modulefile_latest: " + modulefiles_dir + " version=" + version)
    is_latest = True
    
    for v in os.listdir(modulefiles_dir):
        if v != "latest" and is_version_ge(version, v) == False:
            is_latest = False
            break
    
    if is_latest == True:
        print("Updating 'latest' modulefile")
        shutil.copy(
            os.path.join(modulefiles_dir, version),
            os.path.join(modulefiles_dir, "latest"))

def is_version_ge(v1, v2):    
    v1_list = v1.split(".")
    v2_list = v2.split(".")

    # Ensure the versions are the same length
    while len(v1_list) < len(v2_list):
        v1_list.append("0")
    while len(v2_list) < len(v1_list):
        v2_list.append("0")

    # Convert each version to an integer that can be compared
    v1_val = 0
    v2_val = 0
    for i in range(len(v1_list)):
        v1_val *= 10
        v1_val += int(v1_list[i])
    for i in range(len(v2_list)):
        v2_val *= 10
        v2_val += int(v2_list[i])
        
    is_ge = v1_val >= v2_val
#    print("Compare: " + v1 + " " + v2 + ": " + str(is_ge))
    return is_ge

#********************************************************************
#* install main()
#********************************************************************
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("edapack", help="Specifies the path to the edapack install")
    parser.add_argument("--archive", help="Specifies the path to the archive to install")
    parser.add_argument("--force", 
        help="Overwrites an existing installation",
        action="store_true")
   
    args = parser.parse_args()
   
    install(args)
        
    
if __name__ == "__main__":
    main()
    