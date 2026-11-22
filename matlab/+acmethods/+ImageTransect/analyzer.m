function [retval, id] = analyzer(params, id)
% ImageTransect.analyzer parameters: I CursorInfo_value color_type.
% Source: https://github.com/mingsongli/acycle/blob/b52ea9f510f3be00bde9a0238b9898a1e2315b74/code/guicode/AC.m#L4214
if nargin < 2, id = []; end
[retval, id] = aclog.invoke('ImageTransect-v1.0/analyzer', params, id, @execute);
end

function r = execute(p)
I = p.I;
CursorInfo_value = p.CursorInfo_value;
color_type = p.color_type;
imfinfo1.ColorType=color_type;
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4214-L4220
                if strcmp(imfinfo1.ColorType,'CIELab')
                    aDouble = double(I); 
                    cielab(:,:,1) = aDouble(:,:,1) ./ (255/100);
                    cielab(:,:,2) = aDouble(:,:,2)-128;
                    cielab(:,:,3) = aDouble(:,:,3)-128;
                    %I = lab2rgb(cielab);
                    I = cielab(:,:,1);
%% End copied source
end
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4272-L4272
                            if strcmp(imfinfo1.ColorType,'CIELab')
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4283-L4283
                                [cx,cy,c1,xi,yi] = improfile(I,CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4291-L4291
                                [~,~,c2,~,~] = improfile(cielab(:,:,2),CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4300-L4300
                                [~,~,c3,~,~] = improfile(cielab(:,:,3),CursorInfo_value(:,1),CursorInfo_value(:,2));
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4302-L4303
                            else
                                % RGB or grayscale
%% End copied source
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4305-L4334
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
%% Copied from mingsongli/acycle@b52ea9f510f3be00bde9a0238b9898a1e2315b74 code/guicode/AC.m:L4339-L4339
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
