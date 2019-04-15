# -*- coding: utf-8 -*-
"""
Created on Mon Oct  1 09:29:49 2018

@author: siwo
"""

import struct
from PIL import Image
import numpy as np
import time
import sys,os
path_code='./'
sys.path.append(path_code+'casting/')
from get_latlon_f import get_latlon
from u_util_log import get_log,write_log
from cast.optical_flow_f import optical_flow
# In[] 读写文件
def write_latlon(picfile,datafile):
    #从文件路径中提取关键字
    name=picfile.split('/')[-1]
    factor=name.split('_')[-2]
    region=name.split('_')[-1][0:4]
    datatime=name.split('_')[4]
    #生成输出文件名
    outname='MOP_'+region+'_'+'factor'+'_'+datatime+'.latlon'
    #获取全国地图的经纬度网格
    lon,lat=get_latlon('ACHN')
    #获取图像中的经纬度极值范围,生成0.04间隔的等经纬度网格
    lon_min1=int(np.min(lon)*100)//4/25
    lon_max1=int(np.max(lon)*100)//4/25 +0.04
    lat_min1=int(np.min(lat)*100)//4/25
    lat_max1=int(np.max(lat)*100)//4/25 +0.04
    #生成0.04格距的网格
    grid_x, grid_y = np.mgrid[lon_min1:lon_max1+0.04:0.04, lat_min1:lat_max1+0.04:0.04]
    #生成网格对应的空数据
    grid_z1=np.zeros([np.shape(grid_x)[0],np.shape(grid_x)[1]])
    #获得图像中对应的网格点的数值
    out_all=pic2data(picfile)
    #如果返回空集合，则返回1退出
    if out_all==[]:
        return 1
    #放大系数
    fdxs=10
    #乘以放大系数
    out_all[:,2]=out_all[:,2]*fdxs
    try:
        # In[] 打开文件读取latlon文件
        with open (datafile,'rb+') as f:
            #从256个字节开始往后读数据
            f.seek(256)
            #获得文件中头文件以外的数据大小
            datasize=os.path.getsize(datafile)-256
            #读取数据
            context1=f.read(datasize)
            #获取有数值的点的信息
            yxn=struct.unpack('h'*int(datasize/2),context1)
            #初始判断符为0
            panduan=0
            #读取原始latlon文件中数据，挨个读取yxn的数值并写入grid_z1中
            for i in yxn:
                #panduan为0则该值为y
                if panduan==0:
                    y=i
                    panduan+=1
                    continue
                #panduan为0则该值为x
                elif panduan==1:
                    x=i
                    panduan+=1
                    continue
                #panduan为0则该值为n
                elif panduan==2:
                    n0=0
                    n=i
                    panduan+=1
                    continue
                #panduan为0则该值为数值
                elif panduan==3:
                    grid_z1[x+n0,y]=i
                    n0+=1
                    if n0==n:
                        panduan=0
                    continue
            #将新的区域的数据写入latlon中
            for i in out_all:
                grid_z1[int(round((i[1]-lon_min1)/0.04)),
                            int(round((i[0]-lat_min1)/0.04))]=i[2]
            image_out=grid_z1
            #生成latlon文件数据
            out=[]
            for y in range(0,np.shape(grid_z1)[1],1): #y
                ifFirst=True
                for x in range(0,np.shape(grid_z1)[0],1):
                    if image_out[x,y] > 0:
                        if ifFirst:
                            if x!=np.shape(grid_z1)[0]-1:
                                ifFirst=False
                                out_tmp=[]
                                count=1
                                out_tmp.extend([image_out[x,y]])
                            else:
                                out.extend([y,x,1])
                                out.extend([image_out[x,y]])
                        else:
                            if x!=np.shape(grid_z1)[0]-1:
                                out_tmp.extend([image_out[x,y]])
                                count+=1
                            else:
                                out_tmp.extend([image_out[x,y]])
                                count+=1
                                out.extend([y,x-count+1,count])
                                out.extend(out_tmp)
                    elif image_out[x,y]==0 and not ifFirst:
                        out.extend([y,x-count,count])
                        out.extend(out_tmp)
                        ifFirst=True
            #加入结束判断符
            out.extend([-1,-1,-1])
            #将out转成二进制
            for i in out:
                try:
                    data_b+=struct.pack('h',int(i))
                except NameError:
                    data_b=struct.pack('h',int(i))
            #删除256以后的值
            f.truncate(256)
            #从256开始写入新的数据
            f.seek(256)
            f.write(data_b)
            return 0
    #不存在原始文件
    except FileNotFoundError:
        # In[]将新的区域的数据写入latlon中
        for i in out_all:
            grid_z1[int(round((i[1]-lon_min1)/0.04)),
                        int(round((i[0]-lat_min1)/0.04))]=i[2]   
        image_out=grid_z1
        #生成文件
        out=[]
        for y in range(0,np.shape(grid_z1)[1],1): #y
            ifFirst=True
            for x in range(0,np.shape(grid_z1)[0],1):
                if image_out[x,y] > 0:
                    if ifFirst:
                        if x!=np.shape(grid_z1)[0]-1:
                            ifFirst=False
                            out_tmp=[]
                            count=1
                            out_tmp.extend([image_out[x,y]])
                        else:
                            out.extend([y,x,1])
                            out.extend([image_out[x,y]])
                    else:
                        if x!=np.shape(grid_z1)[0]-1:
                            out_tmp.extend([image_out[x,y]])
                            count+=1
                        else:
                            out_tmp.extend([image_out[x,y]])
                            count+=1
                            out.extend([y,x-count+1,count])
                            out.extend(out_tmp)
                elif image_out[x,y]==0 and not ifFirst:
                    out.extend([y,x-count,count])
                    out.extend(out_tmp)
                    ifFirst=True   
        #加入结束判断符
        out.extend([-1,-1,-1])
        #将out转成二进制
        for i in out:
            try:
                data_b+=struct.pack('h',int(i))
            except NameError:
                data_b=struct.pack('h',int(i))
        
        # In[]'''生成文件头'''
        
        
        dataname= outname.encode('utf-8')+b'\x00'*(128-len(outname))
        varname =factor.encode('utf-8')+ b'\x00'*(32-len(factor))
        char    ='dBZ'.encode('utf-8')+ b'\x00'*(16-len('dBZ'))
        label   = 0 #unsigned short
        unitlen = 2 #short
        slat=lat_min1 #float
        wlon=lon_min1#float
        nlat=lat_max1#float
        elon=lon_max1#float
        clat=(slat+nlat)/2#float
        clon=(wlon+elon)/2#float
        rows=np.shape(grid_z1)[1] #	int
        cols=np.shape(grid_z1)[0] #	int
        dlat=0.04 #float
        dlon=0.04 #float
        nodata=0.0 #float
        levelbytes =0  #long
        levelnum=0 #short
        amp= fdxs #short
        compmode =1 #short 
        dates = 0 #unsigned short
        seconds= 0 #int
        min_value =  0 #short
        max_value =  0 #short
        #reserved = 
