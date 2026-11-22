function [retval, id] = analyzer(params, id)
% tanerhilbertML.analyzer parameters: data fc fl fh c.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/tanerhilbertML.m#L1
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/seriesanalysis/tanerhilbertML.m#L73
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('tanerhilbertML-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
data = p.data;
fc = p.fc;
fl = p.fl;
fh = p.fh;
c = p.c;
existed=evalin('base','exist(''tanerfilterenv'',''var'')'); previous=[];
if existed, previous=evalin('base','tanerfilterenv'); end
guard=onCleanup(@() restoreTaner(existed,previous));
[tanhilb,ifaze,ifreq]=tanerhilbertML(data,fc,fl,fh,c);
r = struct();
r.tanhilb = tanhilb;
r.ifaze = ifaze;
r.ifreq = ifreq;
r.response=evalin('base','tanerfilterenv');
end

function restoreTaner(existed, previous)
if existed, assignin('base','tanerfilterenv',previous); else, evalin('base','clear tanerfilterenv'); end
end
