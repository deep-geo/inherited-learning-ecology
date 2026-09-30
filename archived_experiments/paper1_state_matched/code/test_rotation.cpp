#include "rotation.hpp"
#include <cassert>
#include <iostream>
int main(){std::mt19937_64 rng(19517);std::normal_distribution<double>n(0,1);RotationAudit a;for(int it=0;it<10000;it++){std::array<double,384>d{};for(int s=0;s<128;s++)if(s%3==0&&!(s/16<4&&s%2==1)){for(int k=0;k<3;k++)d[3*s+k]=n(rng);if(s%2==0)d[3*s]=d[3*s+1]=d[3*s+2];}auto b=rotate_states(d,rng,a);for(int s=0;s<128;s++)if(s/16<4&&s%2==1)for(int k=0;k<3;k++)assert(b[3*s+k]==0);}
 assert(a.mean_error<1e-12&&a.row_norm_error<1e-12&&a.contrast_error<1e-12&&a.support_error==0);std::cout<<"10000 vector checks passed; max row errors "<<a.mean_error<<" "<<a.row_norm_error<<" "<<a.contrast_error<<"\n";}
