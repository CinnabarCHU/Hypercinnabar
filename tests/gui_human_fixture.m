function out = gui_human_fixture(action)
% Test driver for native user callbacks. Not included in either installed product.
root = getenv('RUNNER_TEMP'); folder = fullfile(root,'study');
fig = findall(groot,'Tag','ft_figure');
switch action
    case 'verify_export'
        h = acgui.state(fig); s = getappdata(fig,'AcycleAnalysis');
        assert(str2double(h.edit1.String)==s.params.flow && str2double(h.edit2.String)==s.params.fhigh);
        assert(isequal(s.res.data_filterout,h.data_filterout));
        original = accore.io('read',h.data_name);
        original = sortrows(original);
        y = original(:,2)-mean(original(:,2));
        ref = gaussfilter(y,mean(diff(original(:,1))),mean([s.params.flow s.params.fhigh]),s.params.flow,s.params.fhigh);
        assert(max(abs(ref(:)-h.data_filterout(:,2)))<1e-10);
        assert(isequaln(s.res,accore.replay(s.ids.analyzer)));
        assert(max(abs(h.ft_axes3.XLim-[s.plt.x_1,s.plt.x_2]))<1e-12 && ~isempty(h.ft_axes4.Children));
        figure(fig); invoke(h.pushbutton26);
        saved = readmatrix(fullfile(folder,h.add_list));
        assert(max(abs(saved(:)-s.res.data_filterout(:)))<1e-6);
    case 'manual_edit'
        h = acgui.state(fig); h.edit2.String = '0.065'; invoke(h.edit2);
    case 'save_exchange'
        s = getappdata(fig,'AcycleAnalysis');
        accore.io('save',fullfile(folder,'filter-exchange.mat'),s);
    case 'close_filter'
        delete(fig);
    case 'capture_filter'
        fig.Units = 'pixels'; fig.Position = [110 170 1100 620]; figure(fig); drawnow;
    case 'first_image_point'
        pick = findall(groot,'Tag','aclive_transect');
        raster = findobj(pick,'Tag','aclive_image');
        raster.ButtonDownFcn(raster,struct('IntersectionPoint',[2 3 0]));
    case 'finish_image'
        pick = findall(groot,'Tag','aclive_transect');
        raster = findobj(pick,'Tag','aclive_image');
        raster.ButtonDownFcn(raster,struct('IntersectionPoint',[7 4 0]));
        invoke(findobj(pick,'Tag','aclive_undo'));
        raster.ButtonDownFcn(raster,struct('IntersectionPoint',[9 7 0]));
        invoke(findobj(pick,'Tag','aclive_finish'));
        s = getappdata(pick,'AcycleAnalysis'); assert(isequal(s.res.data1,[2 3;9 7]));
        assert(isequaln(s.res,accore.replay(s.ids.analyzer)));
        pick.Units='pixels'; pick.Position=[180 150 880 660]; figure(pick); drawnow;
    case 'close_images'
        delete(findall(groot,'Tag','aclive_transect'));
    otherwise
        error('Acycle:Test:Action','Unexpected fixture action.');
end
out = 'ok';
end

function invoke(control)
cb = control.Callback;
if iscell(cb), feval(cb{1},control,[],cb{2:end}); else, cb(control,[]); end
end