#        head =dataname + varname + char +struct.pack('Hh6f2i3fq3hHi2h6h', label,unitlen,slat,wlon,nlat,
#                                                     elon,clat,clon,rows,cols,0.04,0.04,nodata,
#                                                     levelbytes,levelnum,amp,compmode,
#                                                     dates,seconds,min_value,max_value,
#                                                     0,0,0,0,0,0);
        head =dataname + varname + char +struct.pack('Hh6f2i3fi3hHi2h6h', label,unitlen,slat,wlon,nlat,
                                                     elon,clat,clon,rows,cols,dlat,dlon,nodata,
                                                     levelbytes,levelnum,amp,compmode,
                                                     dates,seconds,min_value,max_value,
                                                     0,0,0,0,0,0);
        # In[] '''存储'''
        
        all_out=head+data_b
        #将二进制数据写入文件
        with open(datafile, 'wb') as f:
            f.write(all_out)
        return 0

# In[]
#图像中提取数据
def pic2data(pathname,region,factor = 'CR'):
    try:
        '''各区域对应图例坐标、左上角、右下角经纬度'''
        '''图片分辨率改变时修改这里的图例位置'''
        region_all={'AECN':(523,537,597,793,113.506,38.8444,124.2670,23.1044), #华东
                    'ACCN':(722,333,798,589,103.626,35.3322,120.005,24.0566), #华中
                    'ACHN':(948,613,1021,869,65.6571,46.4849,126.862,13.061),#全国
                    'ANCN':(725,5  ,799,261,104.643,43.0878,122.636,31.1917), #华北
                    'ANEC':(723,564,797,820,114.539,54.224,131.91,36.3301), #东北
                    'ABCJ':(884,98 ,955,348,96.4697,34.7539,126.494,25.0003), #长江流域
                    'ABHH':(692,250,757,499,107.015,40.9176,123.65,30.4626), #黄淮流域
                    'ACES':(721,537,789,789,103.491,35.7671,128.508,13.2104), #东南沿海
                    'ASCN':(725,338,791,589,104.654,27.6771,121.318,16.104), #华南
                    'ANWC':(749,6  ,1017,255,65.4922,43.212,109.31,29.4932),#西北
                    'ASWC':(727,10 ,791,218,96.1597,34.8143,112.812,20.7235)  #西南
                    }
        #'R','CR'的颜色
        if factor in ['R','CR']:
            '''R & CR'''
            colors={(1, 160, 246, 255):12.5,
                    (0, 216, 0, 255):22.5,
                    (255, 0, 240, 255):62.5,
                    (231, 192, 0, 255):37.5,
                    (214, 0, 0, 255):52.5,
                    (192, 0, 0, 255):57.5,
                    (173, 144, 240, 255):72.5,
                    (150, 0, 180, 255):67.5,
                    (0, 236, 236, 255):17.5,
                    (255, 144, 0, 255):42.5,
                    (255, 0, 0, 255):47.5,
                    (1, 144, 0, 255):27.5,
                    (255, 255, 0, 255):32.5}
        #'''VIL的颜色'''
        elif factor == 'VIL':
            colors={(1, 255, 0, 255):12.5,
                    (0, 200, 0, 255):17.5,
                    (255, 0, 240, 255):57.5,
                    (231, 192, 0, 255):32.5,
                    (214, 0, 0, 255):47.5,
                    (192, 0, 0, 255):52.5,
                    (173, 144, 240, 255):72.5,
                    (0, 236, 236, 255):8.5,
                    (120, 0, 132, 255):67.5,
                    (255, 144, 0, 255):37.5,
                    (255, 0, 0, 255):42.5,
                    (216, 0, 156, 255):62.5,
                    (255, 255, 0, 255):27.5,
                    (1, 144, 0, 255):22.5}
        #'''OHP的颜色'''
        elif factor == 'OHP':
            colors={(255, 0, 240, 255):112.5, #100-125
                    (214, 0, 0, 255):69, #63-75
                    (192, 0, 0, 255):87.5,#75-100
                    (173, 144, 240, 255):130, #130-
                    (0, 236, 236, 255):17.5, #10-25
                    (255, 144, 0, 255):44, #38-50
                    (255, 0, 0, 255):56.5, #50-63
                    (0, 0, 246, 255):2.5, #0-5
                    (255, 255, 0, 255):31.5, #25-38
                    (1, 160, 246, 255):7.5} #5-10
        '''河流、行政边界、文字的颜色'''
        word_color=[(104, 104, 104, 255),
                    #(253, 255, 254, 255),
                    (204, 204, 204, 255),
                    (190, 232, 255, 255),
                    (156, 156, 156, 255),
                    (130, 130, 130, 255)]
        
        '''打开文件'''
        img_src = Image.open(pathname)
        img_size=img_src.size
        region_del=region_all[region]
        #定义和图片大小一致的0矩阵
        image_value=np.zeros((img_size[0],img_size[1]))
        src_strlist = img_src.load()
        '''获取格点数据，没有数据为0，河流、行政区域、文字数据为1'''
        for i in range(0,img_size[0],1):
            for j in range(0,img_size[1],1):
                if src_strlist[i,j] in colors: #是否有数据
                    image_value[i,j]=colors[src_strlist[i,j]]
                elif src_strlist[i,j] in word_color: #是否是河流等
                    image_value[i,j]=1
                else: #是不需要的点
                    image_value[i,j]=0
        '''找到图例并填充为0'''
        image_value[region_del[0]:region_del[2],region_del[1]:region_del[3]]=0
        
        '''对河流、文字、行政边界的点进行插值'''
        image_out=np.copy(image_value)
        for i in range(0,img_size[0],1):
            for j in range(0,img_size[1],1):
                #判断是否为河流等点
                if image_value[i,j]==1:
                    sum_value=0  #周围所有有效点的值的和
                    count_1=0    #附近河流等点的个数
                    count_0=0    #附近无效点的个数
                    count_c=0    #附近数据点的个数
                    #取该点周围8各点进行判断
                    for n in [(i-1,j-1),(i-1,j  ),(i-1,j+1),
                              (i  ,j-1),          (i  ,j+1),
                              (i+1,j-1),(i+1,j  ),(i+1,j+1)]:
                        if image_value[n] > 1:
                            count_c += 1
                            sum_value += image_value[n]
                        elif image_value[n] == 1:
                            count_1 += 1
                        else:
                            count_0 += 1
                    #周围没有数据点，且有无效点
                    if count_c == 0 and count_0 > 0:
                        image_out[i,j]=0
                    #有数据点
                    elif count_c >0:
                        try:
                            #数据点占多数
                            if count_c / count_0 > 0.5:
                                image_out[i,j]=sum_value/count_c
                            #数据点占少数
                            elif count_c / count_0 <= 0.5:
                                image_out[i,j]=0
                        #无效点个数可能为0
                        except ZeroDivisionError: 
                            image_out[i,j]=sum_value/count_c
                    #数据点和无效点都没有
                    elif count_1 == 8:
                        #判断再往外的一层
                        for n in [(i-2,j-2),(i-2,j-1),(i-2,j  ),(i-2,j+1),(i-2,j+2),
                                  (i-1,j-2)                              ,(i-1,j+2),
                                  (i  ,j-2)                              ,(i  ,j+2),
                                  (i+1,j-2)                              ,(i+1,j+2),
                                  (i+2,j-2),(i+2,j-1),(i+2,j  ),(i+2,j+1),(i+2,j+2)]:
                            if image_value[n] > 1:
                                count_c += 1
                                sum_value += image_value[n]
                            elif image_value[n] == 1:
                                count_1 += 1
                            else:
                                count_0 += 1
                        #没有数据点
                        if count_c == 0:
                            image_out[i,j]=0
                        #有数据点
                        elif count_c >0:
                            try:
                                #数据点占多数
                                if count_c / count_0 > 0.5:
                                    image_out[i,j]=sum_value/count_c
                                #数据点占少数
                                elif count_c / count_0 <= 0.5:
                                    image_out[i,j]=0
                            #无效点个数可能为0
                            except ZeroDivisionError: 
                                image_out[i,j]=sum_value/count_c
        '''坐标处理'''
        #转置
        image_out=np.transpose(image_out)
        #颠倒y
        image_out=image_out[::-1]
        #得到经纬度转换后的原始网格对应的经纬度信息
        lon,lat=get_latlon(region)    
        #生成离散点数据
        out_index=np.argwhere(image_out > 0)
        out_all=np.zeros((len(out_index),3))

        out_all[:,0]=lat[out_index[:,0],out_index[:,1]]
        out_all[:,1]=lon[out_index[:,0],out_index[:,1]]
        out_all[:,2]=image_out[out_index[:,0],out_index[:,1]]
        #返回坐标转换后的经纬度对应的数据
        return out_all
    #如果有问题则返回空list
    except:
        return []
