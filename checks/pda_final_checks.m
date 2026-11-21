function pda_final_checks()
    addpath(fullfile('upstream','code','package','wavelet'));
    out=table();
    for name=["d13c","d18o","ZB18a","La2010c"]
        for label=["27-55","80-140"]
            pd=readmatrix(fullfile('inputs',name+"_"+label+"_pda.csv"));
            t=pd(:,1); recent=t>=44000 & t<=50000; older=t>=54000 & t<=60000;
            for c=2:3
                field=["fraction","target_power"];
                [w,p,s,coi]=wavelet(pd(:,c)',median(diff(t)),1,1/16,650,36,'Morlet',6);
                short=p>=1200 & p<=1600; long=p>=2000 & p<=2600;
                ok=coi(:)>=max(p(short|long));
                density=abs(w).^2./s(:);
                old=mean(density(short,older&ok),'all')/mean(density(long,older&ok),'all');
                young=mean(density(short,recent&ok),'all')/mean(density(long,recent&ok),'all');
                one=table(name,label,field(c-1),old,young,old/young, ...
                    'VariableNames',{'series','target_band_kyr','quantity','Q_54_60Ma','Q_44_50Ma','Q_old_over_young'});
                if isempty(out),out=one;else,out=[out;one];end
                fprintf('HISTQ %s %s %s Q_old=%.7f Q_young=%.7f contrast=%.7f\n', ...
                    name,label,field(c-1),old,young,old/young);
            end
        end
    end
    writetable(out,'historical-modulation.csv');
end
