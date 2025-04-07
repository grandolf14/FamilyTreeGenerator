import string
import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QSize, Qt, QTimer,QPoint
from PyQt5.QtGui import QFont,QPainter,QBrush,QImage,QPixmap,QColor,QPicture,QTransform,QPen
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton,QHBoxLayout, QGridLayout, QLineEdit,\
    QMessageBox, QVBoxLayout,QStackedWidget, QFileDialog, QTabWidget, QFormLayout, QTextEdit, QScrollArea, \
    QDialog, QDialogButtonBox,QGraphicsScene,QGraphicsView, QComboBox, QCompleter,QFrame

from random import randint

import Executable as ex
import sqlite3
#import main as main


def newChar(name, family=None, title =None , tags = None, notes= None, unchecked = False, family_Id = None,
            newFamily = False, pat_lineage=None, mat_lineage=None,rel_id=None, sex = None):

    conn = sqlite3.connect("DSA Daten.db")
    c = conn.cursor()

    if newFamily:
        pass
    if family==None and family_Id==None:
        raise ValueError('family or family_id required')

    if not family_Id:
        c.execute("""SELECT rowid 
                            FROM Families
                            Where family_Name = (?)""", (family,))
        familyList=c.fetchone()

        if newFamily or not familyList:
            c.execute("""INSERT INTO Families VALUES(?) """, (family,))
            conn.commit()
            family_Id=c.lastrowid

        else:
            family_Id= familyList[0]


    c.execute("INSERT INTO Individuals VALUES (?,?,?,?,?,?,?,?,?,?) ", (name,family_Id,title, tags, notes, unchecked, pat_lineage, mat_lineage,rel_id,sex))
    id=c.lastrowid
    conn.commit()

    conn.close()
    return id


class Resultbox(QStackedWidget):

    def __init__(self):
        super().__init__()
        self.setPref()
        self.source = None
        self.resultUpdate()

    def setPref(self, reloadBottom=False, paintItemFrame=False, buttonList=None, spacer=True, paintLight:list=[None], standardbutton=None,standardButtonVerticalAlignment=True, ignoreIndex=[0], spacing=10, col=4):
        self.buttons = buttonList
        self.spacing = spacing
        self.col = col
        self.standardbutton=standardbutton
        self.standardButtonVerticalAlignment=standardButtonVerticalAlignment
        self.ignoreIndex=ignoreIndex
        self.paintLight=paintLight
        self.spacer=spacer
        self.reloadBottom=reloadBottom
        self.paintItemFrame=paintItemFrame

    def setSource(self, source):
        self.source = source

    def resultUpdate(self, manualResult=None):

        if manualResult is None:
            result = self.source
        else:
            result = manualResult

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        wid = QWidget()
        scroll.setWidget(wid)

        lay = QGridLayout()
        lay.setVerticalSpacing(20)
        lay.setHorizontalSpacing(20)
        wid.setLayout(lay)

        if result == None:
            self.addWidget(scroll)
            self.setCurrentWidget(scroll)
            return


        for itemIndex, item in enumerate(result):
            row = itemIndex % self.col
            col = itemIndex // self.col
            layout = QVBoxLayout()
            lay.addLayout(layout, col, row)
            layout.addStretch(30)

            if self.standardButtonVerticalAlignment:
                innerLayout =QVBoxLayout()
            else:
                innerLayout=QHBoxLayout()

            if self.standardbutton == None:
                if self.paintItemFrame:
                    frame=QFrame()
                    frame.setLayout(innerLayout)
                    layout.addWidget(frame)
                    frame.setLineWidth(1)
                    frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
                else:
                    layout.addLayout(innerLayout)

            else:
                mainButton = QPushButton()
                mainButton.setLayout(innerLayout)
                mainButton.page=item[0]
                mainButton.clicked.connect(self.standardbutton)
                layout.addWidget(mainButton, stretch=1)

            newtext=""
            for lineIndex, line in enumerate(item):
                if lineIndex in self.ignoreIndex:
                    continue


                text = line
                if type(line) is not str:
                    text = str(line)

                if not self.standardButtonVerticalAlignment:
                    newtext+=text+" "
                else:
                    label = QLabel(text)
                    innerLayout.addWidget(label)

                    if lineIndex in self.paintLight:
                        label.setStyleSheet('color: grey')
                        font=label.font()
                        font.setItalic(True)
                        label.setFont(font)

            if not self.standardButtonVerticalAlignment:
                if self.buttons==None:
                    mainButton.setText(newtext)
                else:
                    label = QLabel(newtext)
                    innerLayout.addWidget(label,alignment=Qt.AlignHCenter)

            if self.buttons is not None:
                for button in self.buttons:
                    pBut = QPushButton(button[0])
                    pBut.page = item[0]
                    pBut.clicked.connect(button[1])
                    innerLayout.addWidget(pBut)


            if self.standardbutton!= None and self.standardButtonVerticalAlignment:
                mainButton.setFixedHeight(innerLayout.minimumSize().height())





            layout.addStretch(30)

            if self.spacer:
                layout.addWidget(QLabel(""))

        widget= self.currentWidget()
        self.removeWidget(widget)

        self.addWidget(scroll)
        self.setCurrentWidget(scroll)

        if self.reloadBottom:
            vbar = scroll.verticalScrollBar()
            vbar.setValue(vbar.maximum())


class MyWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        self.cenWid=QStackedWidget()
        self.setCentralWidget(self.cenWid)

        newlay = QVBoxLayout()
        button = QPushButton('button1')
        button.clicked.connect(lambda: print("button 1 pressed"))
        newlay.addWidget(button)

        label=QLabel("try It")
        newlay.addWidget(label)

        button = QPushButton('button2')
        button.clicked.connect(lambda: print("button 2 pressed"))
        newlay.addWidget(button)

        self.button=QPushButton()
        self.button.clicked.connect(lambda: print("main button pressed"))
        self.button.setLayout(newlay)
        self.cenWid.addWidget(self.button)

        self.cenWid.setCurrentWidget(self.button)

class MyWindow2(QMainWindow):

    def __init__(self,lineage, lineage_Infos, zoomTo=None):

        super().__init__()

        wid=QWidget()
        self.setCentralWidget(wid)

        lay=QVBoxLayout()
        wid.setLayout(lay)

        words= [x[1] for x in ex.searchFactory("",'Families',searchFulltext=True)]

        searchbar=QLineEdit()
        self.timer=QTimer()
        completer=QCompleter(words)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setFilterMode(Qt.MatchContains)
        searchbar.setCompleter(completer)
        completer.setCompletionRole(0)
        completer.activated.connect(lambda: self.search(searchbar.text()))
        lay.addWidget(searchbar)


        self.tree = Family_Tree()
        lay.addWidget(self.tree)





    def search(self,text):
        data=ex.searchFactory(text,'Families',attributes=['family_Name'],searchFulltext=True)

        if len(data)>1:
            dialog=QDialog()
            lay=QVBoxLayout()
            dialog.setLayout(lay)
            self.selectedID = -1
            for item in data:
                button=QPushButton(item[1])
                button.page=item[0]
                button.clicked.connect(lambda: self.tree.updateTree(self.sender().page))
                button.clicked.connect(dialog.close)
                lay.addWidget(button)

            dialog.exec_()
        else:
            self.tree.updateTree(data[0][0])




