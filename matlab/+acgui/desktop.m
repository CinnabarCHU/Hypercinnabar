function fig = desktop(folder)
% The same directory and version resolution services are used by GUI and CLI.
if nargin, accore.io('chdir',folder); end
fig = AC();
if nargin
    s = acgui.state(fig);
    acgui.refresh(s,accore.io('workspace'));
end
end
