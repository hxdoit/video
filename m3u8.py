import os
import re
import fcntl 
import time

def get_new_files(path):
    arr = [] 
    try:
        f = open(path, 'r')
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            arr.append(line)
        f.close()
        return arr 
    except Exception, e:
        print e
        return []    

def clean_new_files(arr, path):
    newArr = []
    try:
        f = open(path, 'r+')
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            if not line in arr:
                newArr.append(line + '\n')
        f.seek(0,0)
        f.truncate()
        f.writelines(newArr)
        f.close()
    except Exception, e:
        print e


def read_map(path):
    dic = {}
    try:
        f = open(path, 'r')
        lines = f.readlines()
        for line in lines:
            line = line.strip('\n')
            lineArr = line.split("\t")    
            dic[lineArr[0]] = int(lineArr[1])
        f.close()
        return dic
    except Exception, e:
        print e
        return {}    

def dump_map(dic, path):
    dicSort = sorted(dic.items(),key=lambda d:d[0])
    dic10 = dicSort[-10:]
    arr = []
    for i,j in dic10:
        arr.append("%s\t%s\n"%(i,j))
    f = open(path, 'w')
    f.writelines(arr)
    f.close()
    
def release_old_files(aviPath, tsPath, dicPath):
    dic = read_map(dicPath)
    avis = dic.keys()
    tss = dic.values()
    avis.sort()
    tss.sort()

    aviPattern = re.compile('\d{4}(-\d{2}){5}')
    aviFileList = os.listdir(aviPath)
    for f in aviFileList:
        if f < avis[0] and aviPattern.match(f):
            os.remove(aviPath + '/' + f)

    tsPattern = re.compile('my\d*\.ts')
    tsFileList= os.listdir(tsPath)
    for f in tsFileList:
        seq = f.replace('my', '').replace('.ts', '') 
        if tsPattern.match(f) and int(seq) < tss[0]:
            os.remove(tsPath + '/' + f)

def gen_m3u8():
    dic = read_map(DIC_PATH)
    ids = dic.values()
    ids.sort()

    pieces = []
    pieces.append('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n#EXT-X-MEDIA-SEQUENCE:%d\n'%(ids[0]))
    for i in ids:
        pieces.append('#EXTINF:9.800000,\nmy' + str(i) + '.ts\n')

    pieces[len(ids)] = pieces[len(ids)].strip('\n')
    #pieces.append('#EXT-X-ENDLIST')
   
    f = open(M3U8_FILE_PATH, 'w')
    f.writelines(pieces) 
    f.close()
    
    
AVI_PATH = '/RAM1/avi'
TS_PATH = '/RAM1/ts'
DIC_PATH = '/RAM1/ts/dic'
NEW_FILE_PATH = '/RAM1/avi/newlist'
M3U8_FILE_PATH = '/RAM1/ts/my.m3u8'


while True:
    newFiles = get_new_files(NEW_FILE_PATH)
    if not newFiles:
        time.sleep(2)
        continue

    dic = read_map(DIC_PATH)
    dicSort = sorted(dic.items(),key = lambda d:d[1],reverse=True)
    sequence = 0 if not dicSort else int(dicSort[0][1]) + 1

    for i in newFiles:
        cmd = "ffmpeg -i %s/%s %s/a.m3u8 >/dev/null 2>/dev/null"%(AVI_PATH,i,TS_PATH)
        os.system(cmd)
        cmd = "mv %s/a0.ts %s/my%d.ts"%(TS_PATH,TS_PATH,sequence)
        os.system(cmd)
        dic[i] = sequence
        sequence+=1

    clean_new_files(newFiles, NEW_FILE_PATH)

    dump_map(dic, DIC_PATH) 

    release_old_files(AVI_PATH, TS_PATH, DIC_PATH)

    gen_m3u8()

    time.sleep(2)

















