#include "rotation.hpp"
#include "stability.hpp"
#include <iostream>
int main(){std::mt19937_64 rng(1234);std::uniform_real_distribution<double>u(0,1);double err=0;
 for(int rule=1;rule<=3;rule++)for(int trial=0;trial<10000;trial++){
  std::array<double,12>g{},a{},r{};double lo=rule==2?-.62:-1,hi=rule==2?.42:1;
  for(int k=0;k<12;k++){g[k]=lo+(hi-lo)*u(rng);a[k]=(u(rng)-.5)*100;}
  for(int k=0;k<3;k++)a[k]=0;
  RotationAudit audit;r=rotate_states(a,rng,audit);auto z=constrain_pair(g,a,r,rule,.1841261006694567);
  for(int s=0;s<12;s+=3){double ma=0,mr=0,na=0,nr=0;for(int k=s;k<s+3;k++){ma+=a[k];mr+=r[k];na+=a[k]*a[k];nr+=r[k]*r[k];if(rule>=2){assert(g[k]+a[k]>=lo-1e-12&&g[k]+a[k]<=hi+1e-12);assert(g[k]+r[k]>=lo-1e-12&&g[k]+r[k]<=hi+1e-12);}}err=std::max({err,std::abs(ma-mr),std::abs(na-nr)});}
  for(int k=0;k<3;k++)assert(a[k]==0&&r[k]==0);
 }
 std::cout<<"30000 paired synthetic parents passed; max geometry error "<<err<<"\n";
}