# In[]
def main_2latlon(factor,filelist):
    time1=time.time()
    '''文件路径'''
    path_code='./'
    #图片数据来源
#    path='/home/data/CMACast/RADA_MOSAIC/NOR/IMG'
    path='D:\\nriet\\雷达图识别\\LeiDa\\ChangGui'
    #log文件地址
    logpath= path_code+'casting/'+factor+'.log'
    #读取log文件
#    print(1)
    filelist_casting=get_log(logpath) 
    #输出数据地址
    outpath='./out'
#    outpath='/home/data/CMACast/RADA_MOSAIC/data'
    #需要处理的地图区域
    region_all=['AECN', #华东
                'ACCN', #华中
                'ANCN', #华北
                'ANEC', #东北
                'ABCJ', #长江流域
                'ABHH', #黄淮流域
                'ACES', #东南沿海
                'ASCN', #华南
                'ANWC',#西北
                'ASWC'  #西南
                ]
    # 计算最新的多少文件
    n=200
    #查看log文件最后的标识符
    if filelist_casting[-1]=='Z__0':
        #Z__0为程序没有运行
        run=1
        #将Z__0写入，表示程序正在运行
        filelist_casting[-1]='Z__9'
        #写入文件   
        write_log(logpath,filelist_casting[-min([n,len(filelist_casting)]):])  # local
    else:
        #程序正在运行，返回0
        run=0
    print(factor+' starts:')
    #如果run为1则进行计算，否则不进行计算
    print(run)
    if run==1:
        #初始化需要处理的文件列表
        filelists=[]
        for i in filelist[-n:]:
            filenames=i.split('_')
            #判断文件名中是否有factor参数
            if filenames[-2]==factor:
                #将包含factor的文件名存入filelists
                filelists.append(i)
        print(len(filelists))
        #逐个对filelists中的文件进行处理
        for file in filelists:
            #判断文件头是否符合所需文件的命名规则
            if file[0:6]=='Z_RADA':
                filenames=file.split('_')
                #获取文件所在区域
                region=filenames[-1][0:4]
                #获取文件时间
                date=filenames[4]
                #判断文件区域是否在需要的区域中 并且 文件没有被处理过
                if region in region_all and (file not in filelist_casting):
                    #设定文件输出路径，没有的话则创建新的目录
                    foldername=outpath+'/'+'ACHN'
                    if not os.path.exists(foldername):
                        os.mkdir(foldername)
    #                foldername=foldername+'\\'+factor
                    foldername=foldername+'/'+factor
                    if not os.path.exists(foldername):
                        os.mkdir(foldername)
    #                foldername=foldername+'\\'+date[0:8]
                    foldername=foldername+'/'+date[0:8]
                    if not os.path.exists(foldername):
                        os.mkdir(foldername)
    #                datafile=foldername+'\\MOP_' + 'ACHN' + '_' + date +'.latlon'
                    datafile=foldername+'/MOP_ACHN_' + factor+ '_' + date +'.latlon'
                    picfile=path+'/'+file
                    #执行数据写入
                    aa=write_latlon(picfile,datafile)
                    #如果返回为1，文件写入出现问题
                    if aa:
                        print('*******-----------*******')
                        print('casting fail:'+file)
                        print('*******-----------*******')
                    #返回为0，文件写入正常
                    else:   
                        #将文件名加入filelist_casting中
                        filelist_casting.append(file)
                        print(factor+' casting done:'+file)
                        #删除文件
                        os.remove(picfile)
                        #排序
                        filelist_casting.sort()
                        #将filelist_casting写入log文件
                        write_log(logpath,filelist_casting[-min([n,len(filelist_casting)]):])
        #排序
        filelist_casting.sort()
        #文件最后加入未工作判断符
        filelist_casting[-1]='Z__0'
        #将filelist_casting写入log文件        
        write_log(logpath,filelist_casting[-min([n,len(filelist_casting)]):])  # local
    #结束时间
    time2=time.time()
    #输出单个参数所有文件执行的时间
    print(['timecost:',time2-time1])
    
