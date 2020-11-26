#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thur Oct 10 12:45:56 2019
@author: Andres Vodopivec

USE:
This is a standalone file.
To use type:
python GROmaker.py xx.gro yy.gro zz.gro
xx.gro, yy.gro and zz.gro can be any gro file format.
Also you can concatenate from 2 to infinite files together (three is just for example).
If the gro files do not comply GMX format exactly, this program will give you error.

The only variables to modify are in the 'INPUT VARAIBLES' section.

"""
# ==================================================================================================
# LOADING MODULES
# ==================================================================================================
import os
import sys
import traceback

# ==================================================================================================
# INPUT VARAIBLES
# ==================================================================================================

groConcatName = "comb_out.gro"  # output file name from this python program
extraDistZ = 8  # Addtional distance to leave between the last molecule and the box wall in the
# +Z direction

# ==================================================================================================
# CLASSES REQUIRED
# ==================================================================================================

# --------------------------------------------------------------------------------------------------
# FileUtil class
# --------------------------------------------------------------------------------------------------


class FileUtil():
    """ FileUtil is a class to read and wrtie files ONLY """

    def __init__(self, file):
        """This is the Constructor to instanciate the object for FileUtil() class """
        self.file = file

    @classmethod
    def FileReader(cls, destinationFilePath, fileName):
        """FileUtil.FileReader is a Constructor that takes a path
        (/destinationFilePath/fileName) to instanciste the object. """

        # Chechiing that all arguments given to the func are strings.
        if not isinstance(destinationFilePath, str) and not isinstance(fileName, str):
            raise ValueError('all arguments for FuncForGMX.FileWriter() must be strings')

        print('\nReading new file with name ' + fileName +
              ' in directory: ' + destinationFilePath + '\n')
        filepath = os.path.join(destinationFilePath, fileName)
        fileList = []

        if not os.path.exists(filepath):
            raise FileNotFoundError('The file ' + fileName + ' in directory: ' +
                                    destinationFilePath + ' was not found.')

        else:
            with open(filepath, 'r') as fin:
                fileList = fin.readlines()

        return cls(fileList)

    def FileWriter(self, destinationFilePath, fileName):
        """FileUtil.FileWriter is an instance method that print a object to
        /destinationFilePath/fileName. """
        args = locals()  # locals() is a function to get the arguments of a
        # function. The output is a diccionary.

        for i in args:
            # Chechiing that all arguments given to the func are strings.
            if not isinstance(destinationFilePath, str) and not isinstance(fileName, str):
                raise ValueError('all arguments for FuncForGMX.FileWriter() must be strings')

        print('\nWriting the new file with name ' + fileName +
              ' in directory: ' + destinationFilePath + '\n')
        filepath = os.path.join(destinationFilePath, fileName)

        if not os.path.exists(destinationFilePath):
            raise FileNotFoundError('The directory: ' + destinationFilePath + ' was not found.')

        else:
            with open(filepath, 'w') as fout:
                fout.writelines(self.file)

        return None

    @classmethod
    def fromGROreaderToFileUtil(cls, groFileObject):

        print('\nCreating the new gro file list as FileUtil Object\n')
        gro_format = '%5d%-5s%5s%5d%8.3f%8.3f%8.3f\n'
        box_dim_format = '%10.5f%10.5f%10.5f\n'
        totalSystemAtoms = groFileObject.totalSystemAtoms
        residNum = groFileObject.residNum
        residType = groFileObject.residType
        atomType = groFileObject.atomType
        atomNum = groFileObject.atomNum
        xCoord = groFileObject.xCoord
        yCoord = groFileObject.yCoord
        zCoord = groFileObject.zCoord
        xDim = groFileObject.xDim
        yDim = groFileObject.yDim
        zDim = groFileObject.zDim

        fileList = []
        fileList.append(
            'This is a box printed by FileUtil class (created by AVK on Feb 27, 2019)\n')
        fileList.append('{}\n'.format(str(totalSystemAtoms)))

        for i in range(0, len(residNum)):
            stringToAdd = gro_format % (
                residNum[i], residType[i], atomType[i], atomNum[i], xCoord[i], yCoord[i], zCoord[i])
            fileList.append(stringToAdd)

        fileList.append(box_dim_format % (xDim, yDim, zDim))

        return cls(fileList)

    def __del__(self):
        print("freeing memory by deleting FileUtil object")
        # This is my destructor (it is not mandatory for python)

# --------------------------------------------------------------------------------------------------
# GROreader class
# --------------------------------------------------------------------------------------------------


class GROreader():
    """ GROreader class is a class to process and create .gro file objects from a list ONLY """

    def __init__(self, totalSystemAtoms, residNum, residType, atomType, atomNum, xCoord, yCoord,
                 zCoord, xDim, yDim, zDim):
        """This is the Constructor to instanciate the object for GROreader() class"""
        self.totalSystemAtoms = totalSystemAtoms
        self.residNum = residNum
        self.residType = residType
        self.atomType = atomType
        self.atomNum = atomNum
        self.xCoord = xCoord
        self.yCoord = yCoord
        self.zCoord = zCoord
        self.xDim = xDim
        self.yDim = yDim
        self.zDim = zDim

    @classmethod
    def fromList_GROreader(cls, grofile):
        """ fromList_GROreader is a Constructor that takes the gro file as the argument.
        The grofile must be a list type.
        Example how to use it:
            myGro = GROreader.fromList_GROreader(grofile)
            print(myGro.yDim)  # in case you want to print content
        """

        if isinstance(grofile, list):
            pass
            if all([isinstance(element, str) for element in grofile]):
                pass
            else:
                raise ValueError(
                    'Argument in GROreader.fromList_GROreader() is not a list of strings')
        else:
            raise ValueError('Argument in GROreader.fromList_GROreader() is not a list')

        # Initializing all variables that will be used
        totalSystemAtoms = 0
        residNum = []
        residType = []
        atomType = []
        atomNum = []
        xCoord = []
        yCoord = []
        zCoord = []
        xDim = 0
        yDim = 0
        zDim = 0

        # Saving the first line to get the total atoms in the system
        totalSystemAtoms = int(grofile[1].strip())

        # Making the lists of each variable accordingly to the spaces stated by GMX standard format.
        for line in range(2, len(grofile) - 1):

            residNum.append(int(grofile[line][0:5].strip()))
            residType.append(grofile[line][5:10].strip())
            atomType.append(grofile[line][10:15].strip())
            atomNum.append(int(grofile[line][15:20].strip()))
            xCoord.append(float(grofile[line][20:28].strip()))
            yCoord.append(float(grofile[line][28:36].strip()))
            zCoord.append(float(grofile[line][36:44].strip()))

        lastline = grofile[-1].split()
        xDim = float(lastline[0])
        yDim = float(lastline[1])
        zDim = float(lastline[2])

        return cls(totalSystemAtoms, residNum, residType, atomType, atomNum, xCoord, yCoord,
                   zCoord, xDim, yDim, zDim)


    @classmethod
    def fromObject_GROconcat(cls, objectList, boxZextension):
        """ fromObject_GROconcat is a Constructor that takes a list of grofile objects as first argument.
        The argument boxExtension is the addition space that is to be left between the +Z edge and
        the last molecule.
        It return a single concatenated grofile.
        Order matters. The first grofile object in the list will be first and last objecet will
        be last.
        The grofile objects must comply with the class attribute's format.
        Example how to use it:
            groConcat = GROreader.fromObject_GROconcat(grofile)
            print(groConcat.yDim)       # in case you want to print content
        """

        if isinstance(objectList, list):
            pass
        else:
            raise ValueError('Argument in GROreader.fromObject_GROconcat() is not a list')

        # Initializing all variables that will be used
        totalSystemAtoms = 0
        residNum = []
        residType = []
        atomType = []
        atomNum = 0
        xCoord = []
        yCoord = []
        zCoord = []
        xDim = 0
        yDim = 0
        zDim = 0
        lastNum = 0          # to store the last number of each residNum object
        buffer = 0.1        # leave a small buffer to avoid posible molecule overlapping
        addToZcoord = 0
        atomCount = []

        for groObject in objectList:

            totalSystemAtoms = totalSystemAtoms + groObject.totalSystemAtoms

            residNum.extend([(num + lastNum) for num in groObject.residNum])
            lastNum = residNum[-1]

            residType.extend(groObject.residType)

            atomType.extend(groObject.atomType)

            atomNum = len(groObject.atomNum) + atomNum

            xCoord.extend(groObject.xCoord)

            yCoord.extend(groObject.yCoord)

            zCoord.extend([(num + addToZcoord) for num in groObject.zCoord])
            addToZcoord = max(zCoord) + buffer # adding buffer to avoid possible overlap when puting next gto system in z axis

            if groObject.xDim > xDim:
                xDim = groObject.xDim
            else:
                xDim = xDim

            if groObject.yDim > yDim:
                yDim = groObject.yDim
            else:
                yDim = yDim

        atomNumLess100k = 1
        atomNumHigher100k = 1
        for item in range(1, atomNum + 1):        # atom are counted from number 1
            if item <= 99999:
                atomCount.append(atomNumLess100k)
                atomNumLess100k += 1
            else:
                atomCount.append(atomNumHigher100k)
                atomNumHigher100k += 1

        atomNum = atomCount
        zDim = max(zCoord) + int(boxZextension)

        return cls(totalSystemAtoms, residNum, residType, atomType, atomNum, xCoord, yCoord, zCoord,
                   xDim, yDim, zDim)


    def __del__(self):
        print("freeing memory by deleting GROreader object")
        # This is my destructor (it is not mandatory for python)


# ==================================================================================================
# MAIN (PROGRAM IMPLEMENTATION)
# ==================================================================================================

# --------------------------------------------------------------------------------------------------
# CREATING THE GRO FILE
# --------------------------------------------------------------------------------------------------

mainWorkDir = os.getcwd()  # Getting the path to directory

filesToConcat = sys.argv[1:]

groListToConcat = []

try:

    for file in filesToConcat:
        objFiUtilFile = FileUtil.FileReader(mainWorkDir, file)
        objGROreaderFile = GROreader.fromList_GROreader(objFiUtilFile.file)
        groListToConcat.append(objGROreaderFile)

        del objFiUtilFile, objGROreaderFile

    groConcatOb = GROreader.fromObject_GROconcat(groListToConcat, extraDistZ)
    groConcatObList = FileUtil.fromGROreaderToFileUtil(groConcatOb)

    # Writing the concatenated GROreader Object
    # ------------------------------------------
    groConcatObList.FileWriter(mainWorkDir, groConcatName)


except Exception:
    print('\n\nCaught an error:\n----------------')
    traceback.print_exc()


# Final printouts to the screen
# ------------------------------
print("\nThe new gro file name is: " + groConcatName)
print("\nIt is located in directory: " + mainWorkDir + "\n")
