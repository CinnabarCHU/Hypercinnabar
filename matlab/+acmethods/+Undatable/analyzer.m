function [retval, id] = analyzer(params, id)
% Undatable.analyzer parameters: inputfile nsim xfactor bootpc combine printme savemat savebigmat debug writedir allowreversal run1nsim sar vcloud plotsar.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/package/undatable/undatable.m#L115
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('Undatable-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
[udoutput, shadingmat, sarsummarymat, sarshadingmat] = undatable( ...
    p.inputfile, p.nsim, p.xfactor, p.bootpc, ...
    'combine', p.combine, 'plotme', 0, 'printme', p.printme, ...
    'savemat', p.savemat, 'savebigmat', p.savebigmat, 'debug', p.debug, ...
    'writedir', p.writedir, 'guimode', 0, 'allowreversal', p.allowreversal, ...
    'run1nsim', p.run1nsim, 'sar', p.sar, 'vcloud', p.vcloud, ...
    'plotsar', p.plotsar);
r = struct();
r.udoutput = udoutput;
r.shadingmat = shadingmat;
r.sarsummarymat = sarsummarymat;
r.sarshadingmat = sarshadingmat;
end
