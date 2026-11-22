function [retval,id] = analyzer(params,id)
% StratigraphicCorrelation.analyzer parameters: rawser tiepoints1 tiepoints2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/CorrelationGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('StratigraphicCorrelation-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
rawser=p.rawser; app.tiepoints1=p.tiepoints1; app.tiepoints2=p.tiepoints2;
if size(app.tiepoints1,1)<2 || size(app.tiepoints1,1)~=size(app.tiepoints2,1), error('Acycle:Correlation:Ties','Supply at least two paired tie points.'); end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/CorrelationGUI.m:L631-L637
                agemodel = [app.tiepoints2(:,1),app.tiepoints1(:,1),app.tiepoints2(:,3)];
                agemodel = sortrows(agemodel);
                data1 = rawser;
                [time1,~] = depthtotime(data1(:,1),agemodel);
                data1t = [time1,data1(:,2)];
                tiepoints2sort = sortrows(app.tiepoints2);
                [tie2t,~] = depthtotime(tiepoints2sort(:,1),agemodel);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/CorrelationGUI.m:L662-L673
            idi = size(app.tiepoints2,1)+1;
            sedrate = zeros(idi+1,2);
            sedrate(1,1) = rawser(1,1);
            sedrate(2:end-1,1) = tiepoints2sort(:,1);
            sedrate(end,1) = rawser(end,1);
            sedrate0 = diff(agemodel(:,1))./diff(agemodel(:,2));
            if ~isempty(sedrate0)
                sedrate(2:end-2,2) = sedrate0;
                sedrate(1,2) = sedrate(2,2);
                sedrate(end-1,2) = sedrate(end-2,2);
                sedrate(end,2) = sedrate(end-2,2);
            end
%% End copied source
r = struct();
r.agemodel = agemodel;
r.data1t = data1t;
r.tie2t = tie2t;
r.sedrate = sedrate;
end
