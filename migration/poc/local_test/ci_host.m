function ci_host()
% Keep the user's packaged entry point alive while another process uses Harness.
root = pwd;
fig = start_local_demo();
done = fullfile(root,'generated','local-tests-done.json');
deadline = tic;
while ~isfile(done) && toc(deadline)<360
    drawnow;
    pause(.05);
end
assert(isfile(done),'Local test client did not finish.');
result = jsondecode(fileread(done));
assert(strcmp(result.status,'passed'),'The local commands reported an error.');
assert(isgraphics(fig,'figure'));
filter = findall(groot,'Tag','ft_figure');
assert(isscalar(filter));
s = getappdata(filter,'AcycleAnalysis');
assert(s.params.flow==.035 && s.params.fhigh==.055 && s.plt.x_2==.13);
assert(isequaln(s.res,accore.replay(s.ids.analyzer)));
h = acgui.state(filter);
assert(isequal(h.data_filterout,s.res.data_filterout));
original = accore.io('read',fullfile(root,'study','series.csv'));
reference = gaussfilter(original(:,2)-mean(original(:,2)),1,.045,.035,.055);
assert(max(abs(reference(:)-h.data_filterout(:,2)))<1e-10);
image = findall(groot,'Tag','aclive_transect');
assert(isscalar(image));
session = acgui.share(fig);
delete(image); delete(filter); delete(fig);
assert(~isfolder(session));
fprintf('PASS local package entry point, official Harness commands, GUI state, numerical replay and close cleanup.\n');
end
