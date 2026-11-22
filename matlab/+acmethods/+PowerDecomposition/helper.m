function [retval, id] = helper(params, id)
% PowerDecomposition.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L586
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('PowerDecomposition-v1.0/helper', params, id, @execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L586-L587
handles.f1 = 0.0;
handles.f2 = 0.08;
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6114-L6114
    defaultans = {'1/45 1/25','500','2',num2str(handles.f1),num2str(handles.f2),'1','5000','1','1'};
%% End copied source
answer=defaultans; f3=[1/45 1/25];
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6119-L6124
        window = str2double(answer{2});
        nw = str2double(answer{3});
        ftmin = str2double(answer{4});
        fterm = str2double(answer{5});
        step = str2double(answer{6});
        pad = str2double(answer{7});
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L6126-L6126
        padtype = str2double(answer{9});
%% End copied source
r = struct();
r.data = data;
r.f3 = f3;
r.window = window;
r.nw = nw;
r.ftmin = ftmin;
r.fterm = fterm;
r.step = step;
r.pad = pad;
r.padtype = padtype;
end
