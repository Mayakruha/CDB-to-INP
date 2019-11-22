#---------How to run
#python Mesh_CDB_to_INP.py Mixer-CB-FL-cl.cdb
import sys
Dir=''						# Work directory
MeshFileName=sys.argv[1]	# ANSYS dat file
#---------Example--------------------------
#Dir='D:\\'
#MeshFileName='Mixer-CB-FL-cl.cdb'
#--Settings--------------------------------
Hex=[[0,1,2,3],[0,1,5,4],[1,2,6,5],[2,3,7,6],[0,4,7,3],[4,5,6,7]]
Tet={'S1':[0,1,2],'S2':[0,1,3],'S3':[1,2,3],'S4':[0,3,2]}
#------------------------------------------
#------------DAT-file reading------------------------------
from bitarray import bitarray
ElemTypeList={}	#Keys:[ET Num][Type Elem Num]
Elements={}	#Keys:[Type Elem Num][Mat Num][Element Num] - Node Numbers
Faces={}	#Keys:[Min][Max][Third]
CMBLOCK={}
CMBLOCK['elem']={}
CMBLOCK['node']={}
SurfInfo={}	# Keys: [152 El Num] - [Min,Max,Mid,Named Selection]
SurfInfo['']={}
NamedSelection=''
#------------------------------------------
mf=open(Dir+MeshFileName,'r')
wf=open(Dir+MeshFileName[:-3]+'inp','w')
txt=mf.readline().lower()
while txt[0:5]!='':
	if txt[0:25]=='/com,*********** create "':
		NamedSelection=txt.split('"')[1]
		SurfInfo[NamedSelection]={}
		print(NamedSelection+' has been found')
	elif txt[0:3]=='et,':
		Values=txt.split(',')
		ElemType=int(Values[2])
		ElemTypeList[int(Values[1])]=ElemType
		if not ElemType in Elements:
			Elements[ElemType]={}
	elif txt[0:7]=='nblock,':			#-----Nodes block
		print('*Nodes reading')
		Values=txt.split(',')
		Num=int(Values[4])
		OuterNodes=bitarray(int(Values[3])+1)
		OuterNodes.setall(False)
		wf.write('*Node\n')
		txt=mf.readline()
		Values=txt[1:-2].split(',')
		NumLen=int(Values[0].split('i')[1])
		RowNum=int(Values[0].split('i')[0])
		CoordLen=int(Values[1].split('.')[0].split('e')[1])
		for i in range(0,Num):
			txt=mf.readline()
			TxtLen=len(txt)-1
			wf.write(txt[0:NumLen]+','+txt[RowNum*NumLen:RowNum*NumLen+CoordLen]+',')
			if TxtLen>(RowNum*NumLen+CoordLen): wf.write(txt[RowNum*NumLen+CoordLen:RowNum*NumLen+2*CoordLen]+',')
			else: wf.write(' 0.0,')
			if TxtLen>(RowNum*NumLen+2*CoordLen): wf.write(txt[RowNum*NumLen+2*CoordLen:RowNum*NumLen+3*CoordLen]+'\n')
			else: wf.write(' 0.0\n')
	elif txt[0:7]=='eblock,':			#-----Elements block
		print('*Elements reading')
		Values=mf.readline()[1:-2].split('i')
		RowNum=int(Values[0])
		NumLen=int(Values[1])
		txt=mf.readline()
		while not '-1' in txt:
			ElemType=ElemTypeList[int(txt[NumLen:2*NumLen])]
			ElemNum=int(txt[10*NumLen:11*NumLen])
			if ElemType==70:			#-----LINEAR TETRA/HEX
				MatNum=int(txt[0:NumLen])
				if not MatNum in Elements[ElemType]:Elements[ElemType][MatNum]={}
				Elements[ElemType][MatNum][ElemNum]=[]
				for i in range(11,14):Elements[ElemType][MatNum][ElemNum].append(int(txt[i*NumLen:(i+1)*NumLen]))
				Num=int(txt[14*NumLen:15*NumLen])
				if Elements[ElemType][MatNum][ElemNum][2]!=Num:Elements[ElemType][MatNum][ElemNum].append(Num)
				Elements[ElemType][MatNum][ElemNum].append(int(txt[15*NumLen:16*NumLen]))
				for Face in Tet:
					FaceNodesNum=[Elements[ElemType][MatNum][ElemNum][Tet[Face][0]],Elements[ElemType][MatNum][ElemNum][Tet[Face][1]],Elements[ElemType][MatNum][ElemNum][Tet[Face][2]]]
					MinNum=FaceNodesNum[0]
					MaxNum1=FaceNodesNum[0]
					if MinNum>FaceNodesNum[1]:
						MaxNum1=MinNum
						MinNum=FaceNodesNum[1]
					else:MaxNum1=FaceNodesNum[1]
					if MinNum>FaceNodesNum[2]:
						MidNum1=MinNum
						MinNum=FaceNodesNum[2]
					elif MaxNum1<FaceNodesNum[2]:
						MidNum1=MaxNum1
						MaxNum1=FaceNodesNum[2]
					else:MidNum1=FaceNodesNum[2]
					if not MinNum in Faces: Faces[MinNum]={}
					if not MaxNum1 in Faces[MinNum]: Faces[MinNum][MaxNum1]={}
					if not MidNum1 in Faces[MinNum][MaxNum1]:Faces[MinNum][MaxNum1][MidNum1]=[ElemNum,Face]
					else:
						Faces[MinNum][MaxNum1].__delitem__(MidNum1)
						if len(Faces[MinNum][MaxNum1])==0:
							Faces[MinNum].__delitem__(MaxNum1)
							if len(Faces[MinNum])==0:Faces.__delitem__(MinNum)
			if ElemType==87:			#-----QUADRATIC TETRA
				MatNum=int(txt[0:NumLen])
				if not MatNum in Elements[ElemType]:Elements[ElemType][MatNum]={}
				Elements[ElemType][MatNum][ElemNum]=[]
				for i in range(11,RowNum):Elements[ElemType][MatNum][ElemNum].append(int(txt[i*NumLen:(i+1)*NumLen]))
				txt=mf.readline()
				for i in range(0,21-RowNum):Elements[ElemType][MatNum][ElemNum].append(int(txt[i*NumLen:(i+1)*NumLen]))
				for Face in Tet:
					FaceNodesNum=[Elements[ElemType][MatNum][ElemNum][Tet[Face][0]],Elements[ElemType][MatNum][ElemNum][Tet[Face][1]],Elements[ElemType][MatNum][ElemNum][Tet[Face][2]]]
					MinNum=FaceNodesNum[0]
					MaxNum1=FaceNodesNum[0]
					if MinNum>FaceNodesNum[1]:
						MaxNum1=MinNum
						MinNum=FaceNodesNum[1]
					else:MaxNum1=FaceNodesNum[1]
					if MinNum>FaceNodesNum[2]:
						MidNum1=MinNum
						MinNum=FaceNodesNum[2]
					elif MaxNum1<FaceNodesNum[2]:
						MidNum1=MaxNum1
						MaxNum1=FaceNodesNum[2]
					else:MidNum1=FaceNodesNum[2]
					if not MinNum in Faces: Faces[MinNum]={}
					if not MaxNum1 in Faces[MinNum]: Faces[MinNum][MaxNum1]={}
					if not MidNum1 in Faces[MinNum][MaxNum1]:Faces[MinNum][MaxNum1][MidNum1]=[ElemNum,Face]
					else:
						Faces[MinNum][MaxNum1].__delitem__(MidNum1)
						if len(Faces[MinNum][MaxNum1])==0:
							Faces[MinNum].__delitem__(MaxNum1)
							if len(Faces[MinNum])==0:Faces.__delitem__(MinNum)
			elif ElemType==90:			#-----QUADRATIC HEX
