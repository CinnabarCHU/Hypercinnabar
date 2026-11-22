function [retval,id] = plotter(params,id)
% ImageTransect.plotter parameters: data color_type dat_name distance_label grayscale_label.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ImageTransect-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
data = p.data;
color_type = p.color_type;
dat_name = p.dat_name;
distance_label = p.distance_label;
grayscale_label = p.grayscale_label;
imfinfo1.ColorType=color_type; a157=distance_label; a156=grayscale_label; z=data(:,1);
figure;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5405-L5405
                            plot(data(:,1),data(:,2:end));
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5413-L5425
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
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5427-L5427
                                    ylabel('Value')
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L81-L81
end
%% End copied source
r=[];
end
