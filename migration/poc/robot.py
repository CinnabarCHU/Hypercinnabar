"""Extract both pinned Mini-Robot pipelines from their control-reading callbacks."""
import re
import textwrap

FIELDS = {
    "check_nan":"reportNaN", "check_empty":"removeInf", "check_sort":"sort",
    "check_unique":"unique", "check_interp_v":"interpolate", "check_detrend_v":"detrend",
    "check_spectral_v":"spectrum", "check_evofft_v":"evolutionary", "check_wavelet_v":"wavelet",
    "robot_sr":"spacing", "robot_detrend":"trend", "robot_detrendwin":"spanPercent",
    "robot_spectralmethod":"spectrumMethod", "fmax":"maxFrequency", "winevofft":"window",
    "wavep1":"minPeriod", "wavep2":"maxPeriod"
}


def extract(dest, tree):
    path = dest/"code/guicode/RobotGUI.m"
    src = path.read_text()
    start = src.index("        if unit_type == 0",src.index("function robot_Callback"))
    end = src.index("    end",src.index("disp('>>  ==================================================')",start))
    old = textwrap.dedent(src[start:end])
    name = "acRobotFlowLegacy" if tree=="acycle" else "acRobotFlowMaster"
    op = "Robot_legacy" if tree=="acycle" else "Robot"
    # Refreshing a file list is a host concern. Keep numerical steps, their order,
    # branching, naming, plot styles and save precision from the pinned callback.
    if tree == "acycle":
        old, n = re.subn(r"(?ms)^([ \t]*)d = dir; %get files.*?(?=^[ \t]*cd\(pre_dirML\);)",
                         r"\1host.refresh();\n", old)
        assert n == 5, n
    else:
        old = old.replace("refreshRobotMainList(pwd);","host.refresh();")
    old = old.replace("ac_working_directory('get',pwd)","host.folder")
    old = old.replace("accore.io('workspace')","host.folder")
    old = old.replace("warndlg(", "host.warning(").replace("errordlg(", "host.problem(")
    old = old.replace("dlmwrite(", "accore.io('writeMatrix',")
    # Record the data as it exists between stages, before FFT padding changes it.
    old = old.replace("%% save data", "out.prepared = dat;\n%% save data",1)
    old = old.replace("dati = interpolate(dat,robot_sr);",
                      "dati = interpolate(dat,robot_sr); out.resampled = dati;")
    old = old.replace("dat = dats;", "dat = dats; out.detrended = dat;")
    old = old.replace("%% power spectrum", "out.series = dat;\n%% power spectrum")
    old = old.replace("xlim([0,fmax])","out.spectrum = struct('classic',redconfAR1,'robust',redconfML96);\n        xlim([0,fmax])",1)
    old = old.replace("legend('Power','Median',", "out.spectrum = struct('frequency',f,'power',p,'background',theored, ...\n            'confidence',[tabtchi90,tabtchi95,tabtchi99,tabtchi999]);\n        legend('Power','Median',")
    old = old.replace("[s,x_grid,y_grid] = evofft(dat,winevofft,step,dt,0,fn,1);",
                      "[s,x_grid,y_grid] = evofft(dat,winevofft,step,dt,0,fn,1);\n    out.evolutionary = struct('s',s,'x',x_grid,'y',y_grid);")
    old = old.replace("[~,~,~]= waveletML(","[power,period,lag1]= waveletML(")
    old = old.replace("wavep1,wavep2);","wavep1,wavep2); out.wavelet = struct('power',power,'period',period,'lag1',lag1,'maxPeriod',wavep2);")
    old = old.replace("wavep1,1/2*wavep2);","wavep1,1/2*wavep2); out.wavelet = struct('power',power,'period',period,'lag1',lag1,'maxPeriod',wavep2/2);")
    for marker in ("out.prepared =","out.series =","out.detrended =","out.evolutionary =","out.wavelet ="):
        assert marker in old, (name,marker)
    fields = "\n".join(f"{local} = p.settings.{option};" for local,option in FIELDS.items())
    header = (f"function out = {name}(p,host)\n% Workflow extracted from the pinned RobotGUI.m.\n"
              "data = p.data; dat_name = p.name; unit = p.unit; unit_type = p.unitType;\n"
              "ext = '.txt'; robot_savedata = host.save; robot_pause = host.pause;\n"
              "out = struct('prepared',[],'resampled',[],'detrended',[],'series',[], ...\n"
              "    'spectrum',[],'evolutionary',[],'wavelet',[]);\n")
    (path.parent/(name+".m")).write_text(header+fields+"\n"+old+"\nend\n")

    settings = "\n".join(f"        settings.{option} = {local};" for local,option in FIELDS.items())
    owner = ("@()refreshRobotMainList(accore.io('workspace'))" if tree=="master"
             else "@()acgui.refresh(acgui.state(listbox_acmain),accore.io('workspace'))")
    gui = (settings+"\n        host = struct('plot',true,'save',logical(robot_savedata),'pause',robot_pause, ...\n"
           f"            'folder',accore.io('workspace'),'refresh',{owner});\n"
           f"        p = struct('operation','{op}','data',data,'name',dat_name,'unit',unit,'unitType',unit_type,'settings',settings);\n"
           "        id = acMenuNewId(); result = accore.robot(p,id,host);\n"
           "        setappdata(h_robot,'AcycleWorkflow',struct('params',p,'res',result,'id',id));\n")
    path.write_text(src[:start]+gui+src[end:])
