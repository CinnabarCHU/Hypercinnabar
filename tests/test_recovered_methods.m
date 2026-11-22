function test_recovered_methods()
root=fileparts(fileparts(mfilename('fullpath'))); addpath(root); setup_migration;
old=getenv('ACYCLE_LOG_DIR'); journal=tempname; mkdir(journal); setenv('ACYCLE_LOG_DIR',journal);
guard=onCleanup(@() restore(old,journal));
t=(0:255)'; d=[t,sin(2*pi*t/24).*(1+.3*cos(2*pi*t/100))+.1*cos(t/3)];
p=acmethods.Lyapunov.helper(struct('data',d)); p.step_size=16; p.tau=1;
z=acmethods.Lyapunov.analyzer(p);
assert(isequaln(z.output,lyapunov_timeseries(interpolate(z.data,p.interpolate_rate),p.tau,p.window,p.step_size,0,0)));
assert(size(z.output,2)==2 && ~isempty(z.output));
if exist('OCTAVE_VERSION','builtin'), return; end
before=findall(groot,'Type','figure'); graphicsGuard=onCleanup(@() close(setdiff(findall(groot,'Type','figure'),before)));
p=acmethods.TimeOpt.helper(struct('dat',d)); p.numsed=5; p.sedmin=.3; p.sedmax=1.2; p.cormethod=1;
assignin('base','tanerfilterenv',42);
z=acmethods.TimeOpt.analyzer(p);
assert(isequal(evalin('base','tanerfilterenv'),42));
[xx,datopt,xcl,sr_p]=timeOptAc(d,p.sedmin,p.sedmax,p.numsed,0,p.linLog,p.fit,p.fl,p.fh,p.roll,p.targetE,p.targetP,p.detrend,p.cormethod,0);
assert(isequaln(z.xx,xx) && isequaln(z.datopt,datopt) && isequaln(z.xcl,xcl) && isequaln(z.sr_p,sr_p));
p.nsim=3; rng(71); state=rng; [z,record]=acmethods.TimeOpt.analyzer(p);
assert(isequaln(z,aclog.replay(record)) && isequal(size(z.xcl),[1,4]));
rng(state); s=polyfit(d(:,1),d(:,2),1); detrended=d; detrended(:,2)=d(:,2)-(t*s(1)+s(2));
sims=timeOptSimAc(detrended,z.xcl(1),p.nsim,p.fit,p.cormethod,p.targetE,p.targetP,(p.fl+p.fh)/2,p.fl,p.fh,p.roll);
assert(isequaln(sims,z.xsim) && all(isfinite(sims(:))));
p.mc_scope='all'; z=acmethods.TimeOpt.analyzer(p);
assert(isequal(z.xcl(:,1),xx(:,1)) && all(z.xcl(:,2:4)>0,'all'));
q=acmethods.EvolutionaryTimeOpt.helper(struct('dat',d)); q.time_0pad=0; q.window=100; q.step=65;
q.numsed=p.numsed; q.sedmin=p.sedmin; q.sedmax=p.sedmax; q.cormethod=p.cormethod;
r=acmethods.EvolutionaryTimeOpt.analyzer(q);
[x,~,~,rates]=timeOptAc(d(1:100,:),q.sedmin,q.sedmax,q.numsed,0,q.linLog,q.fit,q.fl,q.fh,q.roll,q.targetE,q.targetP,q.detrend,q.cormethod,0);
assert(isequaln(r.senv(1,:),x(:,2)') && isequaln(r.sr_p(1,:),rates));
q.result=r; acmethods.EvolutionaryTimeOpt.plotter(q);
p.nsim=0; p.result=acmethods.TimeOpt.analyzer(p); acmethods.TimeOpt.plotter(p);
q=acmethods.LinearRegression.helper(struct('selectedData',d)); r=acmethods.LinearRegression.analyzer(q);
mdl=fitlm(d(:,1),d(:,2)); limits=coefCI(mdl); assert(abs(r.slope-mdl.Coefficients.Estimate(2))<1e-12);
assert(max(abs(r.slopeCI-limits(2,:)))<1e-12 && numel(r.Xnew)==100 && ~isempty(r.anovaText));
acmethods.LinearRegression.plotter(struct('result',r));
evalin('base','clear tanerfilterenv');
fprintf('Historical TimeOpt, eTimeOpt, Lyapunov and archival regression comparisons passed.\n');
end

function restore(old,journal)
setenv('ACYCLE_LOG_DIR',old); rmdir(journal,'s');
end
