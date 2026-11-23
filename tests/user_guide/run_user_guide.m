function report = run_user_guide(repo,out,caseId)
% Execute the v2.8 guide's Chapter 6 examples through the production Harness
% MATLAB bridge. Scientific work stays in the registered Acycle interfaces.
% Driver-only code reads/writes fixtures, connects return values, and checks them.
addpath(repo); setup_migration();
addpath(fullfile(repo,'harness','overlay','matlab'));
if ~isfolder(out), mkdir(out); end
out=char(java.io.File(out).getCanonicalPath());
set(groot,'DefaultFigureVisible','off'); rng(20261123,'twister');
steps={}; checks={}; serial=0;
report=struct('case_id',caseId,'matlab',version,'seed',20261123, ...
    'scope','Chapter 6; real Harness MATLAB bridge; no LLM in this runner', ...
    'steps',{{}},'checks',{{}},'fatal',[]);
try
    names=struct('insolation','Example-Insol-t-0-2000ka-day-80-lat-65-meandaily-La04.txt', ...
        'etp','Example-La2004-1E.5T-1P-0-2000.txt','wayao','Example-WayaoCarnianGR0.txt');
    file=fullfile(repo,'upstream','acycle','data','Examples',names.(caseId));
    report.input_file=names.(caseId);
    % Exercise the file import used by the Harness, not an in-driver substitute.
    imp=struct('path',file,'kind','matrix','field','data');
    [h,hj]=call('sort-helper','menu_sort','helper',struct('input', ...
        struct('operation','SortUnique_legacy','datasort',1,'dataunique',1,'dataempty',1),'file_input',imp));
    [sorted,~]=call('sort','menu_sort','analyzer',struct('helper_journal',hj));
    data=sorted.data; raw=data;
    check('sorted_finite_unique',all(isfinite(data),'all') && all(diff(data(:,1))>0),size(data));
    if strcmp(caseId,'wayao')
        [s,~,~]=run('sampling','menu_samplerate','SamplingRate_legacy',struct('data_filterout',data),struct(),true, ...
            struct('dat_name',caseId,'ext','.txt','unit','m','unit_type',1));
        report.sampling=struct('median',median(s.dt),'mean',mean(s.dt));
        check('guide_median_spacing',abs(median(s.dt)-0.3333)<0.0001,median(s.dt));
        check('guide_mean_spacing',abs(mean(s.dt)-0.35341)<0.0001,mean(s.dt));
        z=run('interpolate','menu_interp','interpolate_legacy',struct('data',data),struct('interpolate_rate',0.33),false);
        data=z.data_even;
        span=80/range(data(:,1));
        d=run('detrend','menu_prewhiten','Detrending_legacy',struct('data',data),struct('method','lowess','span',span),true);
    else
        d=run('demean','menu_prewhiten','Detrending_legacy',struct('data',data),struct('method','mean'),true);
    end
    series=[d.datax,d.residual];
    md=run('master-detrend','menu_prewhiten','Detrending', ...
        struct('data',data,'method',d.method,'span',80/range(data(:,1)),'degree',3),struct(),false);
    check('master_detrend_equivalence',isequaln(md,d),[]);
    check('detrend_reconstruction',max(abs(d.trend+d.residual-d.datay))<1e-9,max(abs(d.trend+d.residual-d.datay)));
    writematrix(series,fullfile(out,'prepared-series.csv'));
    if strcmp(caseId,'wayao'), fmax=1; factor=5; periods=[33.9 10 7 2.6 1.8]; else
        factor=1; fmax=.08; periods=[405 125 95 41 23.7 22.4 19];
        if strcmp(caseId,'insolation'), fmax=.06; periods=[23.7 22.4 19]; end
    end
    noise=struct('classic',false,'robust',strcmp(caseId,'wayao'),'smoothwin',.2,'linlog',2, ...
        'biascorr',false,'powerlaw',false,'bending',false,'ftest',false,'swa',false);
    opts=struct('method','Multi-taper method','nw',2,'padtimes',5, ...
        'nzeropad',factor*size(series,1),'fmax',fmax,'noise',noise);
    % padtimes=5 selects the historical explicit-nfft branch, including when
    % the manual nfft field is N. See the documented GUIDE callback ambiguity.
    [power,pj,~]=run('mtm','menu_power','PowerSpectrum_legacy',struct('data',series),opts,true, ...
        struct('fmax',fmax,'linlogY',0,'unit',unit()));
    writematrix([power.fd1,power.po],fullfile(out,'mtm.csv'));
    peakRows=peakChecks(power.fd1,power.po,periods,1/(size(series,1)*median(diff(series(:,1)))));
    report.peaks=peakRows;
    if ~strcmp(caseId,'wayao')
        % The guide's labelled frequencies (e.g. 0.0421788) lie on the 5*N
        % grid, not the N=2001 grid shown in its settings screenshot.
        % Keep this diagnostic separate: it cannot turn a failed literal
        % screenshot check into a pass.
        altOpts=opts; altOpts.nzeropad=5*size(series,1);
        alt=run('mtm-5x-diagnostic','menu_power','PowerSpectrum_legacy',struct('data',series),altOpts,true, ...
            struct('fmax',fmax,'linlogY',0,'unit',unit()));
        writematrix([alt.fd1,alt.po],fullfile(out,'mtm-5x-diagnostic.csv'));
        report.peaks_5x_diagnostic=peakChecks(alt.fd1,alt.po,periods,1/(size(series,1)*median(diff(series(:,1)))),'diagnostic_5x_');
    end
    [repeated,~]=call('mtm-replay','menu_power','replay',struct('replay_journal',pj));
    check('mtm_exact_replay',isequaln(power,repeated),[]);
    models=struct('robust',noise.robust,'classic',false,'ftest',false,'swa',false,'powerLaw',false,'bendingPowerLaw',false);
    [current,~,~]=run('master-mtm','menu_power','PowerSpectrum',struct('data',series), ...
        struct('nfft',opts.nzeropad,'nw',2,'fmin',0,'fmax',fmax,'models',models, ...
        'fitModel',2,'smoothFraction',.2,'fitMaximum',1/(2*median(diff(series(:,1))))),true, ...
        struct('logPower',false,'fmax',fmax));
    check('master_mtm_frequency_equivalence',isequaln(current.frequency,power.fd1),[]);
    check('master_mtm_power_equivalence',max(abs(current.power-power.po))/max(power.po)<1e-10,max(abs(current.power-power.po))/max(power.po));
    writematrix([current.frequency,current.power],fullfile(out,'master-mtm.csv'));
    if strcmp(caseId,'wayao')
        window=40; step=.33; evoMax=.7;
        if isfield(power,'models') && isfield(power.models,'robust')
            rb=power.models.robust.redconfML96;
            writematrix(rb,fullfile(out,'robust-ar1.csv'));
            for kk=1:numel(peakRows)
                fq=1/peakRows(kk).observed;
                threshold=interp1(rb(:,1),rb(:,5),fq);
                value=interp1(power.fd1,power.po,fq);
                check(sprintf('guide_peak_%g_above_95',periods(kk)),value>threshold, ...
                    struct('power',value,'threshold95',threshold,'ratio',value/threshold));
            end
        end
        report.wayao_primary=struct('nfft',opts.nzeropad,'fit_model',2,'source','guide prose: 5x padding, log power fit');
        % p.122 settings conflict with the prose: NFFT=534 and fit model 1.
        % p.123's annotated peak uses a 5*N grid. Retain both alternatives.
        altOpts=opts; altOpts.noise.linlog=1;
        al=run('mtm-linear-fit-diagnostic','menu_power','PowerSpectrum_legacy',struct('data',series),altOpts,true, ...
            struct('fmax',fmax,'linlogY',0,'unit','m'));
        writematrix(al.models.robust.redconfML96,fullfile(out,'linear-fit-diagnostic.csv'));
        altOpts.nzeropad=size(series,1);
        ap=run('mtm-panel-diagnostic','menu_power','PowerSpectrum_legacy',struct('data',series),altOpts,true, ...
            struct('fmax',fmax,'linlogY',0,'unit','m'));
        writematrix([ap.fd1,ap.po],fullfile(out,'mtm-panel-diagnostic.csv'));
        writematrix(ap.models.robust.redconfML96,fullfile(out,'panel-background-diagnostic.csv'));
    else
        window=400; step=3.2; evoMax=.1;
        if strcmp(caseId,'insolation'), evoMax=.06; end
    end
    evoOpts=struct('window',window,'step',step,'fmin',0,'nyquist',evoMax,'norm',1, ...
        'time_0pad',1,'padtype',1,'method','Fast Fourier transform (LAH)');
    [evo,~,~]=run('evolution','menu_period','EvolutionarySpectrum_legacy',struct('data',series),evoOpts,true, ...
        struct('fmax',evoMax,'unit',unit(),'filename',names.(caseId),'plotseries',strcmp(caseId,'insolation')));
    check('evolution_finite_power',all(isfinite(evo.s),'all') && ~isempty(evo.s),size(evo.s));
    report.evolution=struct('window',window,'step',step,'size',size(evo.s),'frequency_bounds',[min(evo.x_grid(:)) max(evo.x_grid(:))]);
    if strcmp(caseId,'etp')
        [wave,~,~]=run('wavelet','menu_waveletGUI','WaveletSpectrum_legacy',struct('data',series,'pt1',10), ...
            struct('pt2',700,'dss',.1,'pad',1,'mother','MORLET','param',6,'method_sel',3,'data_standardize',0),true, ...
            struct('unit','kyr','unit_type',2,'plot_flipy',1,'Yticks',[20 41 95 125 405]));
        check('wavelet_finite_power',all(isfinite(wave.power),'all'),size(wave.power));
        report.wavelet=struct('method_sel',3,'period_max_setting',700,'size',size(wave.power));
    elseif strcmp(caseId,'wayao')
        % Filtering and tuning are independent of the COCO Monte Carlo result.
        [band,~,~]=run('filter','menu_filter','Bandpass_legacy',struct('data',series), ...
            struct('filter','Gaussian','flow',.022,'fhigh',.034),true);
        filtered=band.data_filterout(:,1:2); writematrix(filtered,fullfile(out,'filtered.csv'));
        [age,~,~]=run('age-model','menu_agebuild','BuildAgeModel_legacy',struct('data',filtered), ...
            struct('period',405,'pkstrough',1),true);
        writematrix(age.agemodel,fullfile(out,'age-tiepoints.csv'));
        check('age_tiepoint_spacing_405',all(abs(diff(age.agemodel(:,2))-405)<1e-10),age.agemodel);
        check('age_tiepoints_monotonic',all(diff(age.agemodel(:,1))>0),size(age.agemodel));
        [tuned,~,~]=run('tuning','menu_age','AgeScale_legacy',struct('data',raw,'tiepoints',age.agemodel),struct(),true);
        writematrix(tuned.tuned,fullfile(out,'tuned.csv'));
        check('tuning_preserves_proxy',isequaln(tuned.tuned(:,2),raw(:,2)),[]);
        check('tuned_time_monotonic',all(diff(tuned.time)>0),[min(tuned.time) max(tuned.time)]);
        % Preserve a known historical edge extrapolation issue as a diagnostic,
        % rather than changing a scientific result inside the test.
        edge=age.agemodelfull([1 end],2);
        intended=interp1(age.agemodel(:,1),age.agemodel(:,2),age.agemodelfull([1 end],1),'linear','extrap');
        report.age_model_edge=struct('historical',edge,'linear_extrapolation',intended,'max_difference',max(abs(edge-intended)));
        % COCO GUI's unchanged target construction, with all arguments explicit.
        target=run('target','menu_ecoco','gentarget_legacy',struct('laskar',4,'t1',229000,'t2',231000, ...
            'f1',0,'f2',.08,'ne',1,'nt',.6,'np',.5,'pad',5000,'method',1),struct(),false);
        ageMa=230;
        %% Source: upstream/acycle/code/guicode/eCOCOGUI.m:2303-2307, b52ea9f
        orbit7=[405 125 95 41-.0332*ageMa 23.75-.0121*ageMa 22.43-.0108*ageMa 19.18-.0079*ageMa];
        %% End source-derived orbital-period selection
        common=struct('target',target.target,'orbit7',orbit7,'dt',mean(diff(series(:,1))), ...
            'pad',5000,'sr1',4.29,'sr2',43.5111,'srstep',.13074,'adjust',0,'red',1,'nsim',1000,'slices',1);
        q=common; q.dat=series; q.method='Pearson';
        [coco,cj,~]=run('coco','menu_ecoco','corrcoefslices_rank_legacy',q,struct(),false);
        [~,best]=max(coco.corrCI(:,2));
        report.coco=struct('rate',coco.corrCI(best,1),'correlation',coco.corrCI(best,2), ...
            'p',coco.corr_h0(best,1),'simulations',1000,'rate_count',size(coco.corrCI,1), ...
            'mc_exceedances',sum(coco.corry(best,:)>=coco.corrCI(best,2)), ...
            'empirical_p_add_one',(1+sum(coco.corry(best,:)>=coco.corrCI(best,2)))/1001);
        writematrix([coco.corrCI,coco.corr_h0],fullfile(out,'coco.csv'));
        repeatedCoco=call('coco-replay','menu_ecoco','replay',struct('replay_journal',cj));
        check('coco_exact_replay',isequaln(coco,repeatedCoco),[]);
        check('coco_rate_near_8_1',abs(coco.corrCI(best,1)-8.1)<.6,report.coco);
        check('coco_guide_p_at_most_0_001',coco.corr_h0(best,1)<=.001,report.coco);
        padded=run('ecoco-padding','menu_period','zeropad2_legacy',struct('data',series,'win',45,'padding',1),struct(),false);
        q=common; q.data=padded.dataX; q.window=45; q.step=1; q.delinear=0; q.nsim=500;
        [ec,~,~]=run('ecoco','menu_ecoco','ecoco_legacy',q,struct(),false);
        check('ecoco_nonempty_finite',~isempty(ec.out_ecc) && all(isfinite(ec.out_ecc),'all'),size(ec.out_ecc));
        check('ecoco_simulation_available',~isempty(ec.out_eci) && all(isfinite(ec.out_eci),'all'),size(ec.out_eci));
        report.ecoco=struct('simulations',500,'window',45,'step_in_samples',1,'size',size(ec.out_ecc));
        writematrix(ec.sr_p,fullfile(out,'ecoco-rates.csv'));
        pp=struct('params',struct(),'plt',struct('operation','ecocoplot_legacy','plotn',1),'dat',struct(),'res',ec,'target_kind','none');
        plotCall('ecoco-plot','menu_ecoco',pp);
    end
