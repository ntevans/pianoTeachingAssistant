import board
import neopixel
import time
import mido
from mido import MidiFile

pixels=neopixel.NeoPixel(board.D18, 100, brightness =1)
white = (25,25,25)
turquoise = (25, 0, 25)
purple = (0, 12.5, 25)
off = (0,0,0)

def pix_idx(midi_idx):
    return 108 - midi_idx



def mergeDeltaTime(A, B):
    listA = A
    listB = B
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



def midiVisualizer(midiName, leftRGB, rightRGB, tempoMult):
    mid = MidiFile(midiName)
    tempoChange = []
    tempo = 500000 # Default tempo = 120 BPM
    
    for msg in mid.tracks[0]:
        if msg.type == "set_tempo":
            tempo = msg.tempo
            tempoChange.append([msg.time, tempo])
    
    #tempoChangesLeft = tempoChangesRight

    secPerTick = tempo / (mid.ticks_per_beat * 1000000)
    #print(secPerTick)

    rightInst = [] # LED Instructions
    leftInst = []
    ledInst = []

    ctrlDelay = 0

    for msg in mid.tracks[1]:
        if msg.type == 'note_on' or msg.type == 'note_off':
            
            noteLED = [
                msg.time + ctrlDelay, # Delay in Seconds
                pix_idx(msg.note),            # LED ID
                msg.velocity,                     # On or Off
                rightRGB
            ]
            ctrlDelay = 0
            rightInst.append(noteLED)
        elif msg.type == 'control_change':
            ctrlDelay += msg.time
    
    # [Delay (sec), LED ID, velocity, color]        
    #for inst in rightInst:
    #    print(inst)
    
    master = mergeDeltaTime(tempoChange, rightInst)
    
    """
    for i in rightInst:
        if len(i) == 2:
            secPerTick = i[1] / (mid.ticks_per_beat * 1000000)
        rightInst[i][0] *= secPerTick
    """
    
    ctrlDelay = 0
        
    if len(mid.tracks) > 2:
        for msg in mid.tracks[2]:
            if msg.type == 'note_on' or msg.type[0] == 'note_off':
                noteLED = [
                    msg.time + ctrlDelay, # Delay in Seconds
                    pix_idx(msg.note),            # LED ID
                    msg.velocity,                     # On or Off
                    leftRGB
                ]
                ctrlDelay = 0
                leftInst.append(noteLED)
            elif msg.type == 'control_change':
                ctrlDelay += msg.time
    
    master = mergeDeltaTime(master, leftInst)
    
    tempo = 500000 # Default tempo = 120 BPM
    secondsPerTick = 1 # Default
    for inst in master:
        time.sleep(inst[0] * secondsPerTick / tempoMult)
        
        if len(inst) == 2:
            tempo = inst[1]
            secondsPerTick = tempo / (mid.ticks_per_beat * 1000000)
        if len(inst) == 4:
            if inst[2]:
                pixels[inst[1]] = inst[3]
            else:
                pixels[inst[1]] = off

    
try:
    tempoMult = 1 # In BPM
    midiName = 'ms.mid'
    rightRGB = turquoise
    leftRGB = purple
    midiVisualizer(midiName, leftRGB, rightRGB, tempoMult)
    
    
except KeyboardInterrupt:
    pixels.fill(off)

