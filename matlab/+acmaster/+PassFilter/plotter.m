function [retval,id] = plotter(params,id)
% PassFilter.plotter parameters: f P1 f11 f12(bandstop) passtype y_1 y_2 x_1 x_2.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/misc/update_filter_axes4.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('PassFilter-v3.1.1+dcba427/plotter',params,id,@execute);
end

function r = execute(p)
f = p.f;
P1 = p.P1;
f11 = p.f11;
passtype = p.passtype;
y_1 = p.y_1;
y_2 = p.y_2;
x_1 = p.x_1;
x_2 = p.x_2;
figure;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L49-L50
plot(f,P1)
hold on
%% End copied source
switch passtype
case 'bandstopiir'
    f12=p.f12;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L52-L58
    ff12 = [f11,f12];
    f11 = min(ff12);
    f12 = max(ff12);
    plot([f11,f11],[y_1,y_2],'r-')
    plot([f12,f12],[y_1,y_2],'r-')
    plot([0,f11],[y_2,y_2],'r-')
    plot([f12,max(f)],[y_2,y_2],'r-')
%% End copied source
case 'lowpassiir'
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L61-L62
    plot([f11,f11],[y_1,y_2],'r-')
    plot([0,f11],[y_2,y_2],'r-')
%% End copied source
case 'highpassiir'
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L65-L66
    plot([f11,f11],[y_1,y_2],'r-')
    plot([f11,max(f)],[y_2,y_2],'r-')
%% End copied source
end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/misc/update_filter_axes4.m:L68-L70
xlim([x_1, x_2])
ylim([y_1, y_2])
hold off
%% End copied source
r=[];
end
