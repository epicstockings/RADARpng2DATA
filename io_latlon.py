# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 13:35:31 2019

@author: siwo
"""

import struct
import numpy as np
import os
import time
from itertools import groupby

def byte2str(byte_in):
    return str(byte_in,encoding = "utf-8")

def read_latlon_each(all_info_list,binFile,filesize,location):
    all_info={}
    
    binFile.seek(location)
    context=binFile.read(1*128)
    all_info['dataname']=context.decode('utf-8', 'ignore')
    
    binFile.seek(location+128)
    context=binFile.read(1*32)
    all_info['varname']=context.decode('utf-8', 'ignore')
    
    binFile.seek(location+160)
    context=binFile.read(1*16)
    all_info['units']=context.decode('utf-8', 'ignore')
    
    binFile.seek(location+176)
    context=binFile.read(2*1)
    all_info['label']=struct.unpack('H'*1,context)[0]
    
    binFile.seek(location+178)
    context=binFile.read(2*1)
    all_info['unitlen']=struct.unpack('h'*1,context)[0]
    
    binFile.seek(location+180)
    context=binFile.read(4*6)
    all_info['latlon_domain']=list(struct.unpack('f'*6,context))
    latlon_domain=struct.unpack('f'*6,context)
    
    binFile.seek(location+204)
    context=binFile.read(1*8)
    all_info['rows_cols']=list(struct.unpack('i'*2,context))
    
    binFile.seek(location+212)
    context=binFile.read(1*8)
    all_info['dlat_dlon']=list(struct.unpack('f'*2,context))
    dlat_dlon=struct.unpack('f'*2,context)

    binFile.seek(location+220)
    context=binFile.read(4*1)
    all_info['nodata']=struct.unpack('f'*1,context)[0]
    
    binFile.seek(location+224)
    context=binFile.read(4*1)
    all_info['levelbytes']=struct.unpack('i'*1,context)[0]
    
    binFile.seek(location+228)
    context=binFile.read(2*1)
    all_info['levelnum']=struct.unpack('h'*1,context)[0]
    
    binFile.seek(location+230)
    context=binFile.read(2*1)
    all_info['amp']=struct.unpack('h'*1,context)[0]
    
    binFile.seek(location+232)
    context=binFile.read(2*1)
    all_info['compmode']=struct.unpack('h'*1,context)[0]
    
    binFile.seek(location+234)
    context=binFile.read(2*1)
    all_info['dates']=struct.unpack('H'*1,context)[0]
    
    binFile.seek(location+236)
    context=binFile.read(4*1)
    all_info['seconds']=struct.unpack('i'*1,context)[0]
    
    binFile.seek(location+240)
    context=binFile.read(2*1)
    all_info['min_value']=struct.unpack('h'*1,context)[0]
    
    binFile.seek(location+242)
    context=binFile.read(2*1)
    all_info['max_value']=struct.unpack('h'*1,context)[0]
    
    binFile.seek(location+244)
    context=binFile.read(2*1)
    all_info['enablemultiLevel']=struct.unpack('h'*1,context)[0]

    binFile.seek(location+246)
    context=binFile.read(2*1)
    all_info['height_Ftime']=struct.unpack('h'*1,context)[0]

    binFile.seek(location+248)
    context=binFile.read(4*1)
    all_info['index_nextbytes']=struct.unpack('i'*1,context)[0]
    
    binFile.seek(location+256)
    if all_info['index_nextbytes'] != 0:
        datasize=all_info['index_nextbytes']-location-256
        print('location:'+str(location))
        print('datasize:'+str(datasize))
    else:
        datasize=filesize-location-256
    context=binFile.read(datasize)
    yxn=struct.unpack('h'*int(datasize/2),context)    
    
#    data=np.zeros((int((latlon_domain[2]-latlon_domain[0])/dlat_dlon[0]+1),
#                   int((latlon_domain[3]-latlon_domain[1])/dlat_dlon[1]+1)))
    data=np.zeros(all_info['rows_cols'])
    panduan=0
    for i in yxn:
        if panduan==0:
            y=i
            panduan+=1
            continue
        elif panduan==1:
            x=i
            panduan+=1
            continue
        elif panduan==2:
            n0=0
            n=i
            panduan+=1
            continue
        elif panduan==3:
            try:
                data[y,x+n0]=i
                n0+=1
                if n0==n:
                    panduan=0
                continue
            except IndexError:
#                print(y,x,n)
                break
    all_info['data']=data/all_info['amp']
    all_info_list.append(all_info)    
    if all_info['index_nextbytes'] == 0:
        return all_info_list
    else:
        return read_latlon_each(all_info_list,binFile,filesize,all_info['index_nextbytes'])

def read_latlon(filepath):
    binFile=open(filepath,'rb')
    
    filesize=os.path.getsize(filepath)
    data=read_latlon_each([],binFile,filesize,0)  
    binFile.close()
    return data

def find_index(lst):
    out = []
    fun = lambda x:x[1]-x[0]
    for k,g in groupby(enumerate(lst),fun):
        l1 = [j for i, j in g]
        out.append(l1)
    return out

def int2bytes(x):
    return struct.pack('h',int(x))

def write_latlon_each(filename,data_dict,index_thisbytes):
    rows=data_dict['rows_cols'][1] #6200
    cols=data_dict['rows_cols'][0] #4200
    image_out=data_dict['data'].T*data_dict['amp']

    out = []
    for y in range(cols):
        tmparray = np.array(image_out[:,y]).reshape((-1,1))
        tmp_where= np.where(tmparray > 100)
        tmp_list = find_index(tmp_where[0])
        for tmp_ in tmp_list:
            out.extend([y,tmp_[0],len(tmp_)])
            out.extend(tmparray[tmp_])
    out.extend([-1,-1,-1])
    data_b = b''.join(i for i in map(int2bytes,out))       
    '''数据部分'''
#    out=[]
#    start=False
#    end =False
#    for y in range(cols):
#        for x in range(rows):
#            if image_out[x,y] > 0 and not start:
#                out.extend([y,x])
#                count1=0
#                out_tmp=[]
#                out_tmp.append(int(image_out[x,y]))
#                count1=count1+1
#                start = True
#                end = False		
#            elif start and not end and image_out[x,y] > 0:
#                out_tmp.append(int(image_out[x,y]))
#                count1=count1+1
#            elif start and not end and image_out[x,y] <= 0:
#                end= True
#                start=False				
#                out.append(count1)
#                out.extend(out_tmp)		
    
    
    
    
    
    
    #加入结束判断符


    '''文件头部分'''
    dataname= filename.encode('utf-8')+b'\x00'*(128-len(filename))
    varname ='CR'.encode('utf-8')+ b'\x00'*(32-len('CR'))
    char    ='dBZ'.encode('utf-8')+ b'\x00'*(16-len('dBZ'))
    label   = 0 #unsigned short
    unitlen = 2 #short
    slat=data_dict['latlon_domain'][0] #float
    wlon=data_dict['latlon_domain'][1]#float
    nlat=data_dict['latlon_domain'][2]#float
    elon=data_dict['latlon_domain'][3]#float
    clat=data_dict['latlon_domain'][4]#float
    clon=data_dict['latlon_domain'][5]#float
    rows=data_dict['rows_cols'][0] #	int
    cols=data_dict['rows_cols'][1] #	int
    dlat=data_dict['dlat_dlon'][0] #float
    dlon=data_dict['dlat_dlon'][1] #float
    nodata=0.0 #float
    levelbytes =0  #long
    levelnum=0 #short
    amp= 10 #short
    compmode =1 #short 
    dates = data_dict['dates'] #unsigned short
    
    seconds= data_dict['seconds'] #int
    
    min_value =  0 #short
    max_value =  0 #short
    try:
        height_Ftime = data_dict['height_Ftime']
    except:
        height_Ftime = 0
    try:
        enablemultiLevel= data_dict['enablemultiLevel']
    except:
        enablemultiLevel= 0
    try:
        index_nextbytes = data_dict['index_nextbytes']
    except:
        index_nextbytes = index_thisbytes + 256 + len(out)*2

    head =dataname + varname + char +struct.pack('Hh6f2i3fi3hHi2h2hi2h', label,unitlen,slat,wlon,nlat,
                                                 elon,clat,clon,rows,cols,dlat,dlon,nodata,
                                                 levelbytes,levelnum,amp,compmode,
                                                 dates,seconds,min_value,max_value,
                                                 enablemultiLevel,height_Ftime,
                                                 index_nextbytes,0,0);
                                                 
    return head+data_b,index_nextbytes
def write_latlon_data(data_dict_in):
    data_dict = data_dict_in.copy()
    
    cols = data_dict['rows_cols'][0]
    image_out = data_dict['data'].T * data_dict['amp']
    out = []
    for y in range(cols):
        tmparray = np.array(image_out[:,y]).reshape((-1,1))
        tmp_where= np.where(tmparray > 100)
        tmp_list = find_index(tmp_where[0])
        for tmp_ in tmp_list:
            out.extend([y,tmp_[0],len(tmp_)])
            out.extend(tmparray[tmp_])
    out.extend([-1,-1,-1])
    
    data_b = b''.join(i for i in map(int2bytes, out))
    return data_b
def write_latlon_head(filename, data_dict, index_thisbytes, data_b):
    dataname= filename.encode('utf-8')+b'\x00'*(128-len(filename))
    varname ='CR'.encode('utf-8')+ b'\x00'*(32-len('CR'))
    char    ='dBZ'.encode('utf-8')+ b'\x00'*(16-len('dBZ'))
    label   = 0 #unsigned short
    unitlen = 2 #short
    slat=data_dict['latlon_domain'][0] #float
    wlon=data_dict['latlon_domain'][1]#float
    nlat=data_dict['latlon_domain'][2]#float
    elon=data_dict['latlon_domain'][3]#float
    clat=data_dict['latlon_domain'][4]#float
    clon=data_dict['latlon_domain'][5]#float
    rows=data_dict['rows_cols'][0] #	int
    cols=data_dict['rows_cols'][1] #	int
    dlat=data_dict['dlat_dlon'][0] #float
    dlon=data_dict['dlat_dlon'][1] #float
    nodata=0.0 #float
    levelbytes =0  #long
    levelnum=0 #short
    amp= 10 #short
    compmode =1 #short 
    dates = data_dict['dates'] #unsigned short
    seconds= data_dict['seconds'] #int
    min_value =  0 #short
    max_value =  0 #short
    try:
        height_Ftime = data_dict['height_Ftime']
    except:
        height_Ftime = 0
    try:
        enablemultiLevel= data_dict['enablemultiLevel']
    except:
        enablemultiLevel= 0
    try:
        index_nextbytes = data_dict['index_nextbytes']
    except:
        index_nextbytes = index_thisbytes + 256 + len(data_b)*2

    head =dataname + varname + char +struct.pack('Hh6f2i3fi3hHi2h2hi2h', label,unitlen,slat,wlon,nlat,
                                                 elon,clat,clon,rows,cols,dlat,dlon,nodata,
                                                 levelbytes,levelnum,amp,compmode,
                                                 dates,seconds,min_value,max_value,
                                                 enablemultiLevel,height_Ftime,
                                                 index_nextbytes,0,0);
    return head, index_nextbytes

def write_latlon(filepath,data_dict_list):
    filename=filepath.split('/')[-1]
    outpath='/'.join(filepath.split('/')[:-1])
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    index_thisbytes = 0
    # 单层
    if len(data_dict_list) == 1:
        data_dict_list[0]['index_nextbytes'] = 0
        write_b,index_nextbytes= write_latlon_each(filename,data_dict_list[0],
                                                   index_thisbytes)
    # 多层
    else:
        head_list = []
        write_out = b''
        
        
        data_b_list = list(map(write_latlon_data, data_dict_list))
        
        
        for i in range(len(data_dict_list)):
            
            dict_tmp = data_dict_list[i].copy()
            try:
                del dict_tmp['index_nextbytes']
            except:
                1
            if i == len(data_dict_list)-1:
                data_dict_list[i]['index_nextbytes'] = 0
            elif i == 0:
                data_dict_list[i]['enablemultiLevel'] = 1
            head , index_thisbytes= write_latlon_head(filename,dict_tmp,
                                                       index_thisbytes,data_b_list[i])
            head_list.append(head)
            write_out += head + data_b_list[i]

    with open(filepath, 'wb') as f:
        f.write(write_out)
    return 0

# In[]
filepath='D:/nriet/雷达图识别/全国数据/aaa/'
filename='test.latlon'
#filein='D:/nriet/雷达图识别/全国数据/Z_RADA_C_BABJ_20180523004741_P_ACHN.QREF000.20180523.003600.latlon'
filein='D:/nriet/雷达图识别/程序/version_0.2/out/ACHN/CR/20180917/MOP_ACHN_CR_20180917064200.latlon'
#filepath='D:/nriet/雷达图识别/程序/version_0.2/out/ACHN/CR/20180917/'
#filename='MOP_ACHN_CR_20180917065400.latlon'
cc=read_latlon(filein)
del cc[0]['enablemultiLevel'],cc[0]['index_nextbytes']
dd=[cc[0],cc[0],cc[0],cc[0],cc[0]]
time1=time.time()
write_out=write_latlon(filepath+filename,dd)
print(time.time()-time1)
# In[]
#ee=read_latlon(filepath+filename)
