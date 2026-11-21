function compare_pda_bands(inputName)
    addpath(fullfile('historic','code','seriesanalysis'));
    name=string(inputName);
    switch name
        case {"d13c","d18o"}
            a=readmatrix(fullfile('inputs',name+"_baseline_series.csv"));
            data=a(:,1:2);
        case "La2010c"
            a=load(fullfile('upstream','data','La10c.mat'),'data');
            a=a.data(a.data(:,1)>=40000 & a.data(:,1)<=65000,1:2);
            data=[a(:,1),detrend(a(:,2))];
        case "ZB18a"
            fid=fopen(fullfile('upstream','data','ZB18a.dat'));
            a=textscan(fid,'%f%f%f','CommentStyle','%','CollectOutput',true);
            fclose(fid); a=a{1};
            a=a(a(:,1)>=40000 & a(:,1)<=65000,1:2);
            data=[a(:,1),detrend(a(:,2))];
    end
    mkdir('comparison');
    padded=zeropad2(data,800,1);
    fprintf('DRIVER %s %s start=%.8f end=%.8f n=%d\n',name,which('pdan'), ...
        data(1,1),data(end,1),size(data,1));
    for band={[27,55],[80,140]}
        periods=band{1};
        pd=pdan(padded,[1/periods(2),1/periods(1)],800,2,0,0.08,1,5000);
        key=name+"_"+string(periods(1))+"-"+string(periods(2));
        writematrix(pd,fullfile('comparison',key+"_pda.csv"));
        for age=[47500,50000,51600,54000]
            [~,k]=min(abs(pd(:,1)-age));
            fprintf('PDA_BAND %s at=%.6f fraction=%.10g bandSum=%.10g totalSum=%.10g count=%d\n', ...
                key,pd(k,:),size(pd,1));
        end
    end
    % Selected original window PSDs for independent checks of band settings.
    n=fix(800/(padded(2,1)-padded(1,1)));
    rows=unique(round(linspace(1,size(data,1)-3,15)));
    audit=zeros(numel(rows),2503);
    for k=1:numel(rows)
        ix=rows(k);
        spec=pmtm(detrend(padded(ix:ix+n-1,2)'),2,5000);
        audit(k,:)=[ix,median(diff(data(:,1))),spec(:)'];
    end
    writematrix(audit,fullfile('comparison',name+"_window_bins.csv"));
end
