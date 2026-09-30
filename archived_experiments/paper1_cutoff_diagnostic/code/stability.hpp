#pragma once
#include <array>
#include <cmath>
#include <algorithm>
#include <cassert>
struct StableAudit { double pre=0,post_a=0,post_r=0,geometry=0,min_scale=1; int norm_hit=0,box_rows=0; };
template<size_t N> StableAudit constrain_pair(const std::array<double,N>&g,std::array<double,N>&a,std::array<double,N>&r,int rule,double Q){
 StableAudit z; for(double v:a)z.pre+=v*v;z.pre=std::sqrt(z.pre);
 double scale=z.pre>Q?Q/z.pre:1;z.norm_hit=scale<1;
 for(size_t k=0;k<N;k++){a[k]*=scale;r[k]*=scale;}
 double lo=rule==2?-.62:-1,hi=rule==2?.42:1;
 for(size_t s=0;s<N;s+=3){double alpha=1;
  if(rule>=2){for(size_t k=s;k<s+3;k++){assert(g[k]>=lo-1e-12&&g[k]<=hi+1e-12);
   for(double v:{a[k],r[k]}){if(v>0)alpha=std::min(alpha,(hi-g[k])/v);if(v<0)alpha=std::min(alpha,(lo-g[k])/v);}}
   alpha=std::max(0.,alpha);if(alpha<1){alpha*=.99;z.box_rows++;}}
  z.min_scale=std::min(z.min_scale,alpha*scale);double aa=0,rr=0,ma=0,mr=0;
  for(size_t k=s;k<s+3;k++){a[k]*=alpha;r[k]*=alpha;aa+=a[k]*a[k];rr+=r[k]*r[k];ma+=a[k];mr+=r[k];}
  z.geometry=std::max({z.geometry,std::abs(aa-rr),std::abs(ma-mr)});z.post_a+=aa;z.post_r+=rr;
 }
 z.post_a=std::sqrt(z.post_a);z.post_r=std::sqrt(z.post_r);assert(z.geometry<1e-10);assert(z.post_a<=Q+1e-10&&z.post_r<=Q+1e-10);return z;
}
