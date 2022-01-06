import board
import neopixel
import time
import mido
from mido import MidiFile

mid = MidiFile('deb_clai.mid')

tempo = 500000 # Default tempo = 120 BPM

pixels=neopixel.NeoPixel(board.D18, 100, brightness =1)
white = (25,25,25)
rightRGB = (25, 0, 25)
leftRGB = (0, 12.5, 25)
off = (0,0,0)

def pix_idx(midi_idx):
    return 108 - midi_idx



def mergeDeltaTime(listA, listB):
    
    mergedList = []
    
    while listA and listB:
        if listA[0][0] == listB[0][0]:
            listB[0][0] = 0
            mergedList.append(listA.pop(0))
            mergedList.append(listB.pop(0))
        elif listA[0][0] > listB[0][0]:
            listA[0][0] -= listB[0][0]
            mergedList.append(listB.pop(0))
        else:
            listB[0][0] -= listA[0][0]
            mergedList.append(listA.pop(0))
            
    if listA:
        for inst in listA:
            mergedList.append(inst)
    if listB:
        for inst in listB:
            mergedList.append(inst)
    
    return mergedList



def midiVisualizer(mult):

    tempoChangesRight = []

    for track in mid.tracks[0]:
        midiInfo = str(track).split(" ")
        del midiInfo[0:2]
        #midiInfo = str(track).split("(")[1][:-1].split(", ")
        if midiInfo[0] == "set_tempo":
            tempo = int(midiInfo[1].split('=')[1])
            tempoChangesRight.append([track.time, tempo*mult, track.time])
            #print(mido.tempo2bpm(tempo))

    tempoChangesLeft = tempoChangesRight

    secPerTick = tempo / (mid.ticks_per_beat * 1000000)
    #print(secPerTick)

    rightInst = [] # LED Instructions
    leftInst = []
    ledInst = []

    ctrlDelay = 0

    for track in mid.tracks[1]:
        noteInfo = str(track).split(" ")
        if noteInfo[0] == 'note_on' or noteInfo[0] == 'note_off':
            del noteInfo[0:2]
            noteLED = [
                int(noteInfo[2].split('=')[1]) + ctrlDelay, # Delay in Seconds
                pix_idx(int(noteInfo[0].split('=')[1])),            # LED ID
                int(noteInfo[1].split("=")[1]),                     # On or Off
                rightRGB
            ]
            ctrlDelay = 0
            rightInst.append(noteLED)
        elif noteInfo[0] == 'control_change':
            ctrlDelay += track.time
            
    rightInst = mergeDeltaTime(tempoChangesRight, rightInst)
    
    for i in range(len(rightInst)):
        if len(rightInst[i]) == 3:
            secPerTick = rightInst[i][1] / (mid.ticks_per_beat * 1000000)
        rightInst[i][0] *= secPerTick
    
    ctrlDelay = 0
    
    if len(mid.tracks) > 2:
        for track in mid.tracks[2]:
            noteInfo = str(track).split(" ")
            if noteInfo[0] == 'note_on' or noteInfo[0] == 'note_off':
                del noteInfo[0:2]
                noteLED = [
                    int(noteInfo[2].split('=')[1]) + ctrlDelay, # Delay in Seconds
                    pix_idx(int(noteInfo[0].split('=')[1])),            # LED ID
                    int(noteInfo[1].split("=")[1]),                     # On or Off
                    leftRGB
                ]
                ctrlDelay = 0
                leftInst.append(noteLED)
            elif noteInfo[0] == 'control_change':
                ctrlDelay += track.time
                
        leftInst = mergeDeltaTime(tempoChangesLeft, leftInst)
        for i in range(len(leftInst)):
            if len(leftInst[i]) == 3:
                secPerTick = leftInst[i][1] / (mid.ticks_per_beat * 1000000)
            leftInst[i][0] *= secPerTick
    
    ledInst = mergeDeltaTime(rightInst, leftInst)
    
    for inst in ledInst:
        
        time.sleep(inst[0])
        if len(inst) == 4:
            if inst[2]:
                pixels[inst[1]] = inst[3]
            else:
                pixels[inst[1]] = off
        


    
try:
    tempoMult = 1 # In BPM
    midiVisualizer(tempoMult)
    
    
except KeyboardInterrupt:
    pixels.fill(off)
