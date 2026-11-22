function solution_targets()
% Compare fixed secular frequencies read from two orbital integrations.
% Ages in the public input tables are kyr. Frequencies below are cycles/Myr.
    addpath(fullfile('upstream','code','seriesanalysis'));
    mkdir('target-output');
    windows = [54,62;41,49;55,61;41,47;54,60;42,48];
    solutions = ["ZB18a","La2010c"];
    target = zeros(size(windows,1),2);
    for s = 1:2
        orbit = readmatrix(fullfile('inputs',solutions(s)+"_orbit_series.csv"));
        for w = 1:size(windows,1)
            target(w,s) = h_separation(orbit,windows(w,:));
        end
    end
    edges = [7.10,9.00,9.25,11.40;7.25,8.75,9.45,11.15;6.90,9.10,9.15,11.65];
    ages = (40.01:.02:64.99)';
    scores = table(); folds = table();
    for series = ["d18o","d13c","ZB18a","La2010c"]
        if any(series == solutions)
            file = series+"_orbit_series.csv";
        else
            file = series+"_baseline_series.csv";
        end
        data = readmatrix(fullfile('inputs',file));
        for b = 1:size(edges,1)
            envelopes = zeros(size(data,1),2);
            for j = 1:2
                pair = edges(b,2*j-1:2*j)/1000;
                z = tanerhilbertML([data(:,1),data(:,2)-mean(data(:,2))],mean(pair),pair(1),pair(2),1e20);
                envelopes(:,j) = z(:,3);
            end
            for power = 1:2
                y = bin_envelopes(data(:,1),envelopes.^power);
                for w = 1:size(windows,1)
                    bounds = windows(w,:); sel = ages >= bounds(1) & ages < bounds(2);
                    u = ages(sel)-mean(bounds); v = y(sel,:);
                    weights = sqrt(hann(numel(u)));
                    trend = [ones(size(u)),u];
                    qtrend = orth(weights.*trend);
                    residual = weights.*v - qtrend*(qtrend'*(weights.*v));
                    for s = 1:2
                        freq = target(w,s); basis = [cos(2*pi*freq*u),sin(2*pi*freq*u)];
                        weighted = weights.*basis;
                        qsin = orth(weighted-qtrend*(qtrend'*weighted));
                        r2 = sum((qsin'*residual).^2,1)./sum(residual.^2,1);
                        row = table(series,b,power,bounds(1),bounds(2),solutions(s),freq,r2(1),r2(2),sqrt(prod(r2)),...
                            'VariableNames',{'series','bands','power','from_Ma','to_Ma','target_solution','h_frequency','slow_partial_R2','fast_partial_R2','joint'});
                        scores = append_row(scores,row);
                        if b==1 && power==2 && w<=2
                            designs = [trend,basis];
                            for left = bounds(1):bounds(2)-1
                                test = ages(sel)>=left & ages(sel)<left+1;
                                train = ages(sel)<left-1 | ages(sel)>=left+2;
                                background = trend(train,:)\v(train,:);
                                full = designs(train,:)\v(train,:);
                                scale = sqrt(mean((v(train,:)-trend(train,:)*background).^2,1));
                                eb = ((v(test,:)-trend(test,:)*background)./scale).^2;
                                ef = ((v(test,:)-designs(test,:)*full)./scale).^2;
                                row = table(series,bounds(1),bounds(2),solutions(s),left,sum(eb,'all'),sum(ef,'all'),...
                                    'VariableNames',{'series','from_Ma','to_Ma','target_solution','heldout_from_Ma','sse_background','sse_fixed_frequency'});
                                folds = append_row(folds,row);
                            end
                        end
                    end
                end
            end
        end
    end
    writetable(scores,fullfile('target-output','fixed_frequency_profiles.csv'));
    writetable(folds,fullfile('target-output','fixed_frequency_predictions.csv'));
    group = groupsummary(folds,{'series','from_Ma','to_Ma','target_solution'},'sum',{'sse_background','sse_fixed_frequency'});
    group.predictive_skill = 1-group.sum_sse_fixed_frequency./group.sum_sse_background;
    writetable(group,fullfile('target-output','fixed_frequency_skill.csv'));
    disp(group(:,[1,2,4,end]));
end

function f = h_separation(orbit,bounds)
    age = orbit(:,1)/1000;
    sel = age>=bounds(1) & age<bounds(2);
    [p,freq] = periodogram(detrend(orbit(sel,3)),hann(sum(sel)),65536,1/median(diff(age)));
    keep = freq>=1000/78 & freq<=1000/68;
    [~,lines] = findpeaks(p(keep),freq(keep),'SortStr','descend','MinPeakDistance',2/diff(bounds));
    assert(numel(lines)>=2);
    f = abs(diff(lines(1:2)));
end

function result = bin_envelopes(t,y)
    sel = t>=40000 & t<65000;
    idx = floor((t(sel)-40000)/20)+1;
    result = [accumarray(idx,y(sel,1),[1250,1],@mean,NaN),accumarray(idx,y(sel,2),[1250,1],@mean,NaN)];
    assert(all(isfinite(result),'all'));
end

function out = append_row(out,row)
    if isempty(out)
        out = row;
    else
        out = [out;row];
    end
end
