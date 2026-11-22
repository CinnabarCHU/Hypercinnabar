function cleanup = tanerWorkspace()
% tanerhilbertML exports its filter into the caller's base workspace.
present = evalin('base','exist(''tanerfilterenv'',''var'') ~= 0');
if present
    previous = evalin('base','tanerfilterenv');
    cleanup = onCleanup(@() assignin('base','tanerfilterenv',previous));
else
    cleanup = onCleanup(@() evalin('base','clear tanerfilterenv'));
end
end