catch err
    report.fatal=struct('identifier',err.identifier,'message',err.message,'stack',{err.stack});
end
report.steps=steps; report.checks=checks;
report.execution_ok=isempty(report.fatal) && all(cellfun(@(x)strcmp(x.status,'ok') && strcmp(x.completion,'done'),steps));
report.criteria_ok=all(cellfun(@(x)x.passed,checks));
writejson(fullfile(out,'report.json'),report);
fprintf('GUIDE %s: execution=%d criteria=%d steps=%d checks=%d\n',caseId,report.execution_ok,report.criteria_ok,numel(steps),numel(checks));
if ~isempty(report.fatal), fprintf('%s: %s\n',report.fatal.identifier,report.fatal.message); end

    function [r,j,h]=run(label,menu,op,input,options,draw,style)
        if nargin<7, style=struct(); end
        input.operation=op;
        [h,hj]=call([label,'-helper'],menu,'helper',struct('input',input,'override',struct('params',options,'plt',style)));
        [r,j]=call(label,menu,'analyzer',struct('helper_journal',hj));
        if draw
            payload=struct('helper_journal',hj,'analyzer_journal',j,'target_kind','none');
            if strcmp(label,'wavelet'), h.dat.pt1=10; payload.dat=h.dat; end
            plotCall([label,'-plot'],menu,payload);
        end
    end
    function plotCall(label,menu,p)
        try, call(label,menu,'plotter',p); catch
            % A renderer failure must not prevent downstream scientific checks.
        end
    end
    function [v,j]=call(label,menu,role,p)
        serial=serial+1; folder=fullfile(out,sprintf('%02d-%s',serial,label)); mkdir(folder);
        request=struct('operation','menu','acycle_root',repo,'menu',menu,'role',role,'payload',p,'output_dir',folder);
        requestFile=fullfile(folder,'request.json'); responseFile=fullfile(folder,'response.json'); writejson(requestFile,request);
        started=tic; acycle_harness_menu(requestFile,responseFile); reply=jsondecode(fileread(responseFile));
        record=struct('label',label,'menu',menu,'role',role,'status',reply.status,'completion',reply.completion,'seconds',toc(started),'folder',folder);
        if isfield(reply,'error'), record.error=reply.error; end
        steps{end+1}=record;
        if ~strcmp(reply.status,'ok'), error(reply.error.identifier,'%s',reply.error.message); end
        if strcmp(role,'plotter'), check([label,'_figure_created'],~isempty(reply.files),reply.files); end
        j=fullfile(folder,reply.journal); lines=splitlines(strtrim(fileread(j))); fin=jsondecode(lines{end});
        v=aclog.read(j,fin.info.retval);
    end
    function check(name,passed,detail)
        checks{end+1}=struct('name',name,'passed',logical(passed),'detail',{detail});
    end
    function p=peakChecks(f,power,expected,tol,prefix)
        if nargin<5, prefix=''; end
        ispeak=false(size(power)); ispeak(2:end-1)=power(2:end-1)>power(1:end-2) & power(2:end-1)>=power(3:end);
        ix=find(ispeak); p=struct('expected',{},'observed',{},'frequency_error',{},'tolerance',{},'rayleigh_pass',{},'rounding_pass',{},'passed',{});
        for kk=1:numel(expected)
            [delta,jj]=min(abs(f(ix)-1/expected(kk))); found=ix(jj);
            digits=0;
            if ismember(expected(kk),[33.9 2.6 1.8 23.7 22.4 19]), digits=1; end
            rounded=round(1/f(found),digits)==expected(kk);
            p(kk)=struct('expected',expected(kk),'observed',1/f(found),'frequency_error',delta,'tolerance',tol, ...
                'rayleigh_pass',delta<=tol,'rounding_pass',rounded,'passed',delta<=tol || rounded);
            check([prefix,sprintf('guide_peak_%g',expected(kk))],p(kk).passed,p(kk));
        end
    end
    function u=unit()
        if strcmp(caseId,'wayao'), u='m'; else, u='kyr'; end
    end
end
function writejson(file,value)
fid=fopen(file,'w'); guard=onCleanup(@()fclose(fid)); %#ok<NASGU>
fprintf(fid,'%s\n',jsonencode(value));
end