class Family_Tree(QStackedWidget):
    
    def __init__(self):


        self.banner=QImage('./Graphic_Library/banner3.png')
        self.banner=self.banner.scaled(130,130,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        self.banner=QPixmap.fromImage(self.banner)

        self.firstTime=True

        super().__init__()

        self.updateTree(None)
        
    def updateTree(self,id):
        
        #global Variable assignment
        self.id=id
        
        
        #region Layout assignment
        wid=QWidget()
        lay = QGridLayout()
        lay.setColumnStretch(0,85)
        lay.setColumnStretch(1,7)
        lay.setColumnStretch(2, 7)
        wid.setLayout(lay)

        self.scene=QGraphicsScene(0,0,2000,2000)
        background = QPixmap('./Graphic_Library/Background Pergament.jpg')
        self.scene.setBackgroundBrush(QBrush(background))

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.Antialiasing)
        lay.addWidget(view,0,0,9,1)


        label= QLabel('unnasigned:')
        lay.addWidget(label,0,1,1,2)

        unass_resultbox = Resultbox()
        unass_resultbox.setPref(standardbutton=lambda: self.l_sel_Person.setText(
            str(ex.getFactory(self.sender().page, 'individuals', shortOutput=True)[1]) + " (unassigned)") or self.saveVal.setText(str(self.sender().page)), col=1,
                          standardButtonVerticalAlignment=False)
        lay.addWidget(unass_resultbox, 1, 1, 1, 2)

        label = QLabel('assigned:')
        lay.addWidget(label, 2, 1, 1, 2)

        ass_resultbox = Resultbox()
        ass_resultbox.setPref(standardbutton=lambda: self.l_sel_Person.setText(
            str(ex.getFactory(self.sender().page, 'individuals', shortOutput=True)[1]) + " (assigned)") or self.saveVal.setText(str(self.sender().page)), col=1,
                          standardButtonVerticalAlignment=False)

        lay.addWidget(ass_resultbox, 3, 1, 1, 2)

        self.saveVal=QLabel('None')
        lay.addWidget(self.saveVal,0,0)
        self.saveVal.hide()

        self.l_sel_Person=QLabel('no person selected')
        lay.addWidget(self.l_sel_Person,4,1,1,2)
        label = QLabel('generation')
        lay.addWidget(label, 5, 1)

        self.LE_gen = QLineEdit()
        lay.addWidget(self.LE_gen, 5, 2)

        label = QLabel('relation')
        lay.addWidget(label, 6, 1)

        self.LE_rel = QLineEdit()
        lay.addWidget(self.LE_rel, 6, 2)

        self.QC_rel = QComboBox()
        self.QC_rel.addItem("nächster Verwandter")
        lay.addWidget(self.QC_rel, 7, 1, 1, 2)

        self.calculate=QPushButton('calculate')
        self.calculate.clicked.connect(lambda: self.calculateLineage())   #connect with update lineage
        self.calculate.clicked.connect(lambda: self.updateTree(id))
        lay.addWidget(self.calculate,8,1,1,2)
        #endregion
        
        
        data = ex.searchFactory(id, 'Individuals', attributes=['fKey_family_ID'], dictOut=True)
        
        #gateKeeper, empties resultboxen
        if len(data)==0:
            unass_resultbox.resultUpdate([])
            ass_resultbox.resultUpdate([])
            self.addWidget(wid)
            self.setCurrentWidget(wid)
            return
        
        
        lineage_Infos= {}                  
        unsorted=[]                   
        sortedRes=[]

        for item in data:

            if item['indiv_mat_lineage'] ==None and item['indiv_pat_lineage']==None:
                unsorted.append((item['individual_ID'],item['indiv_fName']))
                continue

            if item['indiv_mat_lineage']!=None and item['indiv_mat_lineage'].startswith(str(id)):
                item_family_pos=item['indiv_mat_lineage'].split('-')[1]
                lineage_Infos[item_family_pos] = item
                sortedRes.append((item['individual_ID'],item['indiv_fName']))

            if item['indiv_pat_lineage']!= None and item['indiv_pat_lineage'].startswith(str(id)):
                item_family_pos = item['indiv_pat_lineage'].split('-')[1]
                lineage_Infos[item_family_pos] = item
                sortedRes.append((item['individual_ID'],item['indiv_fName']))

        
        #gateKeeper, sets Anchoritem (first item for to choose relationship with other items) for family and reloads function
        if len(sortedRes)==0 and len(unsorted)>0:
            anchorItem=ex.getFactory(unsorted.pop(0)[0],'Individuals',dictOut=True)
            if anchorItem['indiv_pat_lineage']==None:
                ex.updateFactory(anchorItem["individual_ID"],[str(self.id)+'-a'],'Individuals',attributes=['indiv_pat_lineage'])
            else:
                ex.updateFactory(anchorItem[0], [str(self.id) + '-a'], 'Individuals', attributes=['indiv_mat_lineage'])
            self.updateTree(self.id)
            return

        #LayoutUpdate: adds owners (sortedRes Items) to Layout Combobox and ResultBox
        for item in sortedRes:
            self.QC_rel.addItem(item[1],item[0])

        unass_resultbox.resultUpdate(unsorted)
        ass_resultbox.resultUpdate(sortedRes)

        # gateKeeper if there are no items for the calculation return 
        if len(lineage_Infos) == 0:
            self.addWidget(wid)
            self.setCurrentWidget(wid)
            return

        #region calculates generations
        lineage_keys = sorted(sorted(list(lineage_Infos)), key=len)
        lineage_SOKeys=[]
        newlineage = []

        #starts with the last generation, any member[item] of the lineage keys will be added to newlineage[generation] if:
        #-there is only 1 descendant in the last generation[ie bbb is a descendant from bb], descendants start with
        #       member_key[item],are not the member and are maximum part of the relevant generation
        #-it is not part of any later generations [len(item)<=round+1]

        for round in range(len(lineage_keys[-1])):
            newlineage.append([])
            for index, item in enumerate(lineage_keys):
                marker=False
                for index2, item2 in enumerate(lineage_keys):
                    if item2.startswith(item) and index != index2 and len(item2) <= round + 1:
                        if marker:
                            break
                        marker=True

                else:

                    if len(item) > round+1:
                        continue

                    # adds SO, adds 1 filler, if needed
                    if not marker and len(item)==round+1:
                        newlineage[round].append(item)

                        if lineage_Infos[item]['indiv_rel_id'] != None:
                            newlineage[round].append(item + "!")
                            lineage_SOKeys.append(item + "!")
                            lineage_Infos[item + "!"] = ex.getFactory(lineage_Infos[item]['indiv_rel_id'], 'Individuals',
                                                                        dictOut=True)
                        else:
                            newlineage[round].append(item[:-1] + "!")

                    #adds filler
                    if not marker and len(item) < round + 1:
                        newlineage[round].append(item+"!")
                        newlineage[round].append(item +"!")


        newlineage = [sorted(x) for x in newlineage]
        lineage_keys=lineage_keys+lineage_SOKeys
        #endregion

        # calculate tree width and tree height
        height = (len(lineage_keys[-1].rstrip('!'))-len(lineage_keys[0])) * 140 + 40
        width = len(newlineage[-1]) * 150 + 40
        x=1000 - int(width / 2) + 70
        y=1000 - int(height / 2)

        #calculate positions for the last generation
        posdict = {}
        for index, item in enumerate(newlineage[- 1]):
            name=item.rstrip('!')
            if name in posdict:
                posdict[name] = ((index * 150)+posdict[name][0],posdict[name][1]+1)
            else:
                posdict[item.rstrip("!")] =(index * 150, 1)


        #calculates other generation
        for gen_index in reversed(range(len(newlineage))):
            for index, item in enumerate(newlineage[gen_index]):
                name=item.rstrip("!")

                xPos = int(posdict[name][0] / posdict[name][1])

                if len(name) < gen_index:
                    if name not in posdict:
                        posdict[name] = (xPos, 1)
                    else:
                        posdict[name]= (posdict[name][0]+xPos,posdict[name][1]+1)
                else:
                    name = name[:-1]
                    oldX = 0
                    number = 0
                    if name in list(posdict):
                        oldX = posdict[name][0]
                        number = posdict[name][1]
                    posdict[name] = (xPos + oldX, number + 1)



        #endregion
        SOposdict={}
        for item in posdict:
            if item+"!" in lineage_SOKeys:
                SOposdict[item + "!"] = [int(posdict[item][0] / posdict[item][1]) + 75,
                                         y + (int(len(item) - len(lineage_keys[0])) * 140 - 60)]

                posdict[item] = [int(posdict[item][0] / posdict[item][1])-75,
                                 y + (int(len(item) - len(lineage_keys[0])) * 140 - 60)]

            else:
                posdict[item] = [int(posdict[item][0] / posdict[item][1]),
                                 y + (int(len(item) - len(lineage_keys[0])) * 140 - 60)]

        for item in SOposdict:
            posdict[item]=SOposdict[item]


        for item in lineage_keys:
            labelback = QLabel()
            labelback.setPixmap(self.banner)
            labelback.setStyleSheet('background-color: transparent')
            labelback.setGeometry(x+posdict[item][0] - 35, posdict[item][1] - 58, 120, 120)
            self.scene.addWidget(labelback)

            label = QLabel(str(lineage_Infos[item]['fKey_family_ID'])+lineage_Infos[item]['indiv_fName']) #!!!remove Family ID Lateron
            label.setAlignment(Qt.AlignLeft)
            label.setAlignment(Qt.AlignVCenter)
            size = label.fontMetrics().boundingRect(label.text())
            label.setGeometry(x+posdict[item][0] + 25 - +int(size.width() / 2), posdict[item][1], size.width(),
                              size.height())
            label.setStyleSheet('background-color: transparent')
            self.scene.addWidget(label)


        for item in lineage_keys:
            name = item[:-1]
            if name in posdict and name != "":
                self.scene.addLine(posdict[item][0]+x + 25, posdict[item][1] - 10, posdict[item][0]+x + 25,
                                   posdict[item][1] - 45, QPen(Qt.black, 2, Qt.SolidLine))
                self.scene.addLine(posdict[name][0]+x + 25, posdict[name][1] + 54, posdict[name][0]+x + 25,
                                   posdict[name][1] + 93, QPen(Qt.black, 2, Qt.SolidLine))

            if item == name + 'a':
                for index, letter in enumerate(string.ascii_lowercase):
                    if name + letter not in posdict:
                        break

                if not index == 1:
                    left = name + 'a'
                    right = name + string.ascii_lowercase[index - 1]
                    self.scene.addLine(posdict[left][0]+x + 25, posdict[left][1] - 45, posdict[right][0] +x + 25,
                                       posdict[right][1] - 45, QPen(Qt.black, 2, Qt.SolidLine))
        self.addWidget(wid)
        self.setCurrentWidget(wid)

        #if zoomTo != None:
        #    x = 8
        #    xPosP = posdict[zoomTo][0] + 20 - view.size().width() / 2
        #    yPosP = posdict[zoomTo][1] + 18 - view.size().height() / 2
        #    view.fitInView(QtCore.QRectF(xPosP, yPosP, view.size().width(), view.size().height()))

        factor=min(view.size().width()/width,view.size().height()/height)
        newWidth=min(max(view.size().width()/factor, view.size().width()//1.5),view.size().width())
        newHeight=min(max(view.size().height()/factor,view.size().height()//1.5),view.size().height())
        view.fitInView(QtCore.QRectF(1000-int(newWidth/2),1000-int(newHeight/2), int(newWidth),int(newHeight)))

    def calculateLineage(self):
        
        #checks userinput for wrong/incomplete Input, sets generationMax, relationshipMax, Verwandter_ID, selbst_ID
        if self.LE_gen.text()==None or self.LE_rel.text()==None or self.QC_rel.currentIndex()==0 or self.saveVal=='None':
            msg = QMessageBox()
            msg.setText('pls fill out values')
            msg.exec()
            return
        
        else:
            generationMax = int(self.LE_gen.text())
            relationshipMax = int(self.LE_rel.text())
            verwandter_ID=self.QC_rel.currentData()
            selbst_ID=int(self.saveVal.text())
        
        #gatekeeper, checks for wrong Input
        if verwandter_ID == selbst_ID:
            msg=QMessageBox()
            msg.setText('identical relative and self')
            msg.exec()
            return
        
        #Gatekeeper, checks for wrong Input
        if generationMax==0 and relationshipMax==0:
            msg=QMessageBox()
            msg.setText('identical relative position and self position')
            msg.exec()
            return

        #gets relative_Code
        relative_code_get=ex.getFactory(verwandter_ID,'individuals',dictOut=True)
        
        if relative_code_get['indiv_mat_lineage']!=None and relative_code_get['indiv_mat_lineage'].startswith(str(self.id)):
            relative_code= relative_code_get['indiv_mat_lineage'].split('-')[1]
        else:
            relative_code= relative_code_get['indiv_pat_lineage'].split('-')[1]
        
        #updates relative_codes of all lineage members if code does not allow the manipulation (for example code aaa
        #needs to be prolonged if you want to have the Grand-Grandparent of aaa)
        if relationshipMax>0:
            if relationshipMax+1>len(relative_code):
                members=ex.searchFactory(str(self.id)+"-",'Individuals',attributes=['indiv_pat_lineage'],  searchFulltext=True,dictOut=True)
                for member in members:
                    newName='a'*(relationshipMax+2)
                    text=member['indiv_pat_lineage'].split('-')
                    ex.updateFactory(member['individual_ID'],[text[0]+"-"+newName+text[1]],'Individuals',['indiv_pat_lineage'])
                relative_code = newName + relative_code
            generationMax = (generationMax + relationshipMax)

        elif -generationMax>len(relative_code):
            members = ex.searchFactory(str(self.id) + "-", 'Individuals', attributes=['indiv_pat_lineage'], searchFulltext=True,
                                       dictOut=True)
            for member in members:
                newName = 'a' * (-generationMax + 2)
                text = member['indiv_pat_lineage'].split('-')
                ex.updateFactory(member['individual_ID'], [text[0] + "-" + newName + text[1]], 'Individuals', ['indiv_pat_lineage'])
            relative_code=newName+relative_code
        

        connecting_rel_codes = []
        # generates connecting relative Codes for side Lineages
        for relationship in range(1, relationshipMax):
            connecting_rel_codes.append(relative_code[:-relationship])

        #generates missing relatives until the generation is met
        for generation in range(generationMax):
            if relationshipMax>0:
                letter = string.ascii_lowercase[string.ascii_lowercase.index(relative_code[-relationshipMax]) + 1]
                connecting_rel_codes.append(relative_code[:-relationshipMax] + letter + 'a' * (generation))

            elif generationMax>=0:
                connecting_rel_codes.append(relative_code+ 'a' * (generation+1))

            else:
                connecting_rel_codes.append(relative_code[:generation])

        #creates connecting relatives if they don't exist in Database
        if len(connecting_rel_codes)>1:
            for item in connecting_rel_codes[:-1]:
                code=str(self.id)+"-"+item
                if len(ex.searchFactory(code,'Individuals',attributes=['indiv_pat_lineage']))==0:
                    random=randint(1,50)
                    name=ex.getFactory(random,'Forname_Kosch_male',dictOut=True)['name']
                    newChar(name=name,family_Id=self.id,pat_lineage=code,unchecked=True)


        #chooses relevant owners code
        owner_code=None
        owner_code_pat=ex.getFactory(selbst_ID,'Individuals',dictOut=True)['indiv_pat_lineage']
        owner_code_mat=ex.getFactory(selbst_ID,'Individuals',dictOut=True)['indiv_mat_lineage']

        if owner_code_pat!= None and owner_code_pat.startswith(str(self.id)+"-"):
            owner_code=owner_code_pat
            owner_lineage='indiv_pat_lineage'
        elif owner_code_mat!= None and owner_code_mat.startswith(str(self.id)+"-"):
            owner_code=owner_code_mat
            owner_lineage='indiv_mat_lineage'
        elif owner_code_pat==None:
            owner_lineage = 'indiv_pat_lineage'
        elif owner_code_mat== None:
            owner_lineage = 'indiv_mat_lineage'

        #replaces owners space if there are descendants
        if owner_code!=None:
            if len(ex.searchFactory(owner_code,'Individuals',attributes=['indiv_pat_lineage'],searchFulltext=True))>1:
                if len(ex.searchFactory(owner_code,'Individuals',attributes=['indiv_pat_lineage']))==1:
                    random = randint(1, 50)
                    name = ex.getFactory(random, 'Forname_Kosch_male', dictOut=True)['name']
                    newChar(name=name, family_Id=self.id, pat_lineage=owner_code_pat,
                                         mat_lineage=owner_code_mat, unchecked=True)

        # updates owners Code, if there is already somebody with newcode, create brothers/sisters Code
        newCode=str(self.id)+"-"+connecting_rel_codes[-1]
        for letter in string.ascii_lowercase:
            newCode=newCode[:-1]+letter
            if len(ex.searchFactory(newCode,'Individuals',attributes=[owner_lineage]))>0:
                continue
            ex.updateFactory(selbst_ID,[newCode],'Individuals',[owner_lineage])
            break

        self.updateTree(self.id)


#lineage = ['a', 'aa', 'ab', 'ac', 'ad', 'aaa', 'aab', 'aba', 'ada', 'adb', 'adc', 'add', 'ade',
                  # 'aaaa', 'aaab', 'aaba']

lineage = {'a':'gerubald', 'aa':'joswean', 'ab':'jomain', 'ac':'Halfdur', 'ad':'Josmene', 'aaa':'Aldare', 'aab':'rundra', 'aba':'drala', 'ada':'Jomain', 'adb':'Galdor', 'adc':'Sandala', 'add':'handra', 'ade':'Golwena',
                   'aaaa':'Gnurrbold', 'aaab':'Olwin', 'aaba':'Jandrascha'}



App = QtWidgets.QApplication(sys.argv)
win = MyWindow2(list(lineage),lineage,'aba')
win.show()
App.exec_()
sys.exit()