# In[]
def latlon2grid(latlon):
    #获取图像中的经纬度极值范围,生成0.04间隔的等经纬度网格
    lon_min1 = 108
    lon_max1 = 132
    lat_min1 = 20
    lat_max1 = 40
    #生成0.04格距的网格
    grid_x, grid_y = np.mgrid[lon_min1:lon_max1+0.04:0.04, lat_min1:lat_max1+0.04:0.04]
    #生成网格对应的空数据
    grid_z1=np.zeros([np.shape(grid_x)[0],np.shape(grid_x)[1]])
    for i in latlon:
        if lon_min1 <= i[1] <= lon_max1 and lat_min1 <= i[0] <= lat_max1:
            grid_z1[int(round(abs((i[1]-lon_min1)/0.04))),
                        abs(int(round((i[0]-lat_min1)/0.04)))]=i[2]  
    return grid_z1
# In[]
#多进程执行文件
if __name__=="__main__":

    ABHH1='D:\\nriet\\雷达图识别\\LeiDa\\ChangGui\\Z_RADA_C_BABJ_20180915151200_P_DOR_RDCP_CR_ABHH.PNG'
    ACES1='D:\\nriet\\雷达图识别\\LeiDa\\ChangGui\\Z_RADA_C_BABJ_20180915151200_P_DOR_RDCP_CR_ACES.PNG'
    ABHH2='D:\\nriet\\雷达图识别\\LeiDa\\ChangGui\\Z_RADA_C_BABJ_20180915153600_P_DOR_RDCP_CR_ABHH.PNG'
    ACES2='D:\\nriet\\雷达图识别\\LeiDa\\ChangGui\\Z_RADA_C_BABJ_20180915153600_P_DOR_RDCP_CR_ACES.PNG'

    ABHH_latlon_1 = pic2data(ABHH1,'ABHH','CR')
    ACES_latlon_1 = pic2data(ACES1,'ACES','CR')
    ABHH_latlon_2 = pic2data(ABHH2,'ABHH','CR')
    ACES_latlon_2 = pic2data(ACES2,'ACES','CR')
    
    latlon_1 = np.concatenate((ABHH_latlon_1,ACES_latlon_1),axis =0)
    latlon_2 = np.concatenate((ABHH_latlon_2,ACES_latlon_2),axis =0)   
    
    grid_z1 = latlon2grid(latlon_1)
    grid_z2 = latlon2grid(latlon_2)
    
    n_in = (36 - 12)/60
    
    dt = 30
    n  = 2
    ts = np.arange(dt, dt*n +1, dt)

    ref_out = optical_flow(grid_z1, grid_z2, n_in, ts)
