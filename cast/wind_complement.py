import numpy as np

def wind_complement(flow,dbz,pre,flag,smax):
    # flag==0 mean wind
    # flag==1 correlation track
    if  flag==0:
        v=flow[:,:,1]
        u=flow[:,:,0]
        speed=np.sqrt(u**2+v**2)
        dbz[np.where(dbz<=0)]=0
        u_mean=np.mean(u[np.where((dbz*speed)>0)])
        v_mean=np.mean(v[np.where((dbz*speed)>0)])
        #print([u_mean,v_mean])
        flow0=flow
        u[np.where((dbz*speed)<=0)]=u_mean
        v[np.where((dbz*speed)<=0)]=v_mean
        u[np.where(u>smax)]=0
        v[np.where(u>smax)]=0
        flow0[:,:,0]=u
        flow0[:,:,1]=v
        
    else:
        pre[np.isnan(pre)]=0
        dbz[np.isnan(dbz)]=0
        pre[pre<0]=0
        dbz[dbz<0]=0        
        n1,n2=np.shape(pre)
        coe=np.zeros((41,41))
        for i in np.arange(-20,20):
            for j in np.arange(-20,20):
             
                a=pre[20+i:n1-21+i,20+j:n2-21+j]
                b=dbz[20:n1-21,20:n2-21]
                a=np.reshape(a,[(n1-41)*(n2-41)])
                b=np.reshape(b,[(n1-41)*(n2-41)])
                c=np.corrcoef(a,b)
            
                coe[i+20,j+20]=c[0,1]
                del(a)
                del(b)
                del(c)
                
        k=np.unravel_index(coe.argmax(), coe.shape)
        v=flow[:,:,1]
        u=flow[:,:,0]
        speed=np.sqrt(u**2+v**2) 
        u_mean=20-k[1]
        v_mean=20-k[0]
        print(k)
        print(coe.max())
        flow0=flow
        u[np.where((dbz*speed)<=0)]=u_mean
        v[np.where((dbz*speed)<=0)]=v_mean
        u[np.where(u>smax)]=0
        v[np.where(u>smax)]=0       
        flow0[:,:,0]=u
        flow0[:,:,1]=v


    
    return flow0

    
