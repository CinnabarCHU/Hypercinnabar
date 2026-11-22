function [retval,id] = analyzer(params,id)
% ImageTransect.analyzer parameters: I CursorInfo_value color_type.
% Source: https://github.com/mingsongli/acycle/blob/dcba4279168745b563e0535b954297023dd62fc7/code/guicode/AC.m
if nargin < 2, id = []; end
[retval,id] = accompat.masterInvoke('ImageTransect-v3.1.1+dcba427/analyzer',params,id,@execute);
end

function r = execute(p)
I = p.I;
CursorInfo_value = p.CursorInfo_value;
color_type = p.color_type;
imfinfo1.ColorType=color_type;
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5265-L5271
                if strcmp(imfinfo1.ColorType,'CIELab')
                    aDouble = double(I); 
                    cielab(:,:,1) = aDouble(:,:,1) ./ (255/100);
                    cielab(:,:,2) = aDouble(:,:,2)-128;
                    cielab(:,:,3) = aDouble(:,:,3)-128;
                    %I = lab2rgb(cielab);
                    I = cielab(:,:,1);
%% End copied source
end
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L1840-L1840
            if strcmp(imfinfo1.ColorType,'CIELab')
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5334-L5334
                                [cx,cy,c1,xi,yi] = improfile(I,CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5342-L5342
                                [~,~,c2,~,~] = improfile(cielab(:,:,2),CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5351-L5351
                                [~,~,c3,~,~] = improfile(cielab(:,:,3),CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5353-L5354
                            else
                                % RGB or grayscale
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5356-L5385
                                [cx,cy,c,xi,yi] = improfile(I,CursorInfo_value(:,1),CursorInfo_value(:,2));
                            end

                            % pixels
                            cxd = diff(cx);
                            cyd = diff(cy);
                            czd = cxd.*cxd + cyd.*cyd;
                            z = cumsum(sqrt(czd));
                            cz = [0;z];
                            % control pixels
                            cxd = diff(xi);
                            cyd = diff(yi);
                            czd = cxd.*cxd + cyd.*cyd;
                            zc = cumsum(sqrt(czd));
                            czp = [0;zc];
                            czp = [(1:length(xi))',czp];

                            if strcmp(imfinfo1.ColorType,'CIELab')
                                data = [cz,c1,c2,c3];
                            else
                                if strcmp(imfinfo1.ColorType,'grayscale')
                                    data = [cz,c];
                                elseif strcmp(imfinfo1.ColorType,'truecolor')
                                    c = reshape(c,[],3);
                                    data = [cz,c];
                                else
                                    c = reshape(c,[],4);
                                    data = [cz,c];
                                end
                            end
%% End copied source
%% Copied from mingsongli/acycle@dcba4279168745b563e0535b954297023dd62fc7 code/guicode/AC.m:L5390-L5390
                            data1 = [xi,yi];
%% End copied source
r = struct();
r.cx = cx;
r.cy = cy;
r.xi = xi;
r.yi = yi;
r.cz = cz;
r.czp = czp;
r.data = data;
r.data1 = data1;
end
