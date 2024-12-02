# Automatic Potion Butler Filler by MatsaMilla - last updated by Aga
#   - Version 5, updated 12/2/24 to work with new butler gump & clean up Matsa's code... THANKS AGA!

# Must have TOOLTIPSON ([toggletooltips in game to turn off/on)

# NEED: Restock Chest (containing regs / empty pots), 
#       Mortars in backpack or in restock chest (can be in a bag in restock chest, has to be open).
#       Empty keg in toons backpack.

# Makes Make sure restock chest & motar restock bags are open

#mark false to NOT fill DP

fillDeadlyPoison = False

#*******************************************************************#
Journal.Clear()
Player.HeadMessage(66,'Target Butler')
butler = Target.PromptTarget('Target Butler')
Player.HeadMessage(66,'Target Restock Chest')
restockChest = Items.FindBySerial( Target.PromptTarget('Target Restock Chest') )
Player.HeadMessage(66,'Mortar Restock Bag (optional)')
mortarBag = Items.FindBySerial( Target.PromptTarget('Mortar Restock Bag (optional)') )

import sys
        
keg = Items.FindByID( 0x1940 , -1 ,  Player.Backpack.Serial )
if keg:
    Misc.SendMessage('Using keg in pack', 66)
else:
    Player.HeadMessage(66,'Target keg to fill')
    kegTarget =  Target.PromptTarget('Target keg to fill')
    Misc.SendMessage('Using targeted Keg', 66)
    keg = Items.FindBySerial(kegTarget)

fillStopNumber = 9000 #10000 if you have upgrade
dragTime = 400
butlerGump = 0x3AF7B574

def setValues( regValue , potValue , gump1 , gump2 ):
    global regID
    global potID
    global gumpAction1
    global gumpAction2
    regID = regValue
    potID = potValue
    gumpAction1 = gump1
    gumpAction2 = gump2


def FindItem( itemID, container, color = -1, ignoreContainer = [] ):
    ignoreColor = False
    if color == -1:
        ignoreColor = True

    if isinstance( itemID, int ):
        foundItem = next( ( item for item in container.Contains if ( item.ItemID == itemID and ( ignoreColor or item.Hue == color ) ) ), None )
    elif isinstance( itemID, list ):
        foundItem = next( ( item for item in container.Contains if ( item.ItemID in itemID and ( ignoreColor or item.Hue == color ) ) ), None )
    else:
        raise ValueError( 'Unknown argument type for itemID passed to FindItem().', itemID, container )

    if foundItem != None:
        return foundItem

    subcontainers = [ item for item in container.Contains if ( item.IsContainer and not item.Serial in ignoreContainer ) ]
    for subcontainer in subcontainers:
        foundItem = FindItem( itemID, subcontainer, color, ignoreContainer )
        if foundItem != None:
            return foundItem
            
def craftPot(potData):
    potType, _, regID, potID, gumpAction1, gumpAction2 = potData

    while not Items.GetPropValue(keg, 'The Keg Is Completely Full.'):
        worldSave()

        # find mortar, even if nested in backpack
        mortar = FindItem(0x0E9B, Player.Backpack)
        if not mortar:
            mortarFound = FindItem(0x0E9B, restockChest)
            if mortarFound:
                Items.Move(mortarFound, Player.Backpack.Serial, 0)
                Misc.Pause(dragTime)
            else:
                Misc.SendMessage('Out of Mortars!', 33)
                Misc.Pause(5000)
                sys.exit()

        # count / restock reg type
        packRegs = FindItem(regID, Player.Backpack)
        if not packRegs or packRegs.Amount < 10:
            Misc.Pause(100)
            regFound = FindItem(regID, restockChest)
            if regFound:
                Items.WaitForProps(regFound.Serial, dragTime)
                Items.Move(regFound, Player.Backpack, 250)
                Misc.Pause(800)
                packRegs = FindItem(regID, Player.Backpack)
                if not packRegs or packRegs.Amount < 10:
                    break
            else:
                Misc.SendMessage('Out of regs for this pot type, moving to next pot', 33)
                return False

        # move pot to keg
        pot = FindItem(potID, Player.Backpack)
        while pot:
            Items.Move(pot, keg, 0)
            Misc.Pause(dragTime)
            pot = FindItem(potID, Player.Backpack)
            if Journal.Search('You decide that it would be a bad idea to mix different types of potions.'):
                Items.Move(keg, butler, 0)
                Misc.Pause(dragTime)
                Journal.Clear('You decide that it would be a bad idea to mix different types of potions.')

            if Journal.SearchByType('The keg will not hold any more!', 'System'):
                break

        # ensure empty bottles are available
        if Items.BackpackCount(0x0F0E) < 1:
            emptyPot = FindItem(0x0F0E, restockChest)
            if emptyPot:
                Items.Move(emptyPot, Player.Backpack.Serial, 2)
                Misc.Pause(dragTime)
            else:
                Player.HeadMessage(33, 'Need empty pot(s) in restock container or in backpack.')
                sys.exit()

        # empty keg of other potion
        if Journal.Search('You decide that it would be a bad idea to mix different types of potions.'):
            Items.Move(keg, butler, 0)
            Misc.Pause(dragTime)
            Journal.Clear('You decide that it would be a bad idea to mix different types of potions.')

        # craft pot
        Items.UseItem(mortar)
        Gumps.WaitForGump(949095101, 1500)
        Gumps.SendAction(949095101, gumpAction1)
        Gumps.WaitForGump(949095101, 1500)
        Gumps.SendAction(949095101, gumpAction2)
        Gumps.WaitForGump(949095101, 1500)
        Misc.Pause(120)

    # move keg to butler
    Items.Move(keg, butler, 0)
    Misc.Pause(dragTime)
    
