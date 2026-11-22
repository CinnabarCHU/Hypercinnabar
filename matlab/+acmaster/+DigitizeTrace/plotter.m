function [retval,id] = plotter(params,id)
% DigitizeTrace.plotter parameters: image result.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/plotdigitizer.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('DigitizeTrace-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
figure; image(p.image); axis image; colormap(gray(256));
pts = p.result.pixels;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/plotdigitizer.m:L575-L577
                hold on;
                plot(pts(:,1),pts(:,2),'+','Color',[0 0.7 0],'MarkerSize',6);
                hold off;
%% End copied source
r = [];
end
