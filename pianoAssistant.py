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

def light_notes(notes, length, rgb):
    for note in notes:
        pixels[note] = rgb
    time.sleep(length)
    for note in notes:
        pixels[note] = off
        
def cool_visual1(baseLED, accentLED):
    pixels.fill(baseLED)
    for i in range(88):
        pixels[87 - i] = accentLED
        time.sleep(0.025)
        pixels[87 - i] = baseLED
    for i in range(88):
        pixels[i] = accentLED
        time.sleep(0.025)
        pixels[i] = baseLED
    pixels.fill(off)
    
def tempo_visual(accentLED, sleepTime):
    pixels.fill(accentLED)
    time.sleep(sleepTime*2)
    pixels.fill(off)
    time.sleep(sleepTime*2)
    pixels.fill(accentLED)
    time.sleep(sleepTime*2)
    pixels.fill(off)
    time.sleep(sleepTime*2)
    pixels.fill(accentLED)
    time.sleep(sleepTime)
    pixels.fill(off)
    time.sleep(sleepTime)
    pixels.fill(accentLED)
    time.sleep(sleepTime)
    pixels.fill(off)
    time.sleep(sleepTime)
    pixels.fill(accentLED)
    time.sleep(sleepTime)
    pixels.fill(off)
    time.sleep(sleepTime)
    pixels.fill(accentLED)
    time.sleep(sleepTime)
    pixels.fill(off)
    time.sleep(sleepTime)
    
def scale(starting_note, length, rgb):
    light_notes([starting_note], length, rgb)
    light_notes([starting_note - 2], length, rgb)
    light_notes([starting_note - 4], length, rgb)
    light_notes([starting_note - 5], length, rgb)
    light_notes([starting_note - 7], length, rgb)
    light_notes([starting_note - 9], length, rgb)
    light_notes([starting_note - 11], length, rgb)
    light_notes([starting_note - 12], length, rgb)
    light_notes([starting_note - 11], length, rgb)
    light_notes([starting_note - 9], length, rgb)
    light_notes([starting_note - 7], length, rgb)
    light_notes([starting_note - 5], length, rgb)
    light_notes([starting_note - 4], length, rgb)
    light_notes([starting_note - 2], length, rgb)
    light_notes([starting_note], length, rgb)
    
def scale_2hands(starting_note, length, rgb):
    light_notes([starting_note, starting_note + 12], length, rgb)
    light_notes([starting_note - 2, starting_note + 10], length, rgb)
    light_notes([starting_note - 4, starting_note + 8], length, rgb)
    light_notes([starting_note - 5, starting_note + 7], length, rgb)
    light_notes([starting_note - 7, starting_note + 5], length, rgb)
    light_notes([starting_note - 9, starting_note + 3], length, rgb)
    light_notes([starting_note - 11, starting_note + 1], length, rgb)
    light_notes([starting_note - 12, starting_note], length, rgb)
    light_notes([starting_note - 11, starting_note + 1], length, rgb)
    light_notes([starting_note - 9, starting_note + 3], length, rgb)
    light_notes([starting_note - 7, starting_note + 5], length, rgb)
    light_notes([starting_note - 5, starting_note + 7], length, rgb)
    light_notes([starting_note - 4, starting_note + 8], length, rgb)
    light_notes([starting_note - 2, starting_note +10], length, rgb)
    light_notes([starting_note, starting_note + 12], length, rgb)

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
    
    
    #tempo_visual(white, master[0][1] * 100 / (mid.ticks_per_beat * 1000000))
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

def choiceLoop(choices, optionPrompt):
    print(optionPrompt)
    
    quitLoop = False
    finalChoice = -1
    while not(quitLoop):
        print()
        idx = 0
        for choice in choices:
            print(choice + "[" + str(idx) + "]")
            idx += 1
        userChoice = int(input())
        if userChoice in range(0, len(choices)):
            finalChoice = userChoice
            quitLoop = True
        else:
            print("Please select from the given options. Please type exacly as shown, no spaces...")
    return finalChoice
    
def userInput():
    
    print("\nHello! Welcome to Piano Assistant!\n")
    #cool_visual1(purple, white)
    
    quitLoop = False
    while not(quitLoop):
        
        mainMenuChoices = ["Scales", "Song", "Quit"]
        userChoice = choiceLoop(mainMenuChoices, "Please choose from the following options:")
        
        if (userChoice == 0):
            scaleDict = [["C", 48], ["C#", 47], ["D", 46], ["D#", 45], ["E", 44], ["F", 43], ["F#", 42], ["G", 41], ["G#", 40], ["A", 39], ["A#", 38], ["B", 37]]
            handChoices = ["Right", "Left", "Both"]
            
            scaleName = choiceLoop(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"], "Please choose from the following scales:")
            handChoice = choiceLoop(handChoices, "Would you like to practice with right hand, left hand or both hands?:")
            
            bpm = int(input("Please insert speed in BPM (60 default)"))
            print(handChoice)
            if handChoice == 0:
                try:
                    print("Press ctrl + C to quit and return to main menu")
                    #tempo_visual(white, 60 / bpm)
                    while True:
                        scale(scaleDict[scaleName][1], 60 / bpm, white)
                except KeyboardInterrupt:
                    pixels.fill(off)
            elif handChoice == 1:
                try:
                    print("Press ctrl + C to quit and return to main menu")
                    #tempo_visual(white, 60 / bpm)
                    while True:
                        scale(scaleDict[scaleName][1] + 12, 60 / bpm, white)
                except KeyboardInterrupt:
                    pixels.fill(off)
            elif handChoice == 2:
                try:
                    print("Press ctrl + C to quit and return to main menu")
                    #tempo_visual(white, 60 / bpm)
                    while True:
                        scale_2hands(scaleDict[scaleName][1], 60 / bpm, white)
                except KeyboardInterrupt:
                    pixels.fill(off)
            else:
                print("else, problem here")
            
            
        elif (userChoice == 1):
            songName = choiceLoop(["Claire de Lune", "Moonlight Sonata", "Twinkle Twinkle Little Star", "Wii Channel Music"], "Please choose from the following songs:")
            if (songName == 0):
                midiName = 'deb_clai.mid'
            elif (songName == 1):
                midiName = 'ms.mid'
            elif (songName == 2):
                midiName = 'ttls.mid'
            elif (songName == 3):
                midiName = 'wii.mid'
            else:
                print("else triggered. problem here")
                
            tempoMult = float(input("Please enter the tempo multiplier you would like to add (1 is default)")) # In BPM
            
            rightRGB = turquoise
            leftRGB = purple
            
            try:
                print("Press ctrl + C to quit and return to main menu")
                midiVisualizer(midiName, leftRGB, rightRGB, tempoMult)
            except KeyboardInterrupt:
                pixels.fill(off)
        elif (userChoice == 2):
            print("Please Come Again!")
            quitLoop = True
        else:
            print("Else triggered, problem here")



try:
    
    userInput()
    
    
except KeyboardInterrupt:
    pixels.fill(off)


