function serve_gui_harness()
% A separate process connects to this visible, long-lived MATLAB session.
root = getenv('RUNNER_TEMP');
setup_acycle();
setenv('ACYCLE_LOG_DIR',fullfile(root,'gui-journals'));
main = ac(fullfile(root,'study'));
matlab.engine.shareEngine('AcycleDesktopTest');
fid = fopen(fullfile(root,'gui-ready'),'w'); fclose(fid);
deadline = tic;
while ~isfile(fullfile(root,'gui-done')) && toc(deadline)<200
    drawnow;
    pause(.05);
end
assert(isfile(fullfile(root,'gui-done')),'The external client did not finish.');
assert(strcmp(strtrim(fileread(fullfile(root,'gui-done'))),'ok'),'The external client reported an error.');
assert(isgraphics(main,'figure'),'Detaching the client closed the desktop.');
delete(findall(groot,'Type','figure'));
end