#name='Z_RADA_C_BABJ_20180915151200_P_DOR_RDCP_R_ACHN.PNG'
#    outpath='D:\\nriet\\雷达图识别\\data_out\\'
##    outpath='/home/data/CMACast/RADA_MOSAIC/data/ACHN/'
#    datafile=outpath+region+'\\'+factor+'\\'+date[0:8]+'\\MOP_' + region + '_' + date +'.latlon'
#for region in region_all:
#    picfile=path+'Z_RADA_C_BABJ_20180917063600_P_DOR_RDCP_CR_' + region + '.PNG'
#    write_latlon(picfile,datafile)
# In[]
#画图
#import matplotlib.pyplot as plt
##    grid_z2=np.transpose(grid_z1)
##实例basemap对象
#b_map = Basemap( projection='lcc',lat_1=30, lat_2=60, lon_0=110, llcrnrlon=80, urcrnrlon=140, 
#                llcrnrlat=10,urcrnrlat=51)  
##初始化图片大小               
#fig=plt.figure(figsize=(24,12))
##将格点经纬度数据转为x，y网格点
#x, y = b_map(grid_x, grid_y)   
##将grid_z1中小于等于0的数据变为nan
#grid_z1=np.where(grid_z1>0,grid_z1,np.nan)
##设定数据颜色范围
#colorlist=[(1/255, 160/255, 246/255, 255/255),
#           (0/255, 236/255, 236/255, 255/255),
#           (0/255, 216/255, 0/255, 255/255),
#           (1/255, 144/255, 0/255, 255/255),
#           (255/255, 255/255, 0/255, 255/255),
#           (231/255, 192/255, 0/255, 255/255),
#           (255/255, 144/255, 0/255, 255/255),
#           (255/255, 0/255, 0/255, 255/255),
#           (214/255, 0/255, 0/255, 255/255),
#           (192/255, 0/255, 0/255, 255/255),
#           (255/255, 0/255, 240/255, 255/255),
#           (150/255, 0/255, 180/255, 255/255),
#           (173/255, 144/255, 240/255, 255/255)]
#from matplotlib import colors
#cmap = colors.ListedColormap(colorlist)
##绘制填色图
#cs=b_map.contourf(x, y ,grid_z1,[10,15,20,25,30,35,40,45,50,55,60,65,70,75],cmap=cmap)#,vmin=0, vmax=70)
##添加colorbar
#b_map.colorbar(cs)    
###海岸线                        
##b_map.drawcoastlines(linewidth=1.5)   
##国界线       
##b_map.drawcountries(linewidth=1.5)      
##添加省界     
#b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_CHN_shp\\gadm36_CHN_1','states',linewidth=0.5)
##添加县界
#b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_CHN_shp\\gadm36_CHN_3','states',linewidth=0.1)
#time2=time.time()
#print(time2-time1)
data=np.transpose(grid_z1.T)
#画图

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
region_all=['AECN', #华东
            'ACCN', #华中
#            'ACHN',#全国
            'ANCN', #华北
            'ANEC', #东北
            'ABCJ', #长江流域
            'ABHH', #黄淮流域
            'ACES', #东南沿海
            'ASCN', #华南
            'ANWC',#西北
            'ASWC'  #西南
            ]
