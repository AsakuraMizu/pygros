from phigros import *
import json
import sys
sys.setrecursionlimit(100000)

chart_location='assets/Chart.json'
music_locatioon='assets/music.wav'
illustration_location='assets/Illustration.png'

with open(chart_location,'r',encoding='utf-8') as f:
    input_chart=json.load(f)
    bpm=input_chart['judgeLineList'][0]['bpm']*1.6
    spd=1
    # d_line=Line(0.5,0.5,0,1)
    # Offset(0.1)
    with Multiplier(30/bpm):
        Offset(-0.1)
        for judgeLine in input_chart['judgeLineList']:
            if(judgeLine['judgeLineDisappearEvents'][0]['start']==1):
                newLine=Line(judgeLine['judgeLineMoveEvents'][0]['start']//1000/2000+0.3,judgeLine['judgeLineMoveEvents'][0]['start']%1000/1000,judgeLine['judgeLineRotateEvents'][0]['start'],1)
            else:
                newLine=Line(judgeLine['judgeLineMoveEvents'][0]['start']//1000/2000+0.3,judgeLine['judgeLineMoveEvents'][0]['start']%1000/1000,judgeLine['judgeLineRotateEvents'][0]['start'],0)
            # for judgeLineDisappear in judgeLine['judgeLineDisappearEvents']:
            #     newLine.set(judgeLineDisappear['startTime']/10,width=judgeLineDisappear['start'])
            # for judgeLineMove in judgeLine['judgeLineMoveEvents']:
            #     newLine.set(judgeLineMove['startTime']/10,x=judgeLineMove['start']//1000/1000+0.5,y=judgeLineMove['start']%1000/1000)
            # for judgeLineRotate in judgeLine['judgeLineRotateEvents']:
            #     newLine.set(judgeLineRotate['startTime']/10,angle=judgeLineRotate['start'])
            #     newLine.set(judgeLineRotate['endTime']/10,angle=judgeLineRotate['end'])
            judgeLineAction=dict()
            # judgeLineAction
            for Action in judgeLine['judgeLineDisappearEvents']:
                if judgeLineAction.get(Action['startTime'])==None:
                    judgeLineAction[Action['startTime']]=dict(width=(1 if Action['start']==1 else 0.1))
                else:
                    judgeLineAction[Action['startTime']]['width']=(1 if Action['start']==1 else 0.1)
            for Action in judgeLine['judgeLineMoveEvents']:
                if judgeLineAction.get(Action['startTime'])==None:
                    judgeLineAction[Action['startTime']]=dict(x=(Action['start']/1000)/2000+0.3,y=(Action['start']%1000)/1000)
                else:
                    judgeLineAction[Action['startTime']]['x']=(Action['start']/1000)/2000+0.3
                    judgeLineAction[Action['startTime']]['y']=(Action['start']%1000)/1000
            for Action in judgeLine['judgeLineRotateEvents']:
                if judgeLineAction.get(Action['startTime'])==None:
                    judgeLineAction[Action['startTime']]=dict(angle=-Action['start'])
                else:
                    judgeLineAction[Action['startTime']]['angle']=-Action['start']
                if judgeLineAction.get(Action['endTime'])==None:
                    judgeLineAction[Action['endTime']]=dict(angle=-Action['end'])
                else:
                    judgeLineAction[Action['endTime']]['angle']=-Action['end']
            for ActionTime,Action in judgeLineAction.items():
                newLine.set(sec=ActionTime/10,
                            x=(Action['x'] if Action.get('x')!=None else None),
                            y=(Action['y'] if Action.get('y')!=None else None),
                            angle=(Action['angle'] if Action.get('angle')!=None else None),
                            width=(Action['width'] if Action.get('width')!=None else None))
            with newLine:
                for note in judgeLine['notesAbove']:
                    if(note['type']==1):
                        Click(note['time']/10,note['positionX']/15,spd)
                    if(note['type']==2):
                        Drag(note['time']/10,note['positionX']/15,spd)
                    if(note['type']==3):
                        Hold(note['time']/10,note['positionX']/15,spd,note['holdTime']/10)
                    if(note['type']==4):
                        Flick(note['time']/10,note['positionX']/15,spd)
                for note in judgeLine['notesBelow']:
                    if(note['type']==1):
                        Click(note['time']/10,note['positionX']/15,-spd)
                    if(note['type']==2):
                        Drag(note['time']/10,note['positionX']/15,-spd)
                    if(note['type']==3):
                        Hold(note['time']/10,note['positionX']/15,-spd,note['holdTime']/10)
                    if(note['type']==4):
                        Flick(note['time']/10,note['positionX']/15,-spd)
                    
    preview(input_chart['name'],input_chart['level'],music=music_locatioon,background=illustration_location)