#				MatNum=int(txt[0:NumLen])
#				if not MatNum in Elements[ElemType]:Elements[ElemType][MatNum]={}
#				Elements[ElemType][MatNum][ElemNum]=[]
#				for i in range(0,8):ElemNodesNum[i]=int(txt[(i+11)*NumLen:(i+12)*NumLen])
#				for Face in Hex:
#					FaceNodesNum=[ElemNodesNum[Face[0]],ElemNodesNum[Face[1]],ElemNodesNum[Face[2]],ElemNodesNum[Face[3]]]
#					MinNum=int(min(FaceNodesNum))
#					indx=FaceNodesNum.index(MinNum)
#					if indx==3:
#						MaxNum1=FaceNodesNum[0]
#						MidNum1=FaceNodesNum[0]
#					else:
#						MaxNum1=FaceNodesNum[indx+1]
#						MidNum1=FaceNodesNum[indx+1]
#					if indx==0:
#						MaxNum2=FaceNodesNum[3]
#						MidNum2=FaceNodesNum[3]
#					else:
#						MaxNum2=FaceNodesNum[indx-1]
#						MidNum2=FaceNodesNum[indx-1]
					#----------
#					if indx>1:
#						if MaxNum1<FaceNodesNum[indx-2]:MaxNum1=FaceNodesNum[indx-2]
#						else:MidNum1=FaceNodesNum[indx-2]
#						if MaxNum2<FaceNodesNum[indx-2]:MaxNum2=FaceNodesNum[indx-2]
#						else:MidNum2=FaceNodesNum[indx-2]					
#					else:
#						if MaxNum1<FaceNodesNum[indx+2]:MaxNum1=FaceNodesNum[indx+2]
#						else:MidNum1=FaceNodesNum[indx+2]
#						if MaxNum2<FaceNodesNum[indx+2]:MaxNum2=FaceNodesNum[indx+2]
#						else:MidNum2=FaceNodesNum[indx+2]
#					if not MinNum in Faces: Faces[MinNum]={}
#					if not MaxNum1 in Faces[MinNum]: Faces[MinNum][MaxNum1]={}
#					if not MaxNum2 in Faces[MinNum]: Faces[MinNum][MaxNum2]={}
#					if not MidNum1 in Faces[MinNum][MaxNum1]: Faces[MinNum][MaxNum1][MidNum1]=0
#					else:
#						Faces[MinNum][MaxNum1].__delitem__(MidNum1)
#						if len(Faces[MinNum][MaxNum1])==0:
#							Faces[MinNum].__delitem__(MaxNum1)
#							if len(Faces[MinNum])==0:Faces.__delitem__(MinNum)
#					if not MidNum2 in Faces[MinNum][MaxNum2]: Faces[MinNum][MaxNum2][MidNum2]=0
#					else:
#						Faces[MinNum][MaxNum2].__delitem__(MidNum2)
#						if len(Faces[MinNum][MaxNum2])==0:
#							Faces[MinNum].__delitem__(MaxNum2)
#							if len(Faces[MinNum])==0:Faces.__delitem__(MinNum)
				txt=mf.readline()
			elif ElemType==152:		#-------Shell elements for ThBCs
				MatNum=int(txt[0:NumLen])
				if not MatNum in Elements[ElemType]:Elements[ElemType][MatNum]={}
				Elements[ElemType][MatNum][ElemNum]=[]
				for i in range(11,14):Elements[ElemType][MatNum][ElemNum].append(int(txt[i*NumLen:(i+1)*NumLen]))
				Num=int(txt[14*NumLen:15*NumLen])
				if Elements[ElemType][MatNum][ElemNum][2]!=Num:Elements[ElemType][MatNum][ElemNum].append(Num)
				Elements[ElemType][MatNum][ElemNum].sort()
				Num=len(Elements[ElemType][MatNum][ElemNum])-1
				Face=Faces[Elements[ElemType][MatNum][ElemNum][0]][Elements[ElemType][MatNum][ElemNum][Num]][Elements[ElemType][MatNum][ElemNum][1]][1]
				if not Face in SurfInfo[NamedSelection]:SurfInfo[NamedSelection][Face]=[] 
				SurfInfo[NamedSelection][Face].append(Faces[Elements[ElemType][MatNum][ElemNum][0]][Elements[ElemType][MatNum][ElemNum][Num]][Elements[ElemType][MatNum][ElemNum][1]][0])
			elif ElemType==131:		#-----TBC LINEAR ELEMENTS
				MatNum=int(txt[3*NumLen:4*NumLen])
				if not MatNum in Elements[ElemType]:Elements[ElemType][MatNum]={}
				Elements[ElemType][MatNum][ElemNum]=[]
				for i in range(11,14):Elements[ElemType][MatNum][ElemNum].append(int(txt[i*NumLen:(i+1)*NumLen]))
				Num=int(txt[14*NumLen:15*NumLen])
				if Elements[ElemType][MatNum][ElemNum][2]!=Num:
					Elements[ElemType][MatNum][ElemNum].append(Num)
			elif ElemType==132:		#-----TBC QUADRATIC ELEMENTS
				MatNum=int(txt[3*NumLen:4*NumLen])
				if not MatNum in Elements[ElemType]:Elements[ElemType][MatNum]={}
				Elements[ElemType][MatNum][ElemNum]=[]
				for i in range(11,14):Elements[ElemType][MatNum][ElemNum].append(int(txt[i*NumLen:(i+1)*NumLen]))
				Num=int(txt[14*NumLen:15*NumLen])
				if Elements[ElemType][MatNum][ElemNum][2]!=Num:
					Elements[ElemType][MatNum][ElemNum].append(Num)
				if RowNum>18:
					for i in range(15,18):Elements[ElemType][MatNum][ElemNum].append(int(txt[i*NumLen:(i+1)*NumLen]))
					Num=int(txt[18*NumLen:19*NumLen])
					if Elements[ElemType][MatNum][ElemNum][len(Elements[ElemType][MatNum][ElemNum])-1]!=Num:
						Elements[ElemType][MatNum][ElemNum].append(Num)
			txt=mf.readline()
		NamedSelection=''
		for MinNum in Faces:
			for MaxNum1 in Faces[MinNum]:
				for MidNum1 in Faces[MinNum][MaxNum1]:
					OuterNodes[MinNum]=True
					OuterNodes[MaxNum1]=True
					OuterNodes[MidNum1]=True
	elif txt[0:8]=='cmblock,':
		Values=txt.split(',')
		NamedSelection=Values[1].replace(' ','')
		BlockType=Values[2].lower()
		Num=int(Values[3].split('!')[0])
		print(NamedSelection+' has been found')
		NumLen=int(mf.readline()[1:-2].split('i')[1])
		j=0
		if BlockType=='elem':
			SurfInfo[NamedSelection]={}
			while j<Num:
				txt=mf.readline()
				TxtLen=len(txt)-1
				k=0					
				while k*NumLen<TxtLen:
					ElemNum=int(txt[k*NumLen:(k+1)*NumLen])
					if 152 in Elements:
						for MatNum in Elements[152]:
							if ElemNum in Elements[152][MatNum]:
								Indx=len(Elements[152][MatNum][ElemNum])-1
								Face=Faces[Elements[152][MatNum][ElemNum][0]][Elements[152][MatNum][ElemNum][Indx]][Elements[152][MatNum][ElemNum][1]][1]
								if not Face in SurfInfo[NamedSelection]:SurfInfo[NamedSelection][Face]=[]
								SurfInfo[NamedSelection][Face].append(Faces[Elements[152][MatNum][ElemNum][0]][Elements[152][MatNum][ElemNum][Indx]][Elements[152][MatNum][ElemNum][1]][0])
					k+=1
				j+=k
		elif BlockType=='node':
			CMBLOCK[BlockType][NamedSelection]=[]
			while j<Num:
				txt=mf.readline()
				TxtLen=len(txt)-1
				k=0					
				while k*NumLen<TxtLen:
					MinNum=int(txt[k*NumLen:(k+1)*NumLen])
					if OuterNodes[MinNum]:CMBLOCK[BlockType][NamedSelection].append(MinNum)
					k+=1
				j+=k
	txt=mf.readline().lower()			
