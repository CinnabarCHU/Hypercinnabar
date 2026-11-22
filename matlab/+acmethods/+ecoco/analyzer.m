function [retval, id] = analyzer(params, id)
% ecoco.analyzer parameters: data target orbit7 window dt step delinear red pad sr1 sr2 srstep nsim adjust slices.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ecoco.m#L58
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/corrcoef/ecoco.m#L190
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ecoco-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
target = p.target;
orbit7 = p.orbit7;
window = p.window;
dt = p.dt;
step = p.step;
delinear = p.delinear;
red = p.red;
pad = p.pad;
sr1 = p.sr1;
sr2 = p.sr2;
srstep = p.srstep;
nsim = p.nsim;
adjust = p.adjust;
slices = p.slices;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L58-L63
nrow = length(data(:,1));       % number of the row of data
time = data(:,1);               % depth or data
datay = data(:,2);              % value of data
npts = fix(window/dt);            % number of time series within 1 window
            
if step >= nrow/2
%% End copied source
error('Acycle:eCOCO:Step','Sliding step is too large.');
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L65-L96
end

m=fix((nrow-npts)/step)+1;     % number of FFT calculations, n_row of FFT matrix results
x=[];
timex=[];

%% prepare data based on running window and steps
disp('>> Step 1: prepare data');
for m1=1:step:(step*m-1)
    m2=npts+m1-1;
    m3 = (m1-1)/step+1;               % number of FFT calculations related with step
    if m2 > nrow                      % break in case of reach moving window boundary
        break
    end
    x(:,m3) = datay(m1:m2,1);
    timex(:,m3) = time(m1:m2,1);
end
    if delinear == 1
        x = detrend(x,0);                   % remove mean trend of x
    end
%% Prepare varables
sr_range = sr1:srstep:sr2;
nofsr = length(sr_range); % number of sedimentation rates to be tested
out_ecc = zeros(nofsr,m3);
out_ep = zeros(nofsr,m3);
out_eci = zeros(nofsr,m3);
out_ecoco = zeros(nofsr,m3);
out_ecocorb = zeros(nofsr,m3);
out_norbit = zeros(nofsr,m3);

%% Simulation for the first sliding window
i = 1;
%% End copied source
q=struct('dat',[timex(:,i),x(:,i)],'target',target,'orbit7',orbit7,'dt',dt,'pad',pad, ...
    'sr1',sr1,'sr2',sr2,'srstep',srstep,'adjust',adjust,'red',red,'nsim',nsim,'slices',slices);
simulation=acmethods.corrcoefslices.analyzer(q); corry=simulation.corry;
q.nsim=0; q.method='Pearson';
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L100-L101
corrCI =[];
sr_p = zeros(m3,6);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L119-L120
orbitn = length(orbit7);
 for i = 1:m3
%% End copied source
    q.dat=[timex(:,i),x(:,i)]; slice=acmethods.corrcoefslices_rank.analyzer(q); corrCI=slice.corrCI;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L124-L141
     norbit1 = orbitn - corrCI(:,end);
     out_norbit(:,i) = norbit1;
     for j = 1 : nofsr
         %percent_value = findperct(corrCI(j,2),corry(j,:));
         %if percent_value == 0
         %    percent_value = 1/(nsim+1);
         %end
         %out_ecoco(j,i) = (- log10(out_eci(j,i))) * out_ecc(j,i);
         %out_ecocorb(j,i) = out_norbit(j,i) / orbitn * out_ecoco(j,i);
         % M. Li; Oct. 2023
         prctile_value = (100-invprctile(corry(j,:), corrCI(j,2)))/100; 
         if prctile_value == 0
            prctile_value = 1/(nsim+1);
         end
         out_eci(j,i) = prctile_value;
         out_ecoco(j,i) = (- log10(prctile_value)) * out_ecc(j,i);
         out_ecocorb(j,i) = out_norbit(j,i) / orbitn * out_ecoco(j,i);
     end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L153-L189
     if nsim > 1
         prt_sr = corrCI(:,1);
         prt_ecc = corrCI(:,2);
         prt_eci = out_eci(:,i);
         prints_ecocorb = max(out_ecocorb(:,i)); % max ecc value
         prints_sr = prt_sr(out_ecocorb(:,i) == prints_ecocorb);
         prints_eci = prt_eci(out_ecocorb(:,i) == prints_ecocorb);
         prints_ecc = prt_ecc(out_ecocorb(:,i) == prints_ecocorb);
         prints_ecoco = prt_ecc(out_ecocorb(:,i) == prints_ecocorb);
         prints_norbit = out_norbit(out_ecocorb(:,i) == prints_ecocorb);
         
         if length(prints_sr) > 1
             disp('Warning: multiple sedimentary rate options are :')
             disp(prints_sr)
         end
         
         loci = ((i-1) * dt * step + data(1,1) + window/2);

         disp(['-----> Location : ',num2str(loci),' m. Iteration : ',num2str(m3),' -> ',num2str(i)])
         try
             disp(['>>  Sedimentation rate = [ ',num2str(prints_sr(1)),...
                 ' ] cm/kyr. # of orbital cycles invloved : ',...
                 num2str(prints_norbit(1)),' of ',num2str(length(orbit7))]);
         catch
             disp('>>  Error: no solution. May not adjust the periodogram of astronomical solutions to the data periodogram')
             break
         end
             disp(['    Correlation coeffcient ',num2str(prints_ecc(1)),...
                 '. H0 significance level ',num2str(prints_eci(1))]);
             disp(['    COCOxH0-SL value ',num2str(prints_ecoco(1)), ' COCOxH0-SLxOrbits ',num2str(prints_ecocorb(1)) ])
             sr_p(i,1) = loci;
             sr_p(i,2) = prints_sr(1);
             sr_p(i,3) = prints_ecc(1);
             sr_p(i,4) = prints_eci(1);
             sr_p(i,5) = prints_norbit(1);
             sr_p(i,6) = prints_ecocorb(1);
     else
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L190-L190
         out_ecocorb(:,i) = out_norbit.*out_ecc(:,i);
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L191-L192
     end
 end
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/corrcoef/ecoco.m:L197-L197
    out_depth = (linspace(data(1,1)+window/2,data(nrow,1)-window/2,m3))';
%% End copied source
prt_sr=corrCI(:,1);
r = struct();
r.prt_sr = prt_sr;
r.out_depth = out_depth;
r.out_ecc = out_ecc;
r.out_ep = out_ep;
r.out_eci = out_eci;
r.out_ecoco = out_ecoco;
r.out_ecocorb = out_ecocorb;
r.out_norbit = out_norbit;
r.sr_p = sr_p;
end
