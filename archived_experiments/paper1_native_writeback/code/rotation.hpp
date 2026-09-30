#pragma once
#include <array>
#include <random>
#include <cmath>
#include <algorithm>
struct RotationAudit{double mean_error=0,row_norm_error=0,contrast_error=0,support_error=0;};
template<size_t N> inline std::array<double,N> rotate_states(const std::array<double,N>&a,std::mt19937_64&rng,RotationAudit&check){
 std::array<double,N>b{};std::uniform_real_distribution<double>u(0,1);
 for(int s=0;s<int(N/3);s++){int j=3*s;double m=(a[j]+a[j+1]+a[j+2])/3,cn=0,rn=0;for(int k=0;k<3;k++){cn+=(a[j+k]-m)*(a[j+k]-m);rn+=a[j+k]*a[j+k];}double angle=6.2831853071795864769*u(rng),x=sqrt(cn)*cos(angle),y=sqrt(cn)*sin(angle);b[j]=m+x/sqrt(2.)+y/sqrt(6.);b[j+1]=m-x/sqrt(2.)+y/sqrt(6.);b[j+2]=m-2*y/sqrt(6.);double mb=(b[j]+b[j+1]+b[j+2])/3,cb=0,rb=0;for(int k=0;k<3;k++){cb+=(b[j+k]-mb)*(b[j+k]-mb);rb+=b[j+k]*b[j+k];}check.mean_error=std::max(check.mean_error,std::abs(mb-m));check.row_norm_error=std::max(check.row_norm_error,std::abs(rb-rn));check.contrast_error=std::max(check.contrast_error,std::abs(cb-cn));if(rn==0)check.support_error=std::max(check.support_error,rb);}
 return b;
}
