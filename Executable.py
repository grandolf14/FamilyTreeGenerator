#region import
from datetime import datetime, time, timedelta
from random import randint
import sqlite3

#endregion

# only for storing data, in use
class DataStore:
    """returns data while in use

    :param path: str
        the current database path
    """
    path='./DSA Daten.db'


#region Database Factories, access and manipulation

def newFactory(library: str, data: dict={}):
    """creates new entries with given data in given table within the library at DataStore.Path

    :param library: str
        name of table
    :param data: dict
        dictionary with columns as keys
    :return: ->int, the id of the newly created entry
    """

    conn = sqlite3.connect(DataStore.path)
    c = conn.cursor()
    c.execute("SELECT * FROM %s" % (library,))
    existing_col = [x[0] for x in c.description]

    listed_values = []
    len_list = ""
    for column in existing_col:
        if column in data:
            listed_values.append(data[column])
        else:
            listed_values.append(None)

        len_list += "?,"

    len_list=len_list.rstrip(',')
    c.execute("INSERT INTO %s VALUES (%s)" % (library, len_list), (*listed_values,))
    id = c.lastrowid
    conn.commit()
    conn.close()

    return id

def getRandom(library:str,path="./Setting Aventurien.db"):
    """

    :param library: str
        the tablename
    :param path: str, optional
        the database path
    :return: list, a random member of the database
    """

    conn=sqlite3.connect(path)
    c=conn.cursor()

    c.execute("""SELECT * FROM %s ORDER BY RANDOM()"""%(library))
    columns= c.description
    data=c.fetchone()
    return data

def searchFactory(text:str,library:str,innerJoin:str ="",output:str =None,  shortOut:bool= False ,
                  attributes:list=None ,Filter:dict={},OrderBy = None, searchFulltext:bool =False,
                  dictOut=False,uniqueID=True):

    """returns the sqlite database datasets

    :param text: str,
        the value/text to search for in database
    :param library: str
        the table to search in
    :param innerJoin: str, optional, sqlitesyntax
    :param output: str, optional, sqlitesyntax
    :param shortOut: bool, optional
        returns the saved profile matching the library
    :param attributes: list, optional
        specifies the list of columnnames to search the text in
    :param Filter: dict, optional
        specifies additional searchparameter
    :param OrderBy: str, optional, sqlitesyntax
    :param searchFulltext: bool, optional
        if yes searches as well if the given searchtext is a substring of the dataitems
    :param dictOut: bool, optional
        if yes returns the data as dict with the column names as keys
    :param uniqueID: bool, optional
        if no returns items several times, if searched in multiple attributes
    :return: ->list|dict , all datasets resembling the specified parameters
    """


    conn=sqlite3.connect(DataStore.path)
    c=conn.cursor()


    if type(text)!=str:
        text=str(text)

    if OrderBy == None:
        OrderBy= library+'.rowid'

    if searchFulltext:
        text = "%"+text+"%"


    if shortOut:

        shortOutputDict= {"Individuals":['individual_ID, indiv_fName, family_Name',
                                         'INNER JOIN Families on Families.family_ID = Individuals.fKey_family_ID'],
                          "Sessions":["Sessions.session_ID, session_Name",
                                      "LEFT JOIN Session_Individual_jnt on Sessions.session_ID= Session_Individual_jnt.fKey_session_ID "
                                      "LEFT JOIN Individuals on Individuals.individual_ID = Session_Individual_jnt.fKey_individual_ID"],
                          "Event_Individuals_jnt":["Individuals.individual_ID,Individuals.indiv_fName, Families.family_Name",
                                              """INNER JOIN Events on Events.event_ID = Event_Individuals_jnt.fKey_event_ID
                                              LEFT JOIN Sessions on Events.fKey_Session_ID = Sessions.session_ID
                                            RIGHT JOIN Individuals on Individuals.individual_ID = Event_Individuals_jnt.fKey_individual_ID
                                            LEFT JOIN Families on Individuals.fKey_family_ID= Families.family_ID"""],
                          "Session_Individual_jnt": ["Sessions.session_ID,session_Name",
                                                """INNER JOIN Sessions on Session_Individual_jnt.fKey_session_ID = Sessions.session_ID 
                                             INNER JOIN Individuals on Individuals.individual_ID = Session_Individual_jnt.fKey_individual_ID
                                             INNER JOIN Families on Individuals.fKey_family_ID= Families.family_ID"""],
                          "Events":["Events.event_ID,Events.event_Title",""],
                          "Notes":["Notes.note_ID,Notes.note_Content",""]}


        if not output:
            output=shortOutputDict[library][0]
        if not innerJoin:
            innerJoin= shortOutputDict[library][1]

    if not output:
        output = '*'
        if library.endswith("_Pathlib"):
            output = library+'.rowid,*'


    if not attributes:
        c.execute("""SELECT *  
                        FROM %s %s""" % ( library, innerJoin))
        attributes = [x[0] for x in c.description]

    elif type(attributes)==str:
        attributes=list(attributes)

    filterstring = ""
    filterTextList = []
    if Filter:
        for item in Filter:
            filterstring += " AND %s like ?" % (item)
            if Filter[item][1]:
                filterTextList.append("%"+Filter[item][0]+"%")
            else:
                filterTextList.append(Filter[item][0])
        if text=="" or None or '' or len(text)==0:
            filterstring=" WHERE "+filterstring[4:]



    a=1
    searchResult = []
    searchIndex = []

    for column in attributes:

        if text=="" or text==None or text=='' or len(text)==0:


            c.execute("""SELECT %s  FROM %s %s %s ORDER BY %s""" % (
            output, library, innerJoin, filterstring, OrderBy),
                      (*[*filterTextList],))
            data = c.fetchall()
            name = [x[0] for x in c.description]



            if uniqueID:
                data_collection = []
                Id_collection = []
                for index,datum in enumerate(data):
                    if datum[0] in Id_collection:
                        continue

                    data_collection.append(datum)
                    Id_collection.append(datum[0])
                data=data_collection

            if dictOut:
                searchResult={}
                for index,item in enumerate(name):
                    searchResult[item]=data[index]
            else:
                searchResult=data

            break

        if column== 'indiv_fName' and not searchFulltext:
            c.execute("""SELECT %s
                        FROM %s %s
                        WHERE %s like ?
                         or % s like ?
                         or % s like ?
                         or % s like ?
                         ORDER BY %s""" % (output, library, innerJoin, column, column, column, column, OrderBy),
                      (text,"% "+text,text+" %","% "+text+" %"))
            data = c.fetchall()

        else:

            c.execute("""SELECT %s  FROM %s %s WHERE %s like ? %s ORDER BY %s""" % (output, library, innerJoin, column, filterstring, OrderBy),
                (text,*[*filterTextList]))
            name=[x[0] for x in c.description]
            data = c.fetchall()


        for indexA,item in enumerate(data):
            if not dictOut:
                if item[0] not in searchIndex:
                    searchIndex.append(item[0])
                    searchResult.append(item)

            else:

                if item[0] not in searchIndex:
                    searchIndex.append(item[0])
                    searchResult.append({})
                    for indexB, Value in enumerate(item):
                        searchResult[indexA][name[indexB]] = Value






    return searchResult


