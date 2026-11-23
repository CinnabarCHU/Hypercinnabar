function varargout = window(name,layout,opening,output,varargin)
% Launch a code-defined singleton and preserve the window's public output.
figs = findall(groot,'Type','figure');
fig = [];
for k = 1:numel(figs)
    if isequal(getappdata(figs(k),'AcycleWindowName'),name)
        fig = figs(k); break
    end
end
if isempty(fig)
    before = get(groot,'CurrentFigure');
    show = get(groot,'DefaultFigureVisible');
    [fig,h,init] = layout();
    try
        handleVisibility = fig.HandleVisibility;
        fig.HandleVisibility = 'on';
        setappdata(fig,'AcycleWindowName',name);
        acgui.state(fig,h);
        for k = 1:numel(init), init{k}(); end
        set(groot,'CurrentFigure',fig);
        opening(fig,[],acgui.state(fig),varargin{:});
        if strcmp(name,'AC')
            acgui.extendDesktop(fig);
        end
        if isgraphics(fig), set(fig,'HandleVisibility',handleVisibility,'Visible',show); end
        if strcmp(name,'AC')
            drawnow;
            fitDesktop(fig);
        end
    catch err
        if isgraphics(fig), delete(fig); end
        if isgraphics(before), set(groot,'CurrentFigure',before); end
        rethrow(err)
    end
else
    if ~isempty(varargin)
        % A new file selection rebinds this singleton's scientific state.
        h = acgui.state(fig);
        if isfield(h,'trendSessions'), h = rmfield(h,'trendSessions'); end
        if isfield(h,'detrendfig') && isgraphics(h.detrendfig), delete(h.detrendfig); end
        previous = fig.HandleVisibility;
        guard = onCleanup(@()restoreVisibility(fig,previous)); %#ok<NASGU>
        fig.HandleVisibility = 'on';
        set(groot,'CurrentFigure',fig);
        opening(fig,[],h,varargin{:});
    end
    if strcmp(get(groot,'DefaultFigureVisible'),'on'), figure(fig); end
end
if nargout
    if isgraphics(fig)
        [varargout{1:nargout}] = output(fig,[],acgui.state(fig));
    else
        varargout = repmat({[]},1,nargout);
    end
end
end

function fitDesktop(fig)
% AC's original size and origin use the scale of the first monitor.
root = groot;
rootUnits = root.Units; figureUnits = fig.Units;
restoreRoot = onCleanup(@()set(root,'Units',rootUnits)); %#ok<NASGU>
restoreFigure = onCleanup(@()set(fig,'Units',figureUnits)); %#ok<NASGU>
root.Units = 'pixels'; fig.Units = 'pixels';
monitor = root.MonitorPositions(1,:);
outer = fig.OuterPosition;
margin = 8;
extent = min(outer(3:4),monitor(3:4)-2*margin);
origin = max(monitor(1:2)+margin,min(outer(1:2),monitor(1:2)+monitor(3:4)-margin-extent));
if ~isequal(outer,[origin extent]), fig.OuterPosition = [origin extent]; end
end

function restoreVisibility(fig,previous)
if isgraphics(fig), fig.HandleVisibility = previous; end
end
