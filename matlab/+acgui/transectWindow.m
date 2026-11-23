function fig = transectWindow(file)
% Nonblocking image transect for human selection in the shared desktop.
imageData = accore.io('readImage',file); info = imfinfo(file); color = info(1).ColorType;
if ~ismember(color,{'grayscale','truecolor'})
    error('Acycle:GUI:Image','This interactive picker supports grayscale and RGB images.');
end
[~,name,ext] = fileparts(file);
fig = figure('Name',['Acycle: Image Profile | ',name,ext],'Tag','aclive_transect','NumberTitle','off','Visible','off');
ax = axes('Parent',fig,'Position',[.08 .17 .84 .77]); raster = imshow(imageData,'Parent',ax);
hold(ax,'on'); trace = plot(ax,NaN,NaN,'g.-','LineWidth',2,'MarkerSize',12,'HitTest','off','PickableParts','none');
title(ax,'Click the image to add profile vertices');
undo = uicontrol(fig,'Style','pushbutton','String','Undo point','Tag','aclive_undo','Units','normalized','Position',[.13 .03 .21 .07],'Callback',@undoPoint);
finish = uicontrol(fig,'Style','pushbutton','String','Finish profile','Tag','aclive_finish','Units','normalized','Position',[.395 .03 .21 .07],'Enable','off','Callback',@complete);
uicontrol(fig,'Style','pushbutton','String','Close','Tag','aclive_close','Units','normalized','Position',[.66 .03 .21 .07],'Callback',@(~,~)delete(fig));
state = struct('file',file,'points',zeros(0,2));
setappdata(fig,'AcycleTransect',state);
raster.Tag = 'aclive_image'; raster.ButtonDownFcn = @pick;
acgui.liveMark(fig,'image_profile','awaiting_input','opened',struct('input_path',file));
fig.Visible = 'on';

    function pick(~,evt)
        point = evt.IntersectionPoint(1:2);
        if any(~isfinite(point)) || point(1)<1 || point(1)>size(imageData,2) || point(2)<1 || point(2)>size(imageData,1), return; end
        state.points(end+1,:) = point;
        refreshPoints();
    end

    function undoPoint(~,~)
        if ~isempty(state.points), state.points(end,:) = []; refreshPoints(); end
    end

    function refreshPoints()
        trace.XData = state.points(:,1); trace.YData = state.points(:,2);
        if size(state.points,1)>=2, finish.Enable='on'; else, finish.Enable='off'; end
        setappdata(fig,'AcycleTransect',state);
    end

    function complete(~,~)
        if size(state.points,1)<2 || strcmp(finish.Enable,'off'), return; end
        input = struct('I',imageData,'CursorInfo_value',state.points,'color_type',color);
        s = accli.improfile(input);
        setappdata(fig,'AcycleAnalysis',s);
        finish.Enable = 'off'; undo.Enable = 'off'; raster.ButtonDownFcn = [];
        title(ax,sprintf('Profile complete (%d samples)',size(s.res.data,1)));
        acgui.liveMark(fig,'image_profile','completed','completed', ...
            struct('input_path',file,'points',s.res.data1,'analyzer_id',s.ids.analyzer,'sample_count',size(s.res.data,1)));
    end
end