mf.close()
print('*Elements writing')
#----------------------------------------------------------
#------------DATA processing-------------------------------
if 152 in Elements: Elements.__delitem__(152)
for ElemType in Elements:
	if ElemType==70: AbaqusCommand='*Element, type=DC3D4, elset=Elem'
	elif ElemType==87: AbaqusCommand='*Element, type=DC3D10, elset=Elem'
	elif ElemType==131: AbaqusCommand='*Element, type=DS3, elset=Elem'
	elif ElemType==132: AbaqusCommand='*Element, type=DS6, elset=Elem'
	for MatNum in Elements[ElemType]:
		wf.write(AbaqusCommand+str(ElemType)+'_'+str(MatNum)+'\n')
		for ElemNum in Elements[ElemType][MatNum]:
			wf.write(str(ElemNum)+',')
			Num=len(Elements[ElemType][MatNum][ElemNum])-1
			for i in range(0,Num):
				wf.write(str(Elements[ElemType][MatNum][ElemNum][i])+',')
			wf.write(str(Elements[ElemType][MatNum][ElemNum][Num])+'\n')
		wf.write('*SOLID SECTION, elset=Elem'+str(ElemType)+'_'+str(MatNum)+', material=mat-'+str(MatNum)+'\n')
#----------------------------------------------------------
#------------DATA processing-------------------------------
#-- Node blocks
print('**Node block data processing')
for NamedSelection in CMBLOCK['node']:
	for MinNum in Faces:
		if MinNum in CMBLOCK['node'][NamedSelection]:
			for MaxNum1 in Faces[MinNum]:
				if MaxNum1 in CMBLOCK['node'][NamedSelection]:
					for MidNum1 in Faces[MinNum][MaxNum1]:
						if MidNum1 in CMBLOCK['node'][NamedSelection]:
							Face=Faces[MinNum][MaxNum1][MidNum1][1]
							if not NamedSelection in SurfInfo: SurfInfo[NamedSelection]={}
							if not Face in SurfInfo[NamedSelection]: SurfInfo[NamedSelection][Face]=[]
							SurfInfo[NamedSelection][Face].append(Faces[MinNum][MaxNum1][MidNum1][0])
SurfInfo.__delitem__('')
#----------------------------------------------------------
#-----------SURFACE OUTPUT---------------------------------
print('***SURFACE OUTPUT')
for NamedSelection in SurfInfo:
	for Face in SurfInfo[NamedSelection]:
		wf.write('*Elset, elset=_'+NamedSelection+'_'+Face+'\n')
		Num=len(SurfInfo[NamedSelection][Face])-1
		j=1
		for i in range(0,Num):
			if j==16:
				j=0
				wf.write(str(SurfInfo[NamedSelection][Face][i])+'\n')
			else: wf.write(str(SurfInfo[NamedSelection][Face][i])+',')
			j=j+1
		wf.write(str(SurfInfo[NamedSelection][Face][Num])+'\n')
	if len(SurfInfo[NamedSelection])>0: wf.write('*Surface, type=ELEMENT, name='+NamedSelection+'\n')
	for Face in SurfInfo[NamedSelection]:
		wf.write('_'+NamedSelection+'_'+Face+', '+Face+'\n')
wf.close()