lon,lat=get_latlon('ACHN')
#获取图像中的经纬度极值范围
#lon_min=np.min(lon)
#lon_max=np.max(lon)
#lat_min=np.min(lat)
#lat_max=np.max(lat)
dlon=0.04
dlat=0.04
lon_min = 108
lon_max = 132
lat_min = 20
lat_max = 40
#lon_min=latlon_domain[1]
#lon_max=latlon_domain[3]
#lat_min=latlon_domain[0]
#lat_max=latlon_domain[2]
#生成0.04间隔的等经纬度网格
#lon_min1=int(lon_min*100)//4/25
#lon_max1=int(lon_max*100)//4/25 +0.04
#lat_min1=int(lat_min*100)//4/25
#lat_max1=int(lat_max*100)//4/25 +0.04
#生成0.04格距的网格
grid_x, grid_y = np.mgrid[lon_min:lon_max+dlon:dlon, lat_min:lat_max+dlat:dlat]
#实例basemap对象
b_map = Basemap( projection='lcc',lat_1=30, lat_2=60, lon_0=110, llcrnrlon=lon_min, urcrnrlon=lon_max, 
                llcrnrlat=lat_min-10,urcrnrlat=lat_max)                 
fig=plt.figure(figsize=(24,18))
x, y = b_map(grid_x, grid_y)   
grid_z1=np.where(data>0,data,np.nan)
colorlist=[(1/255, 160/255, 246/255, 255/255),
           (0/255, 236/255, 236/255, 255/255),
           (0/255, 216/255, 0/255, 255/255),
           (1/255, 144/255, 0/255, 255/255),
           (255/255, 255/255, 0/255, 255/255),
           (231/255, 192/255, 0/255, 255/255),
           (255/255, 144/255, 0/255, 255/255),
           (255/255, 0/255, 0/255, 255/255),
           (214/255, 0/255, 0/255, 255/255),
           (192/255, 0/255, 0/255, 255/255),
           (255/255, 0/255, 240/255, 255/255),
           (150/255, 0/255, 180/255, 255/255),
           (173/255, 144/255, 240/255, 255/255)]
