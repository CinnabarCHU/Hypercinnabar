function [retval, id] = helper(params, id)
% CircularSpectrum.helper parameters: dat.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/circularspecGUI.m#L171
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('CircularSpectrum-v1.0/helper', params, id, @execute);
end

function r = execute(p)
dat = p.dat;
dat = dat(:,1);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/circularspecGUI.m:L183-L191
datx = dat(:,1);
datx = sort(datx);
diffx = diff(datx);
handles.dt = min(diffx)/2;
handles.fh = (max(datx) - min(datx))/2;
handles.sedmin = handles.dt;
handles.sedmax = handles.fh;
handles.numsed = 100;
handles.linLog = 2;
%% End copied source
r = struct('data',dat,'p1',str2double(num2str(handles.sedmin)), ...
    'p2',str2double(num2str(handles.sedmax)),'pn',handles.numsed,'linlog',handles.linLog);
end
