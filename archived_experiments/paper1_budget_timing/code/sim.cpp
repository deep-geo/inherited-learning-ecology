#include <vector>
#include <array>
#include <random>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <cassert>
#include "local_rule.hpp"
#include "rotation.hpp"
#include "stability.hpp"
#ifndef BINS
#define BINS 8
#endif
using namespace std;constexpr int NS=BINS*BINS*2,D=NS*3;
struct Cell{bool alive=false;double e=0;int born=0,visits=0,depth=0;long id=-1;bool tracked=false,intervened=false;array<double,D>g{},th{};};
int state(double e,double r,bool div){return (clamp(int(e*BINS/4.),0,BINS-1)*BINS+clamp(int(r*BINS),0,BINS-1))*2+int(div);}
array<double,3> prob(const array<double,D>&w,int s){double m=max({w[s*3],w[s*3+1],w[s*3+2]});int n=0;for(int a=0;a<3;a++)n+=abs(w[s*3+a]-m)<1e-12;array<double,3>p;for(int a=0;a<3;a++)p[a]=.05/3+(abs(w[s*3+a]-m)<1e-12?.95/n:0);return p;}
struct Probe{int s;array<double,3>r;};
double eval(const array<double,D>&w,const vector<Probe>&v){double sum=0;for(auto&z:v){auto p=prob(w,z.s);for(int a=0;a<3;a++)sum+=p[a]*z.r[a];}return sum/v.size();}
int main(int argc,char**argv){if(argc<10)return 2;string out=argv[1];int L=stoi(argv[2]),T=stoi(argv[3]),seed=stoi(argv[4]);double eta=stod(argv[5]),lam=stod(argv[6]),mu=stod(argv[7]);int mode=stoi(argv[8]);bool random=mode==1;bool probes=stoi(argv[9]);double regen=argc>10?stod(argv[10]):.12,mortality=argc>11?stod(argv[11]):.002;double q=argc>12?stod(argv[12]):.1841261006694567;long cap=argc>13?stol(argv[13]):-1;double fraction=argc>14?stod(argv[14]):.5,bonus=argc>15?stod(argv[15]):.2;int intervention=argc>16?stoi(argv[16]):0;double childeta=argc>17?stod(argv[17]):eta;int rule=argc>18?stoi(argv[18]):0;int stop_time=argc>19?stoi(argv[19]):-1;bool fixed=argc>20?stoi(argv[20]):false;bool spaced=argc>21?stoi(argv[21]):false;assert(stop_time>=-1);assert(rule>=0&&rule<=3);assert(intervention==0||intervention==1||intervention==2);int M=L*L;mt19937_64 rng(seed),noise(seed+100000),direction(seed+200000),measure(seed+300000),counter(seed+400000);uniform_real_distribution<double>u(0,1);normal_distribution<double>normal(0,1);mt19937_64 shuffle_rng(seed+600000),state_rng(seed+800000),audit_rng(seed+900000);RotationAudit ra;double formula_error=0;double total_contrast_sq=0,total_common_sq=0,unreachable_sq=0;vector<Cell>cells(M);vector<double>resource(M,1);vector<array<int,8>>nb(M);for(int i=0;i<M;i++){int k=0;for(int dx=-1;dx<=1;dx++)for(int dy=-1;dy<=1;dy++)if(dx||dy)nb[i][k++]=((i/L+dx+L)%L)*L+(i%L+dy+L)%L;if(u(rng)<.25){cells[i].alive=true;cells[i].e=1.5;}}
 vector<Probe>test;mt19937_64 ev(510003);for(int i=0;i<128;i++){double e=.1+3.9*u(ev),r=u(ev),d=double(ev()%9)/8;Probe p;p.s=state(e,r,can_divide(e,d));for(int a=0;a<3;a++)p.r[a]=action_utility(e,r,d,a);test.push_back(p);}
 ofstream f(out+"_metrics.csv"),life(out+"_lifetimes.csv"),birth(out+"_birth_probes.csv");f<<setprecision(17)<<"t,population,resource_mean,energy_total,births,background_deaths,energy_deaths,visits,harvest,reward,genotype_rms,mean_depth,energy_error,split_error,norm_error,mean_parent_visits\n";life<<"t,status,age_sweeps,visits,depth\n";birth<<setprecision(17)<<"t,birth_index,parent_visits,write_norm,parent_utility,aligned_utility,random_utility,actual_child_utility\n";
 ofstream learn(out+"_learning.csv"),updates(out+"_updates.csv");learn<<setprecision(17)<<"t,id,visits,utility,status\n";updates<<setprecision(17)<<"t,birth_index,allowed,write_norm,zero_signal_skip,candidate_norm,contrast_sq,common_sq,unreachable_sq\n";ofstream stable(out+"_stability.csv");stable<<setprecision(17)<<"t,birth_index,allowed,pre_norm,post_a,post_r,norm_hit,box_rows,min_scale,geometry,child_min,child_max,tv_a,tv_r\n";long intervention_births=0,intervention_visits=0;int cap_time=-1;double erased_sq=0,phenotype_error=0;ofstream iv(out+"_interventions.csv");iv<<setprecision(17)<<"t,birth_index,erased_contrast_sq,theta_g_sq,mean_error\n";long births=0,totalbirths=0,bg=0,ed=0,visits=0,pvis=0,nonzero=0,fallbacks=0;double sum_norm=0,sum_sq=0;double harvest=0,rewards=0,energyerr=0,spliterr=0,normerr=0;int extinct=-1;
 auto dead=[&](Cell&x,int t,const char*why){life<<t<<','<<why<<','<<t-x.born<<','<<x.visits<<','<<x.depth<<'\n';if(x.tracked)learn<<t<<','<<x.id<<','<<x.visits<<','<<eval(x.th,test)<<','<<why<<'\n';x.alive=false;};
 for(int t=0;t<=T;t++){
 if(t%200==0){vector<int>ids;double en=0,rs=0,depth=0;for(int i=0;i<M;i++){rs+=resource[i];assert(resource[i]>=-1e-12&&resource[i]<=1+1e-12);if(cells[i].alive){ids.push_back(i);en+=cells[i].e;depth+=cells[i].depth;assert(cells[i].e>0&&cells[i].e<=4);}}double div=0;if(ids.size()>1){for(int k=0;k<32;k++){auto&a=cells[ids[measure()%ids.size()]],&b=cells[ids[measure()%ids.size()]];for(int j=0;j<D;j++)div+=(a.g[j]-b.g[j])*(a.g[j]-b.g[j])/(32.*D);}div=sqrt(div);}if(ids.empty()&&extinct<0)extinct=t;f<<t<<','<<ids.size()<<','<<rs/M<<','<<en<<','<<births<<','<<bg<<','<<ed<<','<<visits<<','<<harvest<<','<<rewards<<','<<(ids.empty()?nan(""):div)<<','<<(ids.empty()?nan(""):depth/ids.size())<<','<<energyerr<<','<<spliterr<<','<<normerr<<','<<(births?double(pvis)/births:nan(""))<<'\n';births=bg=ed=visits=pvis=0;harvest=rewards=0;}
 if(t==T)break;for(double&r:resource)r=min(1.,r+regen);
 for(int it=0;it<M;it++){int i=rng()%M;Cell&x=cells[i];if(!x.alive)continue;if(u(rng)<mortality){bg++;dead(x,t+1,"background");continue;}int empty[8],n=0;for(int j:nb[i])if(!cells[j].alive)empty[n++]=j;int s=state(x.e,resource[i],x.e-.12>2&&n>0);auto p=prob(x.th,s);double acoin=u(rng);int a=acoin<p[0]?0:acoin<p[0]+p[1]?1:2;double before=x.e,take=a==1?min(.5,resource[i]):0;resource[i]-=take;double cost=a==0?.04:a==1?.08:.12;double uncapped=before+take-cost;double after=min(4.,uncapped);bool death=after<=0,born=!death&&a==2&&after>2&&n>0;double retained=death?0:after;double loss=max(0.,uncapped-4),debt=max(0.,-after);energyerr=max(energyerr,abs(retained-before-(take-cost-loss+debt)));double reward=retained-before+bonus*born-.5*death;double effective_eta=x.intervened?childeta:eta;x.th[s*3+a]+=effective_eta*(reward-x.th[s*3+a]);if(x.intervened)intervention_visits++;x.e=after;x.visits++;visits++;harvest+=take;rewards+=reward;if(x.tracked&&(x.visits==20||x.visits==100))learn<<t+1<<','<<x.id<<','<<x.visits<<','<<eval(x.th,test)<<",checkpoint\n";
 if(death){ed++;dead(x,t+1,"energy");continue;}
 if(born){int j=empty[rng()%n];Cell&y=cells[j];array<double,D>delta{},randdir{};double len=0,rlen=0;for(int k=0;k<D;k++){delta[k]=lam*(x.th[k]-x.g[k]);len+=delta[k]*delta[k];randdir[k]=normal(direction);rlen+=randdir[k]*randdir[k];}len=sqrt(len);rlen=sqrt(rlen);double candidate_norm=len;int release_times[8]={0,107,214,321,429,536,643,750};long released=1024;if(spaced){released=0;for(int rt:release_times)if(t>=rt)released+=128;}bool allowed=(cap<0||nonzero<cap)&&(stop_time<0||t<stop_time)&&(!fixed||nonzero<released);bool fallback=false;array<double,D> step{};
 StableAudit sa;array<double,D> pair_a{},pair_r{};
 if(fixed){if(len>1e-12){for(double &v:delta)v*=q/len;}else{delta.fill(0);allowed=false;}}
 if(rule>0){pair_a=delta;pair_r=rotate_states(delta,state_rng,ra);sa=constrain_pair(x.g,pair_a,pair_r,rule,q);step=mode==8?pair_r:pair_a;len=mode==8?sa.post_r:sa.post_a;}
 else if(mode==7||mode==8){step=delta;if(mode==8)step=rotate_states(step,state_rng,ra);}
 else if(mode>=2){fallback=(mode==2||mode==6)&&len<1e-12;
 if(fallback){step.fill(0);len=0;}
 else if(mode==2||mode==6){for(int k=0;k<D;k++)step[k]=delta[k]*q/len;len=q;if(mode==6)step=rotate_states(step,state_rng,ra);}
 else if(mode==3&&len>=1e-12){step=delta;shuffle(step.begin(),step.end(),shuffle_rng);for(double&v:step)v*=q/len*(u(shuffle_rng)<.5?-1:1);len=q;}
 else{for(int k=0;k<D;k++)step[k]=randdir[k]*q/rlen;len=q;}}

 else{for(int k=0;k<D;k++)step[k]=random?randdir[k]*len/rlen:delta[k];}
 if(fixed&&len<q-1e-10)allowed=false;
 if(!allowed){step.fill(0);len=0;fallback=false;}
 double cs=0,ms=0,us=0;for(int ss=0;ss<NS;ss++){double m=(step[3*ss]+step[3*ss+1]+step[3*ss+2])/3;ms+=3*m*m;for(int k=0;k<3;k++){cs+=(step[3*ss+k]-m)*(step[3*ss+k]-m);if(ss/(BINS*2)<BINS/2&&ss%2==1)us+=step[3*ss+k]*step[3*ss+k];}}total_contrast_sq+=cs;total_common_sq+=ms;unreachable_sq+=us;
 double actual=0;for(int k=0;k<D;k++){double v=step[k];actual+=v*v;y.g[k]=x.g[k]+v+mu*normal(noise);y.th[k]=y.g[k];if(rule==0&&mode==7&&allowed&&mu==0){double expected=(1-lam)*x.g[k]+lam*x.th[k];formula_error=max(formula_error,abs(y.g[k]-expected));assert(formula_error<1e-10);}assert(isfinite(y.g[k]));}normerr=max(normerr,abs(sqrt(actual)-len));totalbirths++;births++;pvis+=x.visits;sum_norm+=sqrt(actual);sum_sq+=actual;if(actual>0)nonzero++;if(cap>0&&nonzero==cap&&cap_time<0)cap_time=t+1;fallbacks+=fallback;updates<<t+1<<','<<totalbirths<<','<<allowed<<','<<sqrt(actual)<<','<<fallback<<','<<candidate_norm<<','<<cs<<','<<ms<<','<<us<<'\n';
 double child_min=*min_element(y.g.begin(),y.g.end()),child_max=*max_element(y.g.begin(),y.g.end());
 double tva=0,tvr=0;if(rule>0){array<double,D> ca{},cr{};for(int k=0;k<D;k++){ca[k]=x.g[k]+(allowed?pair_a[k]:0);cr[k]=x.g[k]+(allowed?pair_r[k]:0);}
 for(int ss=0;ss<NS;ss++){auto pp=prob(x.g,ss),pa=prob(ca,ss),pr=prob(cr,ss);for(int k=0;k<3;k++){tva+=abs(pa[k]-pp[k])/(2.*NS);tvr+=abs(pr[k]-pp[k])/(2.*NS);}}
 if(rule>=2){double lo=rule==2?-.62:-1,hi=rule==2?.42:1;for(int k=0;k<D;k++){assert(ca[k]>=lo-1e-10&&ca[k]<=hi+1e-10);assert(cr[k]>=lo-1e-10&&cr[k]<=hi+1e-10);}}}
 stable<<t+1<<','<<totalbirths<<','<<allowed<<','<<candidate_norm<<','<<(rule?sa.post_a:len)<<','<<(rule?sa.post_r:len)<<','<<sa.norm_hit<<','<<sa.box_rows<<','<<sa.min_scale<<','<<sa.geometry<<','<<child_min<<','<<child_max<<','<<tva<<','<<tvr<<'\n';
 if(probes&&mode<2&&totalbirths%32==0){array<double,D>al{},rr{};double rn=0;for(double&v:rr){v=normal(counter);rn+=v*v;}for(int k=0;k<D;k++){rr[k]=x.g[k]+rr[k]*len/sqrt(rn);al[k]=x.g[k]+delta[k];}birth<<t+1<<','<<totalbirths<<','<<x.visits<<','<<len<<','<<eval(x.g,test)<<','<<eval(al,test)<<','<<eval(rr,test)<<','<<eval(y.g,test)<<'\n';}
 y.intervened=intervention>0&&cap_time>=0;
 if(y.intervened){intervention_births++;double er=0,tg=0,me=0;for(int ss=0;ss<NS;ss++){double m=(y.g[3*ss]+y.g[3*ss+1]+y.g[3*ss+2])/3.;for(int k=0;k<3;k++){if(intervention==2)y.th[3*ss+k]=m;double d=y.th[3*ss+k]-y.g[3*ss+k];er+=d*d;tg+=d*d;}double mt=(y.th[3*ss]+y.th[3*ss+1]+y.th[3*ss+2])/3.;me=max(me,abs(mt-m));}erased_sq+=er;phenotype_error=max(phenotype_error,me);iv<<t+1<<','<<totalbirths<<','<<er<<','<<tg<<','<<me<<'\n';}
 y.alive=true;y.e=after*fraction;x.e=after*(1-fraction);spliterr=max(spliterr,abs(y.e+x.e-after));y.visits=0;y.born=t+1;y.depth=x.depth+1;y.id=totalbirths;y.tracked=probes&&totalbirths%32==0;if(y.tracked)learn<<t+1<<','<<y.id<<",0,"<<eval(y.th,test)<<",birth\n";
 }
 }
 }
 for(auto&x:cells)if(x.alive&&x.tracked)learn<<T<<','<<x.id<<','<<x.visits<<','<<eval(x.th,test)<<",censored\n";
 for(auto&x:cells)if(x.alive)life<<T<<",censored,"<<T-x.born<<','<<x.visits<<','<<x.depth<<'\n';
 ofstream z(out+"_audit.json");z<<setprecision(17)<<"{\"formula_error\":"<<formula_error<<",\"bins\":"<<BINS<<",\"intervention\":"<<intervention<<",\"child_eta\":"<<childeta<<",\"cap_time\":"<<cap_time<<",\"intervention_births\":"<<intervention_births<<",\"intervention_visits\":"<<intervention_visits<<",\"erased_sq\":"<<erased_sq<<",\"phenotype_mean_error\":"<<phenotype_error<<",\"energy_error\":"<<energyerr<<",\"split_error\":"<<spliterr<<",\"norm_error\":"<<normerr<<",\"births_total\":"<<totalbirths<<",\"sum_norm\":"<<sum_norm<<",\"sum_sq\":"<<sum_sq<<",\"nonzero\":"<<nonzero<<",\"fallbacks\":"<<fallbacks<<",\"contrast_sq\":"<<total_contrast_sq<<",\"common_sq\":"<<total_common_sq<<",\"unreachable_sq\":"<<unreachable_sq<<",\"row_mean_error\":"<<ra.mean_error<<",\"row_norm_error\":"<<ra.row_norm_error<<",\"row_contrast_error\":"<<ra.contrast_error<<",\"empty_support_error\":"<<ra.support_error<<",\"extinction_first_sample\":"<<extinct<<"}";
 return 0;
}