from matplotlib import colors
cmap = colors.ListedColormap(colorlist)
0
cs=b_map.contourf(x, y ,grid_z1,[10,15,20,25,30,35,40,45,50,55,60,65,70,75],cmap=cmap)#,vmin=0, vmax=70)
b_map.colorbar(cs)                            #添加colorbar
#b_map.drawcoastlines(linewidth=1.5)          #海岸线
#b_map.drawcountries(linewidth=1.5)           #国界线
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_CHN_shp\\gadm36_CHN_1','states',linewidth=0.5)
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_CHN_shp\\gadm36_CHN_3','states',linewidth=0.1)
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_TWN_shp\\gadm36_TWN_0','states',linewidth=0.5)
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_TWN_shp\\gadm36_TWN_2','states',linewidth=0.1)

time6 = time.time()
print(time6-time5)
#time2=time.time()
#print(time2-time1)
# In[]
from skimage import transform
data_tmp=transform.rescale(data, 4)
data = data_tmp[:-3,:-3]
dlon=0.01
dlat=0.01
lon_min = 108
lon_max = 132
lat_min = 20
lat_max = 40
#lon_min=latlon_domain[1]
#lon_max=latlon_domain[3]
#lat_min=latlon_domain[0]
#lat_max=latlon_domain[2]
#生成0.04间隔的等经纬度网格
#lon_min1=int(lon_min*100)//4/25
#lon_max1=int(lon_max*100)//4/25 +0.04
#lat_min1=int(lat_min*100)//4/25
#lat_max1=int(lat_max*100)//4/25 +0.04
#生成0.04格距的网格
grid_x, grid_y = np.mgrid[lon_min:lon_max+dlon:dlon, lat_min:lat_max+dlat:dlat]
#实例basemap对象
b_map = Basemap( projection='lcc',lat_1=30, lat_2=60, lon_0=110, llcrnrlon=lon_min, urcrnrlon=lon_max, 
                llcrnrlat=lat_min-10,urcrnrlat=lat_max)                 
