function [retval,id] = helper(params,id)
% select_interval.helper parameters: data.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('select_interval-v3.1.1+dcba427/helper',params,id,@execute);
end

function r = execute(p)
data = p.data;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3075-L3077
        time = data(:,1);
        value = data(:,2);
        npts = length(time);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3086-L3086
        defaultans = {num2str(time(1)),num2str(time(npts)),'0'};
%% End copied source
t1=str2double(defaultans{1}); t2=str2double(defaultans{2});
r = struct();
r.data = data;
r.t1 = t1;
r.t2 = t2;
end
