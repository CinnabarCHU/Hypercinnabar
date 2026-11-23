function [s,result] = bispectral(data,options,observer)
% Keep cancellation in the live UI without serializing a closure over its controls.
previous = acgui.progress(observer);
cleanup = onCleanup(@()acgui.progress(previous)); %#ok<NASGU>
options.ProgressFcn = @acgui.progress;
s = accli.run('menu_bispectral',struct('data',data),'Params',struct('options',options));
result = s.res;
end