fig=plt.figure(figsize=(24,18))
x, y = b_map(grid_x, grid_y)   
grid_z1=np.where(data>0,data,np.nan)
colorlist=[(1/255, 160/255, 246/255, 255/255),
           (0/255, 236/255, 236/255, 255/255),
           (0/255, 216/255, 0/255, 255/255),
           (1/255, 144/255, 0/255, 255/255),
           (255/255, 255/255, 0/255, 255/255),
           (231/255, 192/255, 0/255, 255/255),
           (255/255, 144/255, 0/255, 255/255),
           (255/255, 0/255, 0/255, 255/255),
           (214/255, 0/255, 0/255, 255/255),
           (192/255, 0/255, 0/255, 255/255),
           (255/255, 0/255, 240/255, 255/255),
           (150/255, 0/255, 180/255, 255/255),
           (173/255, 144/255, 240/255, 255/255)]
from matplotlib import colors
cmap = colors.ListedColormap(colorlist)

cs=b_map.contourf(x, y ,grid_z1,[10,15,20,25,30,35,40,45,50,55,60,65,70,75],cmap=cmap)#,vmin=0, vmax=70)
b_map.colorbar(cs)                            #添加colorbar
#b_map.drawcoastlines(linewidth=1.5)          #海岸线
#b_map.drawcountries(linewidth=1.5)           #国界线
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_CHN_shp\\gadm36_CHN_1','states',linewidth=0.5)
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_CHN_shp\\gadm36_CHN_3','states',linewidth=0.1)
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_TWN_shp\\gadm36_TWN_0','states',linewidth=0.5)
b_map.readshapefile('C:\\Users\\siwo\\Anaconda3\\envs\\test_py2\\Lib\\gadm36_TWN_shp\\gadm36_TWN_2','states',linewidth=0.1)

time6 = time.time()
print(time6-time5)