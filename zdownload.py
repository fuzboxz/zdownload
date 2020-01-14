import sys, requests, json, os
if sys.version_info >= (3, 6):
    import zipfile
else:
    import zipfile36 as zipfile

zdl_url = "http://www.zoom.co.jp/archive/ZDLM/ZDLF3/"

r = requests.get("https://www.zoom.co.jp/archive/ZDLM/AllZDL3.lst")
if r.status_code == 200:
    data = json.loads(r.text)
    
    #download url might change
    print("Download URL: " + data.get("zdl_url"))
    if zdl_url != data.get("zdl_url"):
        zdl_url = data.get("zdl_url")
    
    #create parent folder
    path = os.path.join(os.getcwd(),"zoom_fx")
    if not os.path.exists(path):
        os.mkdir(path)
    
    #iterate through devices
    for device in data.get("models"):
    
        devicename = device.get("modelName")
        
        if len(device.get("effects")) > 0:
        
            print(devicename)
            
            # create folder structure and clean up purgescript
            
            path = os.path.join(os.getcwd(),"zoom_fx",devicename)
            if not os.path.exists(path):
                os.mkdir(path)
                
            purgescript = os.path.join(path,devicename + "_purge.cmd")
            if os.path.exists(purgescript):
                os.remove(purgescript)
        
            #iterate through effects
            for effect in device.get("effects"):
                
                #download file if we don't have it yet
                filename = effect.get("fileName")
                
                noext = filename[0:(len(filename)-4)]
                path_zd2 = os.path.join(path,noext+".ZD2")
                path_zdl = os.path.join(path,noext+".ZDL")
                
                #only download if the fx is not there
                if not os.path.exists(path_zd2) and not os.path.exists(path_zdl):               
                    
                    #check zip file
                    archive_path = os.path.join(path,filename)
                    if not os.path.exists(archive_path):
                        print(noext)
                        #download zip
                        r = requests.get(zdl_url+filename)
                        with open(archive_path,'wb') as f:
                            f.write(r.content)
                        #extract zip
                        with zipfile.ZipFile(archive_path,'r') as zipObj:
                            zipObj.extractall(path)
                        #remove zip
                        os.remove(archive_path)
                else:
                    print(noext + " already exists - SKIPPING")
                
                #figure out extension for the cleanup script
                if os.path.exists(path_zd2):
                    filename = filename.replace("zip", "ZD2")
                if os.path.exists(path_zdl):
                    filename = filename.replace("zip", "ZDL")
                
                #append command to cleanup script
                with open(purgescript,'a+') as file:
                    file.write("python zoomzt2.py -U %s -S empty.zt2 \n" %filename)
        else:
            print(devicename + " empty - SKIPPING")
            
        
else:
    print('Connection error')