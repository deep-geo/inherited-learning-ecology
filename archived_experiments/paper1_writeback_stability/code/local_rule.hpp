#pragma once
#include <array>
#include <algorithm>
#include <cmath>
inline bool can_divide(double energy,double density){return energy-.12>2. && density<1.;}
inline double task_reward(double before,double after,bool born,bool dead){return (dead?0.:after)-before+.2*born-.5*dead;}
inline double action_utility(double energy,double resource,double density,int action){double after=std::min(4.,energy+(action==1?std::min(.5,resource):0.)-(action==0?.04:action==1?.08:.12));return task_reward(energy,after,action==2&&after>2&&density<1,after<=0);}
inline std::array<double,6> observation(double energy,double resource,double density,double neighbor){return {1.,energy/4.,resource,density,neighbor,can_divide(energy,density)?1.:0.};}
