function [retval, id] = helper(params, id)
% Undatable.helper parameters: inputfile nsim xfactor bootpc.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/undatable/undatable.m#L115
if nargin < 2, id = []; end
params=accompat.inputSnapshot(params);
[retval, id] = aclog.invoke('Undatable-v1.0/helper', params, id, @execute);
end

function r = execute(p)
if ~isfield(p,'input_bytes'), error('Acycle:Undatable:Input','Cannot read the input chronology.'); end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/package/undatable/undatable.m:L115-L127
defaultcombine = 1;
defaultplotme = 1;
defaultprintme = 1;
defaultsavemat = 0;
defaultsavebigmat = 0;
defaultdebug = 0;
defaultwritedir = '';
defaultguimode = 0;
defaultallowreversal = 0;
defaultrun1nsim = 2000;
defaultsar = 0;
defaultvcloud = 0;
defaultplotsar = 0;
%% End copied source
r=p;
if ~isfield(r,'combine'), r.combine=defaultcombine; end
if ~isfield(r,'printme'), r.printme=defaultprintme; end
if ~isfield(r,'savemat'), r.savemat=defaultsavemat; end
if ~isfield(r,'savebigmat'), r.savebigmat=defaultsavebigmat; end
if ~isfield(r,'debug'), r.debug=defaultdebug; end
if ~isfield(r,'writedir'), r.writedir=defaultwritedir; end
if ~isfield(r,'allowreversal'), r.allowreversal=defaultallowreversal; end
if ~isfield(r,'run1nsim'), r.run1nsim=defaultrun1nsim; end
if ~isfield(r,'sar'), r.sar=defaultsar; end
if ~isfield(r,'vcloud'), r.vcloud=defaultvcloud; end
if ~isfield(r,'plotsar'), r.plotsar=defaultplotsar; end
end