def worldSave():
    if Journal.SearchByType('The world is saving, please wait.', 'Regular' ):
        Misc.SendMessage('Pausing for world save', 33)
        while not Journal.SearchByType('World save complete.', 'Regular'):
            Misc.Pause(1000)
        Misc.SendMessage('Continuing', 33)
        Journal.Clear('The world is saving, please wait.')
    
Misc.Pause(1000)
Mobiles.UseMobile(butler)
Misc.Pause(1000)
    

fillList = [
    ('cure', '134 195 3847', 0x0F84, 0x0F07, 43, 16),
    ('agility', '134 225 3848', 0x0F7B, 0x0F08, 8, 9),
    ('strength', '134 255 3849', 0x0F86, 0x0F09, 29, 9),
    ('DP', '134 285 3850', 0x0F88, 0x0F0A, 36, 23),
    ('refresh', '134 315 3851', 0x0F7A, 0x0F0B, 1, 9),
    ('heal', '134 345 3852', 0x0F85, 0x0F0C, 22, 16),
    ('explode', '134 375 3853', 0x0F8C, 0x0F0D, 50, 16)
]

def getFillNumber(gump_raw_layout, stringlist, potType, coords, fillStopNumber):
    Mobiles.UseMobile(butler)
    Misc.Pause(500)
    gump_raw_layout = Gumps.GetGumpRawLayout(butlerGump)

    if not gump_raw_layout:
        Misc.SendMessage(f"Failed to open butler gump for {potType}.", 33)
        return 0

    gump_data = Gumps.GetGumpData(butlerGump)
    stringlist = gump_data.stringList

    entries = [entry.strip() for entry in gump_raw_layout.split('}') if entry.strip()]
    target_index = -1

    for entry_index, entry in enumerate(entries):
        if "tilepic" in entry and coords in entry:
            target_index = entry_index
            break

    if target_index != -1 and target_index + 2 < len(entries):
        target_entry = entries[target_index + 2]
        components = target_entry.split()

        last_number = int(components[-1])

        if 0 <= last_number < len(stringlist):
            value = stringlist[last_number]
            Misc.SendMessage(f"Number of {potType} potions: {value}", 66)
            return fillStopNumber - int(value)  # Calculate fill number
        else:
            Misc.SendMessage(f"Could not find {potType} potions in gump.", 33)
    else:
        Misc.SendMessage(f"Target entry or offset not found for {potType} potions.", 33)

    Gumps.CloseGump(butlerGump)
    return fillStopNumber  # Default to max if unable to calculate

while True:
    for potData in fillList:
        potType, coords, _, _, _, _ = potData

        fillNumber = getFillNumber(butler, butlerGump, potType, coords, fillStopNumber)

        while fillNumber > 100:
            if potType == 'DP' and not fillDeadlyPoison:
                break
            Misc.SendMessage(f'Filling {potType} potions, {fillNumber} left', 66)
            Gumps.CloseGump(butlerGump)
            Misc.Pause(dragTime)
            craftPot(potData)
            fillNumber = getFillNumber(butler, butlerGump, potType, coords, fillStopNumber)

    Misc.SendMessage('Butler is as full as we can get it!', 66)
    Gumps.CloseGump(butlerGump)
    sys.exit()
