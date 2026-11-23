function filterChange(fig,params,style)
% Apply a compound edit once through the same refresh script as ft's callbacks.
h = acgui.state(fig);
s = getappdata(fig,'AcycleAnalysis');
if ~isstruct(s) || ~strcmp(s.operation,'Bandpass_legacy')
    error('Acycle:GUI:Unsupported','This filter mode does not expose live bandpass edits.');
end
p = applyFields(s.params,params,{'flow','fhigh'});
plt = applyFields(s.plt,style,{'x_1','x_2','y_1','y_2'});
nyquist = 1/(2*mean(diff(s.params.data(:,1))));
if p.flow<0 || p.fhigh<=p.flow || p.fhigh>nyquist
    error('Acycle:GUI:Band','Expected 0 <= flow < fhigh <= Nyquist (%g).',nyquist);
end
if plt.x_2<=plt.x_1 || plt.y_2<=plt.y_1
    error('Acycle:GUI:Limits','Axis maxima must exceed their minima.');
end
if isequaln(p,s.params) && isequaln(plt,s.plt), return; end
widgets = [h.edit1,h.edit2,h.edit10,h.edit11,h.edit12,h.edit13];
values = [p.flow,p.fhigh,plt.x_1,plt.x_2,plt.y_1,plt.y_2];
previous = get(widgets,'String'); center = h.text3.String; passMode = h.popupmenu5.Value;
try
    for k = 1:numel(values), widgets(k).String = num2str(values(k),17); end
    hObject = fig; handles = h; %#ok<NASGU>
    update_filter_axes
catch err
    for k = 1:numel(widgets), widgets(k).String = previous{k}; end
    h.text3.String = center; h.popupmenu5.Value = passMode;
    acgui.state(fig,h); setappdata(fig,'AcycleAnalysis',s);
    % Restore both panels even when a renderer failed after drawing the first one.
    for panel = {'fft','mtm'}
        if strcmp(panel{1},'fft'), target=h.ft_axes3; else, target=h.ft_axes4; end
        try, accli.replot(s,struct('panel',panel{1}),target); catch, end
    end
    rethrow(err);
end
end

function obj = applyFields(obj,patch,accepted)
if ~isstruct(patch) || ~isscalar(patch) || ~all(ismember(fieldnames(patch),accepted))
    error('Acycle:GUI:Fields','Unsupported fields for this window.');
end
for n = reshape(fieldnames(patch),1,[])
    value = patch.(n{1});
    validateattributes(value,{'numeric'},{'real','finite','scalar'});
    obj.(n{1}) = value;
end
end
