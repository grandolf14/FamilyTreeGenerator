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

class Family_Tree(QStackedWidget):
    """Provides the widget for showing a family tree and the methods to add or move new members

    """

    def __init__(self):
        """initializes the family tree widget

        """

        self.banner = QImage('./Graphic_Library/banner3.png')
        self.banner = self.banner.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.banner = QPixmap.fromImage(self.banner)

        self.firstTime = True

        super().__init__()

        # region Layout assignment
        self.cenWid = QWidget()
        self.lay = QGridLayout()
        self.lay.setColumnStretch(0, 85)
        self.lay.setColumnStretch(1, 7)
        self.lay.setColumnStretch(2, 7)
        self.cenWid.setLayout(self.lay)

        self.saveVal = QLabel('None')
        self.lay.addWidget(self.saveVal, 0, 0)
        self.saveVal.hide()

        label = QLabel('unnasigned:')
        self.lay.addWidget(label, 0, 1, 1, 2)

        self.unassigned_result = Resultbox()

        # if standardbutton for each result is pressed, saves the name of the Charakter in self.l_sel_Person and the ID in self.saveVal
        self.unassigned_result.setPref(standardbutton=lambda: self.l_sel_Person.setText(
            str(ex.getFactory(self.sender().page, 'individuals', shortOutput=True)[
                    1]) + " (unassigned)") or self.saveVal.setText(str(self.sender().page)), col=1,
                                       standardButtonVerticalAlignment=False)
        self.lay.addWidget(self.unassigned_result, 1, 1, 1, 2)

        label = QLabel('assigned:')
        self.lay.addWidget(label, 2, 1, 1, 2)

        self.QC_assigned = QComboBox()
        # when changed, saves the Character ID in SaveVal #TO DO change l_sel_Person
        self.QC_assigned.currentIndexChanged.connect(lambda: self.saveVal.setText(str(self.QC_assigned.currentData())))
        self.QC_assigned.addItem("zu verändernde Person auswählen")
        self.lay.addWidget(self.QC_assigned, 3, 1, 1, 2)

        self.l_sel_Person = QLabel('no person selected')
        self.lay.addWidget(self.l_sel_Person, 4, 1, 1, 2)

        label = QLabel('generation')
        self.lay.addWidget(label, 5, 1)

        self.LE_gen = QLineEdit()
        self.lay.addWidget(self.LE_gen, 5, 2)

        label = QLabel('relation')
        self.lay.addWidget(label, 6, 1)

        self.LE_rel = QLineEdit()
        self.lay.addWidget(self.LE_rel, 6, 2)

        self.QC_rel = QComboBox()
        self.QC_rel.addItem("nächster Verwandter")
        self.lay.addWidget(self.QC_rel, 7, 1, 1, 2)

        self.calculate = QPushButton('calculate')
        self.calculate.clicked.connect(lambda: self.calculateLineage())  # connect with update lineage
        self.lay.addWidget(self.calculate, 8, 1, 1, 2)

        # endregion
        self.updateTreeGraph(None)

    def updateTreeGraph(self, id: int):
        """recalculates the graphical depiction of the family tree

        :param id: int
            id of depicted family
        :return: None
        """

        # resets manipulation area
        self.saveVal.setText(None)
        self.QC_rel.clear()
        self.QC_assigned.clear()
        self.QC_assigned.addItem("zu verändernde Person auswählen")
        self.QC_rel.addItem("nächster Verwandter")
        self.l_sel_Person.setText('no person selected')

        # global Variable assignment
        self.id = id

        # setting up scene and View
        self.scene = QGraphicsScene(0, 0, 2000, 2000)
        background = QPixmap('./Graphic_Library/Background Pergament.jpg')
        self.scene.setBackgroundBrush(QBrush(background))

        view = QGraphicsView(self.scene)
        view.setRenderHint(QPainter.Antialiasing)
        self.lay.addWidget(view, 0, 0, 9, 1)

        # retrieves Datasets for all family members from Database
        data = ex.searchFactory(id, 'Individuals', attributes=['fKey_family_ID'], dictOut=True)

        # gateKeeper, empties unassigned result if no Character with family id==id is found
        if len(data) == 0:
            self.unassigned_result.resultUpdate([])
            self.addWidget(self.cenWid)
            self.setCurrentWidget(self.cenWid)
            return

        # splits family members into already included in Family Tree and not included, sets up dictionary for included with lineage-Code as ID
        self.lineage_Infos = {}
        unsorted = []
        sortedRes = []

        for item in data:

            if item['indiv_pat_lineage'] == None:
                unsorted.append((item['individual_ID'], item['indiv_fName']))
                continue

            if item['indiv_pat_lineage'].startswith(str(id)):
                item_family_pos = item['indiv_pat_lineage'].split('-')[1]
                self.lineage_Infos[item_family_pos] = item
                sortedRes.append((item['individual_ID'], item['indiv_fName']))

        # gateKeeper, garantuees that at least one Character has a lineage code
        if self.noCharSet(sortedRes,unsorted):
            self.updateTreeGraph(self.id)
            return

        # LayoutUpdate: adds owners (sortedRes Items) to Layout Combobox and ResultBox
        for item in sortedRes:
            text = item[1]
            char = ex.getFactory(item[0], 'Individuals', dictOut=True)
            if char['indiv_rel_id'] != None:
                text += " (" + ex.getFactory(char['indiv_rel_id'], 'Individuals', dictOut=True)['indiv_fName'] + ")"

            self.QC_assigned.addItem(text, item[0])
            self.QC_rel.addItem(text, item[0])

        self.unassigned_result.resultUpdate(unsorted)

        # gateKeeper if there are no items for the calculation return # TO DO remove?
        if len(self.lineage_Infos) == 0:
            self.addWidget(self.cenWid)
            self.setCurrentWidget(self.cenWid)
            return


        newlineage, lineage_keys, lineage_SOKeys=self.calcGenGraph()
        
        # calculate tree width and tree height
        height = (len(sorted(lineage_keys, key=len)[-1].rstrip('z')) - len(sorted(lineage_keys, key=len)[0])) * 140 + 40
        width = len(newlineage[-1]) * 150 + 40
        x = 1000 - int(width / 2) + 70
        y = 1000 - int(height / 2)

        # if scene >2000
        if height > 2000 or width > 2000:
            self.scene.setSceneRect(x - 100, y - 100, width + 200, height + 200)
        
        posDict=self.graph_CalcPos(newlineage, lineage_keys, lineage_SOKeys, y)
            
        # draws labels
        for item in lineage_keys:
            labelback = QLabel()
            labelback.setPixmap(self.banner)
            labelback.setStyleSheet('background-color: transparent')
            labelback.setGeometry(x + posDict[item][0] - 35, posDict[item][1] - 58, 120, 120)
            self.scene.addWidget(labelback)

            label = QLabel(self.lineage_Infos[item]['indiv_fName'])
            label.setAlignment(Qt.AlignLeft)
            label.setAlignment(Qt.AlignVCenter)
            size = label.fontMetrics().boundingRect(label.text())
            label.setGeometry(x + posDict[item][0] + 25 - +int(size.width() / 2), posDict[item][1], size.width(),
                              size.height())
            label.setStyleSheet('background-color: transparent')
            self.scene.addWidget(label)

            label = QLabel(self.lineage_Infos[item]['indiv_pat_lineage'])
            label.setAlignment(Qt.AlignLeft)
            label.setAlignment(Qt.AlignVCenter)
            size = label.fontMetrics().boundingRect(label.text())
            label.setGeometry(x + posDict[item][0] + 25 - +int(size.width() / 2), posDict[item][1] + 15, size.width(),
                              size.height())
            label.setStyleSheet('background-color: transparent')
            self.scene.addWidget(label)
        
        # draws connecting lines
        for item in lineage_keys:
            name = item[:-1]

            if item.endswith("z"):

                if item.rstrip("z") + "a" in posDict:

                    # horizontal connecting SO-Member
                    self.scene.addLine(posDict[item][0] + x + 25, posDict[item][1] + 70, posDict[name][0] + x + 25,
                                       posDict[name][1] + 70, QPen(Qt.black, 2, Qt.SolidLine))

                    # vertical from bottom SO item down
                    self.scene.addLine(posDict[item][0] + x + 25, posDict[item][1] + 54, posDict[item][0] + x + 25,
                                       posDict[item][1] + 70, QPen(Qt.black, 2, Qt.SolidLine))

                    # vertical from Member down
                    self.scene.addLine(posDict[name][0] + x + 25, posDict[name][1] + 54, posDict[name][0] + x + 25,
                                       posDict[name][1] + 70, QPen(Qt.black, 2, Qt.SolidLine))

                    # vertical connecting mother_father line and children
                    self.scene.addLine((posDict[name][0] + posDict[item][0]) // 2 + x + 25, posDict[name][1] + 71,
                                       (posDict[name][0] + posDict[item][0]) // 2 + x + 25,
                                       posDict[name][1] + 112, QPen(Qt.black, 2, Qt.SolidLine))

                else:
                    # connecting married without children
                    self.scene.addLine(posDict[item][0] + x - 15, posDict[item][1] + 25, posDict[name][0] + x + 73,
                                       posDict[name][1] + 25, QPen(Qt.black, 2, Qt.SolidLine))

            elif name in posDict and name != "":

                # vertical from member up
                self.scene.addLine(posDict[item][0] + x + 25, posDict[item][1] - 10, posDict[item][0] + x + 25,
                                   posDict[item][1] - 26, QPen(Qt.black, 2, Qt.SolidLine))

            # horizontale verbindung zwischen Geschwistern
            if item == name + 'a' and name in posDict:

                left = posDict[item]
                right = 0
                for index, letter in enumerate(string.ascii_lowercase):
                    if name + letter not in posDict:
                        break

                if not index == 1:
                    right = posDict[name + string.ascii_lowercase[index - 1]]

                else:
                    if name + "z" in posDict:
                        right = ((posDict[name][0] + posDict[name + "z"][0]) // 2, left[1])

                if right:
                    self.scene.addLine(left[0] + x + 25, left[1] - 26, right[0] + x + 25,
                                       right[1] - 26, QPen(Qt.black, 2, Qt.SolidLine))

        self.addWidget(self.cenWid)
        self.setCurrentWidget(self.cenWid)

        factor = min(view.size().width() / width, view.size().height() / height)
        newWidth = min(max(view.size().width() / factor, view.size().width() // 1.5), view.size().width())
        newHeight = min(max(view.size().height() / factor, view.size().height() // 1.5), view.size().height())
        view.fitInView(
            QtCore.QRectF(1000 - int(newWidth / 2), 1000 - int(newHeight / 2), int(newWidth), int(newHeight)))

    def graph_CalcPos(self, newlineage, lineage_keys, lineage_SOKeys, y):
        """calculates the graphical positiion of each tree member

        :param newlineage: list
            the list of generations for graphical Layout
        :param lineage_keys: list
            the key-list of all tree members
        :param lineage_SOKeys: list
             the key list of all significant others
        :param y: y
        :return: -> dict, dictionary with the graphical position for each tree member
        """
        posDict = {}
        for index, item in enumerate(newlineage[- 1]):
            name = item
            xPos = (index) * 150

            if name not in posDict:
                posDict[name] = xPos

        # calculates other generation
        for gen_index in reversed(range(len(newlineage[:-1]))):

            for name in newlineage[gen_index]:

                if not name.endswith("z"):

                    children = []
                    for item in newlineage[gen_index + 1]:
                        if item.startswith(name):
                            children.append(item)

                    if len(children) <= 2:
                        if name + "a" in children:
                            posDict[name] = posDict[name + "a"]
                        else:
                            posDict[name] = posDict[name + "z"]
                    else:
                        minimum = min([posDict[x] for x in children if x in posDict])
                        maximum = max([posDict[x] for x in children if x in posDict])
                        posDict[name] = (minimum + maximum) // 2 - 75

        SOposDict = {}
        for item in posDict:

            if item + "z" in lineage_SOKeys:
                SOposDict[item + "z"] = [posDict[item] + 150,
                                         y + (int(len(item) - len(lineage_keys[0])) * 140 - 60)]

                posDict[item] = [posDict[item],
                                 y + (int(len(item) - len(lineage_keys[0])) * 140 - 60)]

            else:
                posDict[item] = [posDict[item],
                                 y + (int(len(item) - len(lineage_keys[0])) * 140 - 60)]

        for item in SOposDict:
            posDict[item] = SOposDict[item]
            
        return posDict

    def calculateLineage(self):

        """ calculates the new family tree and updates all set members

        :return: ->None
        """

        # checks userinput for wrong/incomplete Input, sets generationMax, relationshipMax, Verwandter_ID, selbst_ID
        if self.LE_gen.text() == None or self.LE_rel.text() == None or self.QC_rel.currentIndex() == 0 or self.saveVal.text() == None:
            msg = QMessageBox()
            msg.setText('pls fill out values')
            msg.exec()
            return


        generationMax = int(self.LE_gen.text())
        relationshipMax = int(self.LE_rel.text())
        verwandter_ID = self.QC_rel.currentData()
        selbst_ID = int(self.saveVal.text())

        # gatekeeper, checks for wrong Input
        if verwandter_ID == selbst_ID:
            msg = QMessageBox()
            msg.setText('identical relative and self')
            msg.exec()
            return

        # Gatekeeper, checks for wrong Input
        if generationMax == 0 and relationshipMax == 0:
            msg = QMessageBox()
            msg.setText('identical relative position and self position')
            msg.exec()
            return

        # gets relative_Code
        relative_code_get = ex.getFactory(verwandter_ID, 'individuals', dictOut=True)

        relative_code_raw = relative_code_get['indiv_pat_lineage']
        relative_code = relative_code_get['indiv_pat_lineage'].split('-')[1]

        # updates relative_codes of all lineage members if code does not allow the manipulation (for example code aaa
        # needs to be prolonged if you want to have the Grand-Grandparent of aaa)
        if relationshipMax > 0:
            if relationshipMax + 1 > len(relative_code):
                members = ex.searchFactory(str(self.id) + "-", 'Individuals', attributes=['indiv_pat_lineage'],
                                           searchFulltext=True, dictOut=True)
                for member in members:
                    newName = 'a' * (relationshipMax + 2)
                    text = member['indiv_pat_lineage'].split('-')
                    ex.updateFactory(member['individual_ID'], [text[0] + "-" + newName + text[1]], 'Individuals',
                                     ['indiv_pat_lineage'])
                relative_code = newName + relative_code
            generationMax = (generationMax + relationshipMax)

        elif -generationMax + 1 > len(relative_code):
            members = ex.searchFactory(str(self.id) + "-", 'Individuals', attributes=['indiv_pat_lineage'],
                                       searchFulltext=True,
                                       dictOut=True)
            for member in members:
                newName = 'a' * (-generationMax + 2)
                text = member['indiv_pat_lineage'].split('-')
                ex.updateFactory(member['individual_ID'], [text[0] + "-" + newName + text[1]], 'Individuals',
                                 ['indiv_pat_lineage'])
            relative_code = newName + relative_code

        connecting_rel_codes = []

        # generates connecting relative Codes for side Lineages
        for relationship in range(1, relationshipMax + 1):
            connecting_rel_codes.append(relative_code[:-relationship])

        # generates missing relatives until the generation is met
        if generationMax < 0:
            gen_Index = reversed(range(generationMax, 0))
        else:
            gen_Index = range(generationMax)

        for generation in gen_Index:
            if relationshipMax > 0:
                letter = string.ascii_lowercase[string.ascii_lowercase.index(relative_code[-relationshipMax]) + 1]
                connecting_rel_codes.append(relative_code[:-relationshipMax] + letter + 'a' * (generation))
                continue

            if generationMax >= 0:
                connecting_rel_codes.append(relative_code + 'a' * (generation + 1))
                continue

            connecting_rel_codes.append(relative_code[:generation])

        # creates connecting relatives if they don't exist in Database and adds new Significant other if there is none
        if len(connecting_rel_codes) > 1:
            for item in connecting_rel_codes[:-1]:
                code = str(self.id) + "-" + item
                id = ex.searchFactory(code, 'Individuals', attributes=['indiv_pat_lineage'])
                if len(id) == 0:
                    random = randint(0, 1)
                    if random:
                        sex = "male"
                    else:
                        sex = "female"
                    name = ex.getRandom('Forname_Kosch_' + sex)[0]
                    id = ex.newFactory("Individuals",
                                       {"indiv_fName": name, "indiv_pat_lineage": code, "fKey_family_ID": self.id,
                                        "indiv_sex": sex, "unchecked": True})

                if ex.getFactory(id, 'Individuals', dictOut=True)["indiv_rel_id"] == None:
                    if ex.getFactory(id, 'Individuals', dictOut=True)["indiv_sex"] == "male":
                        sex_SO = "female"
                    else:
                        sex_SO = "male"
                    name = ex.getRandom('Forname_Kosch_' + sex_SO)[0]
                    id2 = ex.newFactory("Individuals", {"indiv_fName": name, "fKey_family_ID": 1, "unchecked": True,
                                                        "indiv_sex": sex_SO, "indiv_rel_id": id})
                    ex.updateFactory(id, [str(id2)], "Individuals", ['indiv_rel_id'])

        # chooses relevant owners code
        owner_code = None
        owner_code_pat = ex.getFactory(selbst_ID, 'Individuals', dictOut=True)['indiv_pat_lineage']
        owner_code_mat = ex.getFactory(selbst_ID, 'Individuals', dictOut=True)['indiv_mat_lineage']

        if owner_code_pat != None and owner_code_pat.startswith(str(self.id) + "-"):
            owner_code = owner_code_pat
            owner_lineage = 'indiv_pat_lineage'
        elif owner_code_pat == None:
            owner_lineage = 'indiv_pat_lineage'

        # replaces owners space if there are descendants
        rename_siblings = True
        changeChildren = []
        if owner_code != None:
            if len(ex.searchFactory(owner_code + "a", 'Individuals', attributes=['indiv_pat_lineage'])) > 0:
                self.dialog = QDialog()
                lay = QVBoxLayout()
                self.dialog.setLayout(lay)

                label = QLabel('do you want to take the descendants with you?')
                lay.addWidget(label)

                dialogbutton = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
                dialogbutton.accepted.connect(self.dialog.accept)
                dialogbutton.rejected.connect(self.dialog.reject)
                lay.addWidget(dialogbutton)

                if self.dialog.exec_():
                    changeChildren = ex.searchFactory(owner_code, 'Individuals', attributes=['indiv_pat_lineage'],
                                                      searchFulltext=True, dictOut=True)

                else:

                    if len(ex.searchFactory(owner_code, 'Individuals', attributes=['indiv_pat_lineage'])) == 1:
                        sex = ex.searchFactory(owner_code, 'Individuals', attributes=['indiv_pat_lineage'])[0][
                            "indiv_sex"]
                        name = ex.getRandom("Forname_Kosch_" + sex)
                        parent_id = ex.newFactory("Individuals", {"indiv_fName": name, "fKey_family_ID": self.id,
                                                                  "indiv_pat_lineage": owner_code_pat,
                                                                  "indiv_mat_lineage": owner_code_mat,
                                                                  "unchecked": True})
                        if sex == "male":
                            sex_SO = "female"
                        else:
                            sex_SO = "male"
                        name = ex.getRandom('Forname_Kosch_' + sex_SO)[0]
                        id2 = ex.newFactory("Individuals", {"indiv_fName": name, "fKey_family_ID": 1,
                                                            "indiv_rel_id": parent_id, "indiv_sex": sex_SO,
                                                            "unchecked": True})
                        ex.updateFactory(parent_id, [str(id2)], "Individuals", ['indiv_rel_id'])
                        rename_siblings = False

        # updates owners Code, if there is already somebody with newcode, create brothers/sisters Code
        newCode = str(self.id) + "-" + connecting_rel_codes[-1]

        for letter in string.ascii_lowercase[string.ascii_lowercase.index(connecting_rel_codes[-1][-1]):-1]:
            newSiblingCode = newCode[:-1] + letter
            sibling = ex.searchFactory(newSiblingCode, 'Individuals',
                                       attributes=['indiv_pat_lineage', 'indiv_mat_lineage'], dictOut=True)
            if len(sibling) > 0:
                continue

            descendants = ex.searchFactory(newCode + "a", 'Individuals', dictOut=True)
            if str(self.id) + "-" + connecting_rel_codes[-1] != newSiblingCode and len(descendants) > 0 and len(
                    changeChildren) == 0:
                self.dialog = QDialog()
                self.dialog_lay = QVBoxLayout()
                self.dialog.setLayout(self.dialog_lay)

                label = QLabel("""new member space is already inhabited in lineage.\n Should the new member replace the spaces old inhabitant?\n 
                            If so the spaces old inhabitant will be moved to be a sibling, if not the new member will be a sibling of the spaces old inhabitant""")
                self.dialog_lay.addWidget(label)

                dialogbutton = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
                dialogbutton.accepted.connect(self.dialog.accept)
                dialogbutton.rejected.connect(self.dialog.reject)
                self.dialog_lay.addWidget(dialogbutton)

                if self.dialog.exec_():
                    self.dialog.close()
                    oldOwner_id = ex.searchFactory(newCode, 'Individuals', attributes=[owner_lineage], dictOut=True)[0][
                        'individual_ID']
                    ex.updateFactory(oldOwner_id, [newSiblingCode], 'Individuals', [owner_lineage])
                    ex.updateFactory(selbst_ID, [newCode], 'Individuals', [owner_lineage])
                    break

            ex.updateFactory(selbst_ID, [newSiblingCode], 'Individuals', [owner_lineage])
            newCode = newSiblingCode
            break

        # updates children of owner if needed:
        if changeChildren:
            for item in changeChildren:
                ex.updateFactory(item['individual_ID'], [newCode + item['indiv_pat_lineage'].removeprefix(owner_code)],
                                 'Individuals', ['indiv_pat_lineage'])

        # updates right siblings pat_lineage
        if owner_code_pat != None and rename_siblings:
            last_letter = owner_code_pat[-1]
            for letter in string.ascii_lowercase[string.ascii_lowercase.index(last_letter) + 1:-1]:
                newPrefix = owner_code_pat[:-1] + last_letter
                oldPrefix = owner_code_pat[:-1] + letter
                sibling_pat = ex.searchFactory(oldPrefix, 'Individuals', attributes=['indiv_pat_lineage'],
                                               searchFulltext=True, dictOut=True)
                if len(sibling_pat) > 0:
                    for item in sibling_pat:
                        ex.updateFactory(item['individual_ID'],
                                         [newPrefix + item['indiv_pat_lineage'].removeprefix(oldPrefix)], 'Individuals',
                                         ['indiv_pat_lineage'])

                    last_letter = letter
                    continue
                break

        # updates right siblings mat_lineage !!!! does not work properly!!!!
        if owner_code_mat != None and rename_siblings:
            last_letter = owner_code_mat[-1]
            for letter in string.ascii_lowercase[string.ascii_lowercase.index(last_letter) + 1:-1]:
                newPrefix = owner_code_mat[:-1] + last_letter
                oldPrefix = owner_code_mat[:-1] + letter
                sibling_mat = ex.searchFactory(oldPrefix, 'Individuals', attributes=['indiv_mat_lineage'],
                                               searchFulltext=True, dictOut=True)
                print(sibling_mat)
                if len(sibling_mat) > 0:
                    ex.updateFactory(sibling_mat[0][0], [newPrefix], 'Individuals', ['indiv_mat_lineage'])
                    last_letter = letter
                    continue
                break

        # checks owner for descendants, if yes adds significant other if needed
        selbst = ex.getFactory(selbst_ID, 'Individuals', dictOut=True)
        if selbst['indiv_rel_id'] == None:
            owner_check_descendants = ex.searchFactory(newCode + "a", 'Individuals',
                                                       attributes=['indiv_pat_lineage', 'indiv_mat_lineage'])
            if len(owner_check_descendants) > 0:
                if selbst["indiv_sex"] == "male":
                    sex_SO = "female"
                else:
                    sex_SO = "male"
                name = ex.getRandom("Forname_Kosch_" + sex_SO)[0]
                id2 = ex.newFactory("Individuals", {"indiv_fName": name, "fKey_family_ID": 1,
                                                    "indiv_rel_id": selbst_ID,
                                                    "indiv_sex": sex_SO,
                                                    "unchecked": True})
                ex.updateFactory(selbst_ID, [str(id2)], "Individuals", ['indiv_rel_id'])

        # checks relevant relative for descendants, if yes adds significant other if needed
        relative = ex.getFactory(verwandter_ID, 'Individuals', dictOut=True)
        if relative['indiv_rel_id'] == None:
            relative_check_descendants = ex.searchFactory(relative_code_raw + "a", 'Individuals',
                                                          attributes=['indiv_pat_lineage', 'indiv_mat_lineage'])
            if len(relative_check_descendants) > 0:
                if selbst["indiv_sex"] == "male":
                    sex_SO = "female"
                else:
                    sex_SO = "male"
                name = ex.getRandom("Forname_Kosch_" + sex_SO)[0]
                id2 = ex.newFactory("Individuals", {"indiv_fName": name, "fKey_family_ID": 1,
                                                    "indiv_rel_id": selbst_ID,
                                                    "indiv_sex": sex_SO,
                                                    "unchecked": True})
                ex.updateFactory(verwandter_ID, [str(id2)], "Individuals", ['indiv_rel_id'])

        # updates owner mat_lineage
        parent = ex.searchFactory(newCode[:-1], 'Individuals', attributes=['indiv_pat_lineage'], dictOut=True)
        if parent != []:
            SO_pat_lineage = ex.getFactory(int(parent[0]['indiv_rel_id']), 'Individuals', dictOut=True)
            mat_lineage_code = None
            if SO_pat_lineage['indiv_pat_lineage'] != None:
                mat_lineage_code = SO_pat_lineage['indiv_pat_lineage'] + newCode[-1]

            ex.updateFactory(selbst_ID, [mat_lineage_code], 'Individuals', ['indiv_mat_lineage'])

        self.updateTreeGraph(self.id)
    def noCharSet(self,sortedRes,unsorted):
        """checks if there is any character with lineage code in family and provides one if necessary

        :param sortedRes: list of character Dictionaries
        :param unsorted: list of character Dictionaries
        :return: -> bool, True if there was no individual with lineage code in family
        """
        # creates first lineage code, if none of the family members has a lineage code
        if len(sortedRes) == 0 and len(unsorted) > 0:
            anchorItem = ex.getFactory(unsorted[0][0], 'Individuals', dictOut=True)
            if anchorItem['indiv_pat_lineage'] == None:
                ex.updateFactory(anchorItem['individual_ID'], [str(self.id) + '-aaa'], 'Individuals',
                                 attributes=['indiv_pat_lineage'])
            else:
                ex.updateFactory(anchorItem['individual_ID'], [str(self.id) + '-aaa'], 'Individuals',
                                 attributes=['indiv_mat_lineage'])
            return True

        return False
    def calcGenGraph(self):
        """calculates the generations for graphical layout

        :return: newlineage: list, lineage_keys: list, lineage_SOKeys: list
        """

        # region calculates generations
        lineage_keys = sorted(sorted(list(self.lineage_Infos)), key=len)
        lineage_SOKeys = []
        newlineage = []

        # starts with the last generation, any member[item] of the lineage keys will be added to newlineage[generation] if:
        # -there is only 1 descendant in the last generation[ie bbb is a descendant from bb], descendants start with
        #       member_key[item],are not the member and are maximum part of the relevant generation
        # -it is not part of any later generations [len(item)<=round+1]

        for round in range(len(lineage_keys[-1])):
            newlineage.append([])
            for index, item in enumerate(lineage_keys):
                marker = False
                for index2, item2 in enumerate(lineage_keys):

                    if round > 12:
                        print(item, item2, item2.startswith(item) and index != index2 and len(item2) <= round + 1)
                    if item2.startswith(item) and index != index2 and len(item2) <= round + 1:
                        if marker:
                            break
                        marker = True

                else:

                    if len(item) > round + 1:
                        continue

                    # adds SO, adds 1 filler, if needed
                    if not marker and len(item) == round + 1:
                        newlineage[round].append(item)

                        if self.lineage_Infos[item]['indiv_rel_id'] != None:
                            newlineage[round].append(item + "z")
                            lineage_SOKeys.append(item + "z")
                            self.lineage_Infos[item + "z"] = ex.getFactory(self.lineage_Infos[item]['indiv_rel_id'],
                                                                      'Individuals',
                                                                      dictOut=True)
                        elif marker or item[:-1] in lineage_keys and self.lineage_Infos[item[:-1]][
                            'indiv_rel_id'] != None and item[:-1] + "b" not in lineage_keys:
                            newlineage[round].append(item[:-1] + "z")

                    # adds filler [wenn der Vater keinen 2. Sohn hat und der Sohn keine Partnerin hat
                    if not marker and len(item) < round + 1:
                        newlineage[round].append(item + "z")

                        if not item[:-1] + "b" in lineage_keys or self.lineage_Infos[item]['indiv_rel_id'] != None:
                            newlineage[round].append(item + "z")

        lineage_keys = lineage_keys + lineage_SOKeys
        for index, generation in enumerate(newlineage):
            newlineage[index] = sorted(generation)

        return newlineage, lineage_keys, lineage_SOKeys

class Resultbox(QStackedWidget):
    """
    Widget for dynamic display of data lists with buttons for data manipulation.

    Methods
    -------
     setPref(self, reloadBottom=False, paintItemFrame=False, buttonList=None, spacer=True, paintLight:list=[None], standardbutton=None,standardButtonVerticalAlignment=True, ignoreIndex=[0], spacing=10, col=4)
        defines the preferences for this Resultbox

    resultUpdate(self, manualResult=None)
        displays new Content for given data list
    """

    def __init__(self):
        super().__init__()
        self.setPref()
        self.source = None
        self.resultUpdate()

    def setPref(self, reloadBottom=False, paintItemFrame=False, buttonList=None, spacer=True, paintLight:list=[None], standardbutton=None,standardButtonVerticalAlignment=True, ignoreIndex=[0], spacing=10, col=4):
        """ sets the preferences for the specific Resultbox

        :param reloadBottom: Bool, optional
                reloads the Resultbox scroll widget bottom
        :param paintItemFrame: Bool, optional
                adds a frame for each dataset
        :param buttonList: list of [buttonName, function without parenthesis], optional
                adds specified Buttons for each dataset, self.sender().page = item[0] of dataset
        :param spacer: Bool, optional
                adds spaceritems between the single datasets
        :param paintLight: List of int
                specifies which index of the Dataset should be painted in light grey
        :param standardbutton: function without parenthesis, optional
                defines which function to call when the button gets pressed
        :param standardButtonVerticalAlignment: Bool, optional
                align the contents in the button vertical [True] or horizontal [False]
        :param ignoreIndex: list of int, optional
                do not display the contents of each dataset with chosen index
        :param spacing: int, optional
                defines spacing span
        :param col: int, optional
                how many columns should the Resultbox have
        :return: -> None
        """

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
        """repaints the resultbox with given data as content

        :param manualResult: list of datasets, optional
            the content of the Resultbox
        :return: ->None
        """


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
    """provides the main window for the application

    """
    def __init__(self):

        """initializes the main-window layout

        """
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
        """searches the database for families with given string

        :param text: str
        :return: -> None
        """

        data=ex.searchFactory(text,'Families',attributes=['family_Name'],searchFulltext=True)

        if len(data)>1:
            dialog=QDialog()
            lay=QVBoxLayout()
            dialog.setLayout(lay)
            self.selectedID = -1
            for item in data:
                button=QPushButton(item[1])
                button.page=item[0]
                button.clicked.connect(lambda: self.tree.updateTreeGraph(self.sender().page))
                button.clicked.connect(dialog.close)
                lay.addWidget(button)

            dialog.exec_()
        else:
            self.tree.updateTreeGraph(data[0][0])


def newChar(name, family=None, title =None , tags = None, notes= None, unchecked = False, family_Id = None,
            newFamily = False, pat_lineage=None, mat_lineage=None,rel_id=None, sex = None):

    """inserts a new Char into the database

    :param name: str
    :param family: int, optional
        if you want to search any family by name
    :param title: str, optional
    :param tags: str, optional
    :param notes: str, optional
    :param unchecked: Bool, optional
    :param family_Id: int, optional
    :param newFamily: bool, optional
    :param pat_lineage: str, optional
    :param mat_lineage: str, optional
    :param rel_id: int, optional
    :param sex: str, optional

    :return: -> id [int]
    """

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


    c.execute("INSERT INTO Individuals VALUES (?,?,?,?,?,?,?,?,?,?,?) ", (None,name,family_Id,title, tags, notes, unchecked, pat_lineage, mat_lineage,rel_id,sex))
    id=c.lastrowid
    conn.commit()

    conn.close()
    return id


App = QtWidgets.QApplication(sys.argv)
win = MyWindow()
win.show()
App.exec_()
sys.exit()
