function [retval, id] = analyzer(params, id)
% StratigraphicCorrelation.analyzer parameters: tiepoints1 tiepoints2 data1.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/CorrelationGUI.m#L421
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('StratigraphicCorrelation-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
tiepoints1 = p.tiepoints1;
tiepoints2 = p.tiepoints2;
data1 = p.data1;
idi=size(tiepoints2,1);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/CorrelationGUI.m:L421-L439
            agemodel = [tiepoints2(:,1),tiepoints1(:,1),tiepoints2(:,3)]; % [series reference]
            agemodel = sortrows(agemodel);
            [time1,~] = depthtotime(data1(:,1),agemodel);
            % tuning series
            data1t(:,1) = time1;
            data1t(:,2) = data1(:,2);
            % sr
            tiepoints2sort = sortrows(tiepoints2);
            sedrate = zeros(idi+2,2);
            sedrate(1,1) = data1(1,1);
            sedrate(2:end-1,1) = tiepoints2sort(:,1);
            sedrate(end,1) = data1(end,1);
            sedrate0 = diff(agemodel(:,1))./diff(agemodel(:,2));
            sedrate(2:end-2,2) = sedrate0;
            sedrate(1,2) = sedrate(2,2);
            sedrate(end-1,2) = sedrate(end-2,2);
            sedrate(end,2) = sedrate(end-2,2);
            
            [tie2t,~] = depthtotime(tiepoints2sort(:,1),agemodel);
%% End copied source
r = struct();
r.agemodel = agemodel;
r.data1t = data1t;
r.sedrate = sedrate;
r.tie2t = tie2t;
end
