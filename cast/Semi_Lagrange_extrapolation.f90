


subroutine backward(echo,flow,step,time,n1,n2,dbz)
!f2py intent(in) :: echo, flow, step, time, n1, n2
!f2py intent(out):: dbz
!echo : radar reflectivity
!flow: u,v(unit:grid)
!step: n_step
!time: forecast time
implicit none
integer :: n1,n2,i,j,t,step,time
real*8 :: echo(n1,n2),flow(n1,n2,2)
real*8 :: delta_t
real*8 :: dbz(n1,n2),u(n1,n2),v(n1,n2)
real*8 :: a1(n1,n2),b1(n1,n2),a0(n1,n2),b0(n1,n2)
integer :: i0(n1,n2),j0(n1,n2),it(n1,n2),jt(n1,n2)
u=flow(:,:,1)
v=flow(:,:,2)
delta_t=(1.0*time)/step

do j=1,n2
 do i=1,n1
   it(i,j)=i
 end do
end do

do i=1,n1
do j=1,n2
   jt(i,j)=j
end do
end do

a0=0.
b0=0.
a1=0.
b1=0.

do t=1,step
   i0=int(it-b0/2.0)
   where(i0.lt.1) i0=1
   where(i0.gt.n1) i0=n1
   j0=int(jt-a0/2.0)
   where(j0.lt.1) j0=1
   where(j0.gt.n2) j0=n2
   do i=1,n1
     do j=1,n2
       a0(i,j)=delta_t*u(i0(i,j),j0(i,j))
       b0(i,j)=delta_t*v(i0(i,j),j0(i,j))
   end do
   end do
   a1=a0+a1
   b1=b0+b1
end do 
  

   it=int(it-b1)
   jt=int(jt-a1)
   where(it.lt.1) it=1
   where(it.gt.n1) it=n1
   where(jt.lt.1) jt=1
   where(jt.gt.n2) jt=n2
   echo(1,:)=0
   echo(n1,:)=0
   echo(:,1)=0
   echo(:,n2)=0
   
   do i=1,n1
   do j=1,n2
     dbz(i,j)=echo(it(i,j),jt(i,j))
   end do
   end do
 
   return  
end
