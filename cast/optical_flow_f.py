import numpy as np
import cv2 as cv
from wind_complement import *
import semi



def optical_flow(pre,nex,dt,ts):

    pre=np.uint8(pre)
    nex=np.uint8(nex)
    flow0 = np.zeros_like(pre)

    #=====================================
    # Gunnar Farneback
    # pre:previous image
    # nex: next image
    # flow0: u,v
    # 0.5: pyr_scale
    # 3: levels of pyr
    # 15: window size
    # 3: iterations
    # 5: poly_n
    # 1.2: poly_sigma
    # 0:flags
    #=====================================

#    flow=cv.calcOpticalFlowFarneback(pre,nex,flow0,0.5,5,15,3,1,1.2,0)
    flow=cv.calcOpticalFlowFarneback(pre,nex,flow0,0.5,5,15,3,5,1.2,0)    
#    u_new0=u
#    v_new0=v
#        
#    cc=speed>0.5
#    d_speed=1
#    speed0=speed
#    while d_speed>0.01:
#
#        u_new=cv.blur(u_new0,(20,20))
#        v_new=cv.blur(v_new0,(20,20))
#        u_new[cc]=u_new0[cc]
#        v_new[cc]=v_new0[cc]
#        cc=speed>0.5
#        u_new0=u_new
#        v_new0=v_new
#        speed1=np.sqrt(u_new0**2+v_new0**2)
#        d_speed=np.max(np.abs(speed1-speed0))
#        speed0=speed1
#        print(d_speed)    



    flow0=wind_complement(flow,nex,pre,0,25)
        
    flow=flow0

#    del(nex)
#    del(pre)
#    del(flow0)     
    
    flow=flow/dt
    
    n1,n2=np.shape(nex)
    ll=len(ts)
    out_put_all=np.zeros([n1,n2,ll])
    k=0
    for t in ts:
        forecast=semi.backward(nex,flow,4,t,n1,n2)
        
        forecast1=np.ascontiguousarray(forecast)
        out_put_all[:,:,k]=forecast1
        k=k+1
    return out_put_all
