function serve_gui_harness()
% A separate process connects to this visible, long-lived MATLAB session.
root = getenv('RUNNER_TEMP');
setup_acycle();
setenv('ACYCLE_LOG_DIR',fullfile(root,'gui-journals'));
study = fullfile(root,'study');
t = (0:255)'; data = [t,sin(2*pi*t/20)+.2*cos(2*pi*t/5)];
writematrix(data,fullfile(study,'series.csv'));
writematrix([t,cos(2*pi*t/17)],fullfile(study,'second.csv'));
imwrite(reshape(uint8(1:100),10,10),fullfile(study,'core.png'));
main = ac(study); h = acgui.state(main);
h.listbox_acmain.Value = find(strcmp(cellstr(h.listbox_acmain.String),'series.csv'));
cb = h.menu_filter.Callback; cb(h.menu_filter,[]);
assert(strcmp(acgui.share('AcycleDesktopTest'),'AcycleDesktopTest'));
fid = fopen(fullfile(root,'gui-ready'),'w'); fclose(fid);
deadline = tic;
timeLimit = 420;
if ~isempty(getenv('ACYCLE_PROVIDER_FIXTURE')), timeLimit = 900; end
while ~isfile(fullfile(root,'gui-done')) && toc(deadline)<timeLimit
    drawnow;
    pause(.05);
end
assert(isfile(fullfile(root,'gui-done')),'The external client did not finish.');
assert(strcmp(strtrim(fileread(fullfile(root,'gui-done'))),'ok'),'The external client reported an error.');
assert(isgraphics(main,'figure'),'Detaching the client closed the desktop.');
delete(findall(groot,'Type','figure'));
end
