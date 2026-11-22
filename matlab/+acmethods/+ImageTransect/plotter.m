function [retval, id] = plotter(params, id)
% ImageTransect.plotter parameters: data color_type dat_name distance_label grayscale_label.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4356
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ImageTransect-v1.0/plotter', params, id, @execute);
end

function r = execute(p)
data = p.data;
color_type = p.color_type;
dat_name = p.dat_name;
distance_label = p.distance_label;
grayscale_label = p.grayscale_label;
imfinfo1.ColorType=color_type; a157=distance_label; a156=grayscale_label; z=data(:,1);
figure;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4356-L4356
                            plot(data(:,1),data(:,2:end));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4364-L4376
                            xlabel(a157);

                            xlim([0,z(end)])
                            set(gca,'XMinorTick','on','YMinorTick','on')
                            if strcmp(imfinfo1.ColorType,'grayscale')
                                ylabel(a156)
                            elseif strcmp(imfinfo1.ColorType,'CIELab')
                                ylabel('CIELab')
                                legend('L*','a*','b*')
                            elseif strcmp(imfinfo1.ColorType,'truecolor')
                                ylabel('RGB')
                                legend('Red','Green','Blue')
                            else
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4378-L4378
                                    ylabel('Value')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4382-L4382
                            end
%% End copied source
r=[];
end
