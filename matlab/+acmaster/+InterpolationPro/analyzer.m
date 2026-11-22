function [retval,id] = analyzer(params,id)
% InterpolationPro.analyzer parameters: data dt method gap2zero gapdt.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/update_interpolationGUI.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('InterpolationPro-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
data = p.data;
dt = p.dt;
method = p.method;
gap2zero = p.gap2zero;
gapdt = p.gapdt;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_interpolationGUI.m:L16-L16
xq = data(1,1):dt:data(end,1);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_interpolationGUI.m:L78-L114
    if method == 1    
        vq = interp1(data(:,1),data(:,2),xq);
        titlei = '(Default) Linear Interpolation';
        legendi = 'linear';
    elseif method == 2
        vq = interp1(data(:,1),data(:,2),xq, 'nearest');
        titlei = 'Nearest Neighbor Interpolation';
        legendi = 'nearest';
    elseif method == 3
        vq = interp1(data(:,1),data(:,2),xq, 'next');
        titlei = 'Next Neighbor Interpolation';
        legendi = 'next';
    elseif method == 4
        vq = interp1(data(:,1),data(:,2),xq, 'previous');
        titlei = 'Previous Neighbor Interpolation';
        legendi = 'previous';
    elseif method == 5
        vq = interp1(data(:,1),data(:,2),xq, 'pchip');
        titlei = 'Shape-preserving Piecewise Cubic Interpolation';
        legendi = 'pchip';
    elseif method == 6
        vq = interp1(data(:,1),data(:,2),xq, 'cubic');
        titlei = 'Cubic Interpolation';
        legendi = 'cubic';
    elseif method == 7
        vq = interp1(data(:,1),data(:,2),xq, 'v5cubic');
        titlei = 'V5cubic Interpolation';
        legendi = 'v5cubic';
    elseif method == 8
        vq = interp1(data(:,1),data(:,2),xq, 'makima');
        titlei = 'Modified Akima Cubic Hermite Interpolation';
        legendi = 'makima';
    elseif method == 9
        vq = interp1(data(:,1),data(:,2),xq,'spline');
        titlei = 'Spline Interpolation';
        legendi = 'spline';
    end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_interpolationGUI.m:L117-L129
if gap2zero == 1
    dfdt = diff(data(:,1));
    gapi = 0;
    gappair = [];
    for dti = 1 : length(dfdt)
        if dfdt(dti) > dt * gapdt
            gapi = gapi + 1;
            gappair(gapi,1) = data(dti,1);
            gappair(gapi,2) = data(dti+1,1);
            vq(and(xq> gappair(gapi,1), xq < gappair(gapi,2))) = 0;
        end
    end
end
%% End copied source
r = struct();
r.xq = xq;
r.vq = vq;
r.titlei = titlei;
r.legendi = legendi;
end
