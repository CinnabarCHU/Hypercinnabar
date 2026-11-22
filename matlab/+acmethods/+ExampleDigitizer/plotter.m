function [retval, id] = plotter(params, id)
% ExampleDigitizer.plotter parameters: im_name data_name.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L8251
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ExampleDigitizer-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
im_name = p.im_name;
data_name = p.data_name;
[~,dat_name,ext]=fileparts(data_name);
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L8251-L8253
    figure;
    imshow(im_name)
    set(gcf,'Name',[dat_name,ext],'NumberTitle','off')
%% End copied source
r=[];
end
