from django.shortcuts import render
from django.conf import settings
import glob
import imp
import os

reportdir = settings.HOSTINFO_REPORT_DIR


################################################################################
def index(request):
    d = {"reports": getReports()}
    return render(request, "report/index.template", d)


################################################################################
def getReports():
    ans = []
    repfiles = glob.glob(os.path.join(reportdir, "*.py"))
    for rf in repfiles:
        repmodule = module_from_path(rf)
        if hasattr(repmodule, "reportname"):
            name = repmodule.reportname
        else:
            name = "unknown name"

        if hasattr(repmodule, "reportdesc"):
            desc = repmodule.reportdesc
        else:
            desc = "unknown description"
        link = "report/%s" % os.path.split(rf)[1].replace(".py", "")
        ans.append((link, name, desc))
    return ans


################################################################################
def doReport(request, report, args=""):
    reportmodule = os.path.join(reportdir, "%s.py" % report)
    if os.path.exists(reportmodule):
        repmodule = module_from_path(reportmodule)
        try:
            return repmodule.doReport(request, args)
        except Exception as err:
            return render(request, "report/error.template", {"error": err})


################################################################################
def module_from_path(filepath):
    """Taken from djangosnippets.org/snippets/757"""
    dirname, filename = os.path.split(filepath)
    mod_name = filename.replace(".py", "")
    dot_py_suffix = (".py", "U", 1)  # From imp.get_suffixes()[2]
    return imp.load_module(mod_name, open(filepath), filepath, dot_py_suffix)


# EOF
