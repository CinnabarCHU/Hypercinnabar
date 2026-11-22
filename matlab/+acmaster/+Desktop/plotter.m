function [retval,id] = plotter(params,id)
% Desktop.plotter parameters: tag (active master desktop required).
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/ac_gui_dispatch.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('Desktop-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
figs = findall(groot,'Type','figure','Tag','acfigmain');
for i = 1:numel(figs)
    if ~isempty(findall(figs(i),'Type','uimenu','Tag','menu_bispectral'))
        fig = figs(i); break
    end
end
if ~exist('fig','var')
    error('Acycle:Desktop:Session','Start the pinned 3.1.1 ac.m in a separate MATLAB desktop session.');
end
item = findall(fig,'Type','uimenu','Tag',p.tag);
if numel(item)~=1, error('Acycle:Desktop:Menu','Unknown or ambiguous menu tag.'); end
current = item;
while isgraphics(current,'uimenu')
    if strcmpi(get(current,'Visible'),'off') || strcmpi(get(current,'Enable'),'off')
        error('Acycle:Desktop:Unavailable','This entry is hidden or disabled in the running desktop.');
    end
    current = get(current,'Parent');
end
callback = get(item,'Callback');
if isa(callback,'function_handle')
    callback(item,[]);
elseif iscell(callback) && ~isempty(callback) && isa(callback{1},'function_handle')
    feval(callback{1},item,[],callback{2:end});
else
    error('Acycle:Desktop:Heading','The selected entry has no callable action.');
end
r = struct('tag',p.tag);
end
