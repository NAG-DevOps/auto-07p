#! /usr/bin/env python
try:
    import grapher_mpl 
    grapher = grapher_mpl
except ImportError:
    import grapher
import parseB
import parseS
import AUTOutil
import types
import os

class plotter(grapher.GUIGrapher):
    def __init__(self,parent=None,cnf={},**kw):

        optionDefaults = {}
        # The kind of diagram (single solution vs. bifur diagram)
        optionDefaults["type"]     = ("bifurcation",self.__optionCallback)  
        # The X column
        optionDefaults["bifurcation_x"] = ([0],self.__optionCallback)
        optionDefaults["solution_x"]    = (["t"],self.__optionCallback)
        # The Y column
        optionDefaults["bifurcation_y"] = ([1],self.__optionCallback)
        optionDefaults["solution_y"]    = ([0],self.__optionCallback)
        # Sets of labels that the user is likely to want to use
        optionDefaults["label_defaults"]   = (None,self.__optionCallback)
        # Sets of columns that the user is likely to want to use
        optionDefaults["bifurcation_column_defaults"]   = (None,self.__optionCallback)
        optionDefaults["solution_column_defaults"]   = (None,self.__optionCallback)
        # The index of the solution we wish to draw
        optionDefaults["index"]    = ([0],self.__optionCallback)
        # The label of the solution we wish to draw
        optionDefaults["label"]    = ([0],self.__optionCallback)

        # Already parsed data structures
        optionDefaults["bifurcation_diagram"]          = (parseB.parseBR(),self.__optionCallback)
        optionDefaults["solution"]          = (parseS.parseS(),self.__optionCallback)
        optionDefaults["bifurcation_diagram_filename"] = ("",self.__optionCallback)
        optionDefaults["solution_filename"] = ("",self.__optionCallback)
        optionDefaults["runner"]         = (None,self.__optionCallback)
        optionDefaults["mark_t"]         = (None,self.__optionCallback)

        optionDefaults["bifurcation_symbol"]     = ("B",self.__optionCallback)
        optionDefaults["limit_point_symbol"]     = ("L",self.__optionCallback)
        optionDefaults["hopf_symbol"]            = ("H",self.__optionCallback)
        optionDefaults["period_doubling_symbol"] = ("D",self.__optionCallback)
        optionDefaults["torus_symbol"]           = ("T",self.__optionCallback)
        optionDefaults["user_point_symbol"]      = ("U",self.__optionCallback)
        optionDefaults["error_symbol"]           = ("X",self.__optionCallback)

        optionDefaults["ps_colormode"]           = ("color",self.__optionCallback)
        optionDefaults["stability"]              = (0,self.__optionCallback)

        parser = AUTOutil.getAUTORC("AUTO_plotter")
        optionDefaultsRC = {}
        for option in parser.options("AUTO_plotter"):
            v = eval(parser.get("AUTO_plotter",option))
            optionDefaultsRC[option] = v

        self.__needsPlot = None
        apply(grapher.GUIGrapher.__init__,(self,parent,optionDefaultsRC))

        dict = AUTOutil.cnfmerge((cnf,kw))
        self.addOptions(optionDefaults)
        self.addRCOptions(optionDefaultsRC)
        plotter._configNoDraw(self,optionDefaultsRC)
        plotter._configNoDraw(self,dict)
        self._plotNoDraw()
        self.__needsPlot = None
        self.computeXRange()
        self.computeYRange()
        grapher.GUIGrapher.plot(self)

    def config(self,cnf=None,**kw):
        if type(cnf) == types.StringType or (cnf is None and len(kw) == 0):
            return self._configNoDraw(cnf)
        else:
            self._configNoDraw(AUTOutil.cnfmerge((cnf,kw)))
        if self.__needsPlot:
            self._plotNoDraw()
            self.__needsPlot = None
            self.clear()
            self.computeXRange()
            self.computeYRange()
            grapher.GUIGrapher.plot(self)
        else:
            self.clear()
        self.draw()
        self.update()
        
    configure=config

    def _configNoDraw(self,cnf=None,**kw):
        if type(cnf) == types.StringType or (cnf is None and len(kw) == 0):
            return grapher.GUIGrapher._configNoDraw(self,cnf)
        else:
            grapher.GUIGrapher._configNoDraw(self,AUTOutil.cnfmerge((cnf,kw)))
    _configureNoDraw = _configNoDraw

    def __optionCallback(self,key,value,options):
        if key == "runner":
            self.cget("bifurcation_diagram").read(value.getBifurcation_diagram())
            self.cget("solution").read(value.getSolution())
        elif key == "bifurcation_diagram_filename":
            if os.path.exists(value):
                self.cget("bifurcation_diagram").readFilename(value)
        elif key == "solution_filename":
            if os.path.exists(value):
                self.cget("solution").readFilename(value)
            if self.cget("label") != [0]:
                self.__optionCallback("label",self.cget("label"),options)
        elif key == "label":
            labels = self.cget("solution").getLabels()
            options["index"] =[]
            for v in value:
                for j in range(len(labels)):
                    if labels[j] == v:
                        options["index"].append(j)
        elif key == "index":
            options["label"] =[]
            for v in value:
                labels = self.cget("solution").getLabels()
                options["label"].append(labels[v])
        # We only recreate the data if one of the above options gets set
        # We can't just recreate the data for any option since:
        #   1)  It is inefficient
        #   2)  The range gets recomputed when we create new data, so
        #       minx, miny, maxx, and maxy all never get used.
        self.__needsPlot = "yes"

    def _plotNoDraw(self):
        self.delAllData()
        if self.cget("type") == "bifurcation" and len(self.cget("bifurcation_diagram")) > 0:
            self.__plot7()
        if self.cget("type") == "solution" and len(self.cget("solution")) > 0:
            self.__plot8()

    def plot(self):
        self._plotNoDraw()
        self.clear()
        self.computeXRange()
        self.computeYRange()
        grapher.GUIGrapher.plot(self)
        self.draw()

    def __plot7(self):
        symbollist = [
            [[1,6], "bifurcation_symbol"],
            [[2,5], "limit_point_symbol"],
            [[3],   "hopf_symbol"],
            [[8],   "torus_symbol"],
            [[-4],  "user_point_symbol"]]
        xcolumns = self.cget("bifurcation_x")
        ycolumns = self.cget("bifurcation_y")
        self.delAllData()
        solution = self.cget("bifurcation_diagram")
        dp = self.cget("stability")
        if len(solution) > 0 and len(xcolumns) == len(ycolumns):
            for j in range(len(xcolumns)):
                for branch in solution:
                    data = branch["data"]
                    try:
                        x = data[xcolumns[j]]
                    except IndexError:
                        print "The x-coordinate (set to column %d) is out of range"%xcolumns[j]
                        break
                    try:
                        y = data[ycolumns[j]]
                    except IndexError:
                        print "The y-coordinate (set to column %d) is out of range"%ycolumns[j]
                        break
                    if dp:
                        #look at stability:
                        newsect = 1
                        old = 0
                        for pt in branch["stability"]:
                            abspt = abs(pt)
                            if old < abspt - 1 and abspt > 2:
                                self.addArrayNoDraw((x[old:abspt],y[old:abspt]),
                                                    newsect,stable=pt<0)
                                old = abspt - 1
                                newsect = 0
                    else:
                        self.addArrayNoDraw((x,y),1)
                    for label in branch["Labels"]:
                        lab = label["LAB"]
                        TYnumber = label["TY number"]
                        text = ""
                        if lab != 0:
                            text = str(lab)
                        symbol = None
                        for item in symbollist:
                            if TYnumber in item[0]:
                                symbol = self.cget(item[1])
                        if not symbol and TYnumber not in [0,4,9]:
                            symbol = self.cget("error_symbol")
                        i = label["index"]
                        self.addLabel(len(self)-1,[x[i],y[i]],text,symbol)
        
        # Call the base class config
        xlabel = self["xlabel"]
        if self.config("xlabel")[3] is None:
            xlabel = "Column %d"%xcolumns[0]
        ylabel = self["ylabel"]
        if self.config("ylabel")[3] is None:
            ylabel = "Column %d"%ycolumns[0]
        grapher.GUIGrapher._configNoDraw(self,xlabel=xlabel,ylabel=ylabel)

    def __plot8(self):
        self.delAllData()
        xcolumns = self.cget("solution_x")
        ycolumns = self.cget("solution_y")

        if len(xcolumns) == len(ycolumns):
            xnames="Error"
            ynames="Error"
            index = 9
            for ind in self.cget("index"):
                sol = self.cget("solution").getIndex(ind)
                solution = sol["data"]
                label = sol["Label"]
                xnames = ""
                ynames = ""
                for j in range(len(xcolumns)):
                    labels = []
                    xc = xcolumns[j]
                    yc = ycolumns[j]
                    if xc == "t":
                        x = map(lambda s: s["t"], solution)
                    else:
                        x = map(lambda s, c = xc: s["u"][c], solution)
                    if yc == "t":
                        y = map(lambda s: s["t"], solution)
                    else:
                        y = map(lambda s, c = yc: s["u"][c], solution)

                    if not(self.cget("mark_t") is None):
                        for i in range(len(solution)):
                            if i != 0 and solution[i-1]["t"] <= self.cget("mark_t") < solution[i]["t"]:
                                labels.append({"index": i,
                                               "text": "",
                                               "symbol": "fillcircle"})
                    if len(solution) <= 15:
                        index = 1
                        if len(solution) <= 1:
                            index = 0
                    labels.append({"index": index, "text": str(label), "symbol": ""})
                    # Call the base class config
                    if len(x) > 0:
                        self.addArrayNoDraw((x,y))
                    for lab in labels:
                        self.addLabel(len(self)-1,
                                      [x[lab["index"]],y[lab["index"]]],
                                      lab["text"],lab["symbol"])

                    xnames = xnames + " " + str(xcolumns[j])
                    ynames = ynames + " " + str(ycolumns[j])
                index = index + 10
                if index > len(solution):
                    index = 14
            xlabel = self["xlabel"]
            if self.config("xlabel")[3] is None:
                xlabel = "Columns %s"%xnames
            ylabel = self["ylabel"]
            if self.config("ylabel")[3] is None:
                ylabel = "Columns %s"%ynames
            grapher.GUIGrapher._configNoDraw(self,xlabel=xlabel,ylabel=ylabel)


def test():
    import parseB
    import parseS
    import sys
    foo = plotter(bifurcation_diagram_filename="../test_data/fort.7",
                  solution_filename="../test_data/fort.8")

    foo.plot()
    foo.pack()
    foo.update()
    print "Hit return to continue"
    raw_input()
    foo.clear()
    foo.update()
    print "Hit return to continue"
    raw_input()
    foo.clear()
    foo.config(type="solution",label=[6])
    foo.plot()
    foo.update()
    print "Hit return to continue"
    raw_input()
    foo.clear()
    foo.config(index=[3])
    foo.plot()
    foo.update()
    print "Hit return to continue"
    raw_input()

if __name__ == "__main__":
    test()





