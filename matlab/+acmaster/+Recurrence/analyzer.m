function [retval,id] = analyzer(params,id)
% Recurrence.analyzer parameters: data method_use normFlag threshold showdet w ws theiler_window lmin embed_m embed_tau.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/RecPlotGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Recurrence-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
app = p; data_s=p.data; threshold=p.threshold;
if ~isscalar(threshold) || ~isfinite(threshold) || isempty(p.normFlag) || isempty(p.method_use), error('Acycle:Recurrence:Option','Supply a finite threshold, metric and normalization.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L389-L389
            [N, ncol] = size(data_s);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L392-L398
            if ncol == 1
                x = data_s;
                t = (1:N)';
            else
                x = data_s(:,2);
                t = data_s(:,1);
            end
%% End copied source
[~,S,~]=localBuildSAndThreshold([],x,app.normFlag);
app.localOffdiagDistvec=@(d) localOffdiagDistvec([],d);
app.localEpsFromRrForPlot=@(d,rr) localEpsFromRrForPlot(app,d,rr);
[eps_plot,rr_plot,threshold_used]=localThresholdToEpsForPlot(app,threshold,app.method_use,S);
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L400-L407
            if strcmpi(app.normFlag, 'norm')
                x0 = x(:);
                mu = mean(x0, 'omitnan');
                sig = std(x0, 'omitnan');
                if sig > 0
                    x = (x - mu) ./ sig;
                end
            end
%% End copied source
DETx=[]; DETy=[];
if p.showdet
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L447-L453
                if ncol == 1
                    winN = N;
                    wsN = 1;
                else
                    winN = max(data_s(:,1)) - min(data_s(:,1));
                    wsN = median(diff(data_s(:,1)));
                end
%% End copied source
    w=p.w; ws=p.ws; theiler_window=p.theiler_window; lmin=p.lmin;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L460-L469
                if w > winN
                    w = winN;
                    app.EditWindowSize.Value = num2str(w);
                elseif w <= 0
                    w = winN;
                    app.EditWindowSize.Value = num2str(w);
                end
                if ncol > 1
                    w = round(N * w / winN);
                end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L476-L485
                if ws > w
                    ws = w;
                    app.EditSlidingStep.Value = num2str(ws);
                elseif ws < wsN
                    ws = wsN;
                    app.EditSlidingStep.Value = num2str(ws);
                end
                if ncol > 1
                    ws = round(N * ws / winN);
                end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L504-L505
                [DETy, testi] = crp_pdist(x, w, ws, theiler_window, lmin, 0, threshold, app.method_use, app.normFlag, app.embed_m, app.embed_tau);
                DETx = round(t(testi) + 1/2 * winN * w / N);
%% End copied source
end
r=struct('S',S,'recurrence',S<eps_plot,'t',t,'eps_plot',eps_plot,'rr_plot',rr_plot, ...
    'threshold_used',threshold_used,'DETx',DETx,'DETy',DETy);
end

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L648-L676
        function [x_use, S, threshold] = localBuildSAndThreshold(~, x, normFlag)
            x_use = double(x(:));
            if nargin < 3 || isempty(normFlag), normFlag = 'nonorm'; end
            nf = lower(strtrim(string(normFlag)));
            if nf == "narow", nf = "nonorm"; end
            if nf == "normalize" || nf == "zscore", nf = "norm"; end
            if nf == "norm"
                mu = mean(x_use,'omitnan');
                sig = std(x_use,'omitnan');
                if isfinite(sig) && sig > 0
                    x_use = (x_use - mu) ./ sig;
                end
            end
            N = numel(x_use);
            S = zeros(N,N);
            for i = 1:N
                S(:,i) = abs(x_use(i) - x_use);
            end
            d = S(:);
            d = d(isfinite(d));
            if isempty(d)
                threshold = 0.1;
            else
                threshold = median(d) - 0.5 * std(d);
            end
            dmin = min(d); dmax = max(d);
            if ~isfinite(threshold), threshold = 0.1; end
            threshold = max(dmin, min(dmax, threshold));
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L678-L715
        function [eps_plot, rr_plot, thr_used] = localThresholdToEpsForPlot(app, threshold, method_use, S)
            thr_used = threshold;
            if nargin < 3 || isempty(method_use), method_use = 'rr'; end
            if nargin < 2 || isempty(threshold) || ~isfinite(threshold)
                threshold = 0.10; thr_used = threshold;
            end
            method_use = lower(string(method_use));
            rr_methods = ["rr","fa","in"];
            d = app.localOffdiagDistvec(S);
            if isempty(d)
                eps_plot = 0; rr_plot = NaN; return
            end
            dmin = min(d); dmax = max(d);

            if any(method_use == rr_methods)
                if threshold <= 0
                    rr = 0.10; thr_used = rr;
                elseif threshold <= 1
                    rr = threshold;
                elseif threshold <= 100
                    rr = threshold/100;
                else
                    rr = 1.0; thr_used = 100;
                end
                rr = max(0,min(1,rr));
                rr_plot = rr;
                eps_plot = app.localEpsFromRrForPlot(S, rr_plot);
                eps_plot = max(dmin, min(dmax, eps_plot));
            else
                rr_plot = NaN;
                eps_plot = double(threshold);
                if eps_plot > dmax
                    eps_plot = dmax; thr_used = eps_plot;
                elseif eps_plot < dmin
                    eps_plot = dmin; thr_used = eps_plot;
                end
            end
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L717-L723
        function d = localOffdiagDistvec(~, D)
            n = size(D,1);
            mask = triu(true(n), 1);
            d = D(mask);
            d = d(isfinite(d));
            d = double(d(:));
        end
%% End copied source

%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/RecPlotGUI.m:L725-L735
        function epsk = localEpsFromRrForPlot(app, D, rr)
            d = app.localOffdiagDistvec(D);
            if isempty(d)
                epsk = 0;
                return
            end
            rr = max(0,min(1,rr));
            d = sort(d);
            K = max(1, min(numel(d), round(rr * numel(d))));
            epsk = d(K);
        end
%% End copied source
