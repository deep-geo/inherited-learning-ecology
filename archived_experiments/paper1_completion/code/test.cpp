#define main simulator_main
#include "sim.cpp"
#undef main
int main(){
 mt19937_64 rng(771);normal_distribution<double> norm(0,1);RotationAudit ra;
 for(int trial=0;trial<10000;trial++){array<double,D>a{};for(int s=0;s<NS;s++)for(int k=0;k<3;k++)a[3*s+k]=s%5?norm(rng):0.;auto b=rotate_states(a,rng,ra);for(int s=0;s<NS;s++)if(s%5==0)for(int k=0;k<3;k++)assert(b[3*s+k]==0);}
 assert(ra.mean_error<1e-12&&ra.row_norm_error<1e-12&&ra.contrast_error<1e-12&&ra.support_error==0);
 double worst=1;for(int seed=0;seed<20;seed++){mt19937_64 r(70000+seed);uniform_real_distribution<double>u(0,1);
 for(int target=0;target<3;target++){array<double,D>w{};double energy=target==2?3:1,resource=target==1?.9:0,density=.5;int st=state(energy,resource,can_divide(energy,density));
 for(int t=0;t<600;t++){auto p=prob(w,st);double v=u(r);int a=v<p[0]?0:v<p[0]+p[1]?1:2;double reward=action_utility(energy,resource,density,a);w[3*st+a]+=.2*(reward-w[3*st+a]);}
 double correct=prob(w,st)[target];worst=min(worst,correct);assert(correct>=.9);}}
 cout<<"{\"bins\":"<<BINS<<",\"rotation_trials\":10000,\"gate_seeds\":20,\"gate_scenarios\":3,\"minimum_correct_probability\":"<<worst<<",\"passed\":true}"<<endl;
}
