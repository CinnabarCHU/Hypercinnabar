function [retval,id] = analyzer(params,id)
% CENOGRID.analyzer parameters: (none).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('CENOGRID-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8957-L8958
data_name = which('Example-cenogrid-d18o.txt');
data_name2 = which('Example-cenogrid-d13c.txt');
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L3074-L3076
        data = load(data_name);
        time = data(:,1);
        value = data(:,2);
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L8975-L8977
data = load(data_name2);
time2 = data(:,1);
value2 = data(:,2);
%% End copied source
r = struct();
r.time = time;
r.value = value;
r.time2 = time2;
r.value2 = value2;
end