def getFactory(id:int,library:str,output:str='*',defaultOutput:bool=False,shortOutput=False, dictOut=False, path=None):

    """returns the sqlite datum with matching id

    :param id: int
        id of searched datum
    :param library: str
        table name
    :param output: str, optional, sqlitesyntax
    :param defaultOutput: bool, optional
        returns the saved profile matching the library
    :param shortOutput: bool, optional
        returns the saved profile matching the library
    :param dictOut: bool, optional
        if yes returns the data as dict with the column names as keys
    :param path: str, optional
    :return: -> list|dict
    """
    defaultOutDict= {'Families':['*',''],
                        'Individuals':['*, family_Name','INNER JOIN Families on Families.family_ID = Individuals.fKey_family_ID']}

    shortOutDict = {'Families': ['family_ID,family_Name', ''],
                      'Individuals': ['Individuals.individual_ID, indiv_fName, family_Name',
                                      'INNER JOIN Families on Families.family_ID = Individuals.fKey_family_ID']}

    innerJoin=''
    if shortOutput and library in shortOutDict:
        output = shortOutDict[library][0]
        innerJoin = shortOutDict[library][1]

    if defaultOutput and library in defaultOutDict:
        output=defaultOutDict[library][0]
        innerJoin=defaultOutDict[library][1]

    if path==None:
        path=DataStore.path

    conn = sqlite3.connect(path)
    c=conn.cursor()

    c.execute("""SELECT %s FROM %s %s WHERE %s.rowid=(?)"""%(output,library,innerJoin,library),(id,))
    column = [x[0] for x in c.description]
    data=c.fetchone()

    c.close()

    if dictOut:
        dataDict = {}
        for index,item in enumerate(data):
            dataDict[column[index]]=item

        return dataDict
    else:
        return data

def updateFactory(id, texts:list,library:str,attributes:list, path=None):

    """updates the specified datasets attributes with given values

    :param id: str
        sqlite id of dataset
    :param texts: list
        list of values to update with
    :param library: str
        table name
    :param attributes:  list
        list of columns to update
    :param path: str, optional
        path of database
    :return:
    """
    if path==None:
        path=DataStore.path

    conn = sqlite3.connect(path)
    c = conn.cursor()
    str= ("""UPDATE %s 
          SET """)
    for index,attribute in enumerate(attributes):
        str+= " %s = (?) "
        if not index >= len(attributes)-1:
            str+=", "
        str+="""
        """
    str+= "WHERE rowid = (?) "

    c.execute(str %(library,*attributes),(*texts,id))
    conn.commit()
    conn.close()


#endregion Factories

