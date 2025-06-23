from opentrons import protocol_api
from opentrons.protocol_api import COLUMN, ALL

#metadata
metadata = {
    'protocolName': 'LEGENDPLEX_Human_CD8_NK_Final_Protocol',
    'author': 'Suat Dervish',
    'description': 'Assay Protocl for LEGENDPLEX Human CD8/NK Panel',
    'source': 'OpentronsAI'
}

#load instrument specifics
requirements = {"robotType": "Flex", "apiLevel": "2.22"}

#all in one protocol starts here
def run(protocol: protocol_api.ProtocolContext):
    
    #custom well offset of 384, 1 results in lower  tip than 3.
    well_height_sample = 1.2
    well_height_wash = 14
    
    #touch tip offset
    touch_v_offset = -9.5
    
    #rates
    wash_rate = 3
    sample_rate = 1
    
    #touchtip well coverage
    touchtip_ratio = 0.85
    
    #loading of 96 well & 384 well plate    
    source_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 'B2', label='Source Plate')
    dest_plate = protocol.load_labware('agilent_384_wellplate_140ul', 'D1', label='Destination Plate')
    
    #loading of x12 and x1 reservoirs
    small_reservoir = protocol.load_labware('nest_12_reservoir_15ml', 'A1', label='Small Reservoir')
    wash_reservoir = protocol.load_labware('nest_1_reservoir_195ml', 'D2', label='Wash Buffer Reservoir')
    
    #load trash bin in deck slot A3
    trash = protocol.load_trash_bin(location="A3")

    #load of tips on racks no adapter for partials
    tips_1 = protocol.load_labware("opentrons_flex_96_filtertiprack_50ul", "B1")    
    partial_tip_racks_initial = [tips_1]
    tips_2 = protocol.load_labware("opentrons_flex_96_filtertiprack_50ul", "C1")
    partial_tip_racks_secondary = [tips_2]
    tips_3 = protocol.load_labware("opentrons_flex_96_filtertiprack_50ul", "B3")
    partial_tip_racks_tertiary = [tips_3]
    tips_4 = protocol.load_labware("opentrons_flex_96_filtertiprack_50ul", "C3")
    partial_tip_racks_quaternary = [tips_4]
    
    
    #load of tips on racks with adapter with adapter for full plate load
    tips_5 = protocol.load_labware("opentrons_flex_96_filtertiprack_50ul", "A2", adapter="opentrons_flex_96_tiprack_adapter") 
    tips_6 = protocol.load_labware("opentrons_flex_96_filtertiprack_200ul", "D3",adapter="opentrons_flex_96_tiprack_adapter") 
    full_tip_racks = [tips_5]  # Add the other tip racks here
    full_tip_racks_wash = [tips_6]  # Add the other tip racks here

    #load pipette, note tips not attached
    pipette = protocol.load_instrument('flex_96channel_1000','left')
    
    #snippet to do quadrant pipetting 96>384
    def generate_384_well_groups():
        
        # Create empty list to store all well groups
        well_groups = []
    
        # Iterate through 12 column pairs (1-2, 3-4, ..., 23-24)
        for col in range(1, 24, 2):  # Start at 1, increment by 2 to get odd columns
            # Create the group of 4 wells in the pattern A1, A2, B1, B2
            well_group = [
                f"A{col}",    # e.g., A1
                f"A{col+1}",  # e.g., A2
                f"B{col}",    # e.g., B1
                f"B{col+1}"   # e.g., B2
            ]
        
            # Add this group to our list
            well_groups.append(well_group)
    
        return well_groups

#region step 1 - prewet, buffer, sample 96>384 aliquot, bead mix/aliquot
##################################################################################
##################################################################################
    protocol.comment("STEP 1 commencing. This step prewets the plate with wash tips, awaits filtrations, and then aluiquots required reagents into the appropriate well. It is setup for 96>384 well processing but can be modified as required).")
    
    #set flex to 96 well and tips wash
    pipette.configure_nozzle_layout(
    style=ALL,
    start="A1",
    tip_racks=full_tip_racks_wash
    )
     
    #pick up full tips for wasing - 200ul
    pipette.pick_up_tip()
    #Aspirate 200ul from the source plate (96-well) into the pipette tip
    pipette.aspirate(180, wash_reservoir['A1'])  
    protocol.comment("cleaning, waiting 30 seconds")
    #blow out the remaining liquid in the tip
    pipette.blow_out(trash)
    #Aspirate 200ul from the source plate (96-well) into the pipette tip
    pipette.aspirate(180, wash_reservoir['A1'])  
    #pre-dispense 10
    pipette.dispense(10, wash_reservoir['A1'])  
    
    #dispense sequentially to all 4 quadrants    
    pipette.dispense(40, dest_plate['A1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
    pipette.dispense(40, dest_plate['A2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
    pipette.dispense(40, dest_plate['B1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
    pipette.dispense(40, dest_plate['B2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
    
    #blow out the remaining liquid in the tip
    pipette.blow_out(trash)  
    
    #return wash tips
    pipette.return_tip()    

    #wait for user to vaccum
    protocol.pause("Place is wetted. Wait 1+ minute, then vacuum and return for addition of next compnents of the assay. Then click 'Resume' to continue.")

    #set flex to column pickup
    pipette.configure_nozzle_layout(
        style=COLUMN,
        start="A1",
        tip_racks=partial_tip_racks_initial    
        )
    


    #STANDARDS
    # Generate the well groups for the step
    well_groups = generate_384_well_groups()
    well_groups = well_groups[:1] # Limit to the first 2 groups (A1-B2, A3-B4, ..., A23-B24)
    # In your protocol:
    for i, group in enumerate(well_groups):
        protocol.comment(str(dest_plate[group[0]]))   
        protocol.comment(str(dest_plate[group[1]]))
        protocol.comment(str(dest_plate[group[2]]))
        protocol.comment(str(dest_plate[group[3]]))
        pipette.pick_up_tip()
        # Aspirate 28µL (7µL × 4 quadrants) from the source well
        pipette.aspirate(35, small_reservoir['A1'], rate=0.5)  # Example source well, change as needed
        protocol.delay(seconds=1) # pause for 5 seconds 
        # Dispense 7µL to each of the four quadrant wells in the 384-well plate
        # The corresponding well in each quadrant gets the same source
        pipette.dispense(7, dest_plate[group[0]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)  # Touch tip to the side of the well
        pipette.dispense(7, dest_plate[group[1]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[2]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[3]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.drop_tip(trash)  # Discard the tip after dispensing
        
    protocol.comment("standard wells have now 7ul of matrix")
    

#SAMPLES    
    # Generate the well groups for the step
    well_groups = generate_384_well_groups()
    well_groups = well_groups[1:] # remainder of wells 
    # In your protocol:
    for i, group in enumerate(well_groups):
        protocol.comment(str(dest_plate[group[0]]))   
        protocol.comment(str(dest_plate[group[1]]))
        protocol.comment(str(dest_plate[group[2]]))
        protocol.comment(str(dest_plate[group[3]]))
        pipette.pick_up_tip()
        # Aspirate 28µL (7µL × 4 quadrants) from the source well
        pipette.aspirate(50, small_reservoir['A2'], rate=0.5)  # Example source well, change as needed
        protocol.delay(seconds=1) # pause for 5 seconds
        # Dispense 7µL to each of the four quadrant wells in the 384-well plate
        # The corresponding well in each quadrant gets the same source
        pipette.dispense(7, dest_plate[group[0]].bottom(z=well_height_sample), rate=0.5)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[1]].bottom(z=well_height_sample), rate=0.5)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[2]].bottom(z=well_height_sample), rate=0.5)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[3]].bottom(z=well_height_sample), rate=0.5)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.drop_tip(trash)  # Discard the tip after dispensing
        
    protocol.comment("samples wells have now 7ul of assay buffer")
    
    # Protocol steps
    protocol.comment("Starting 96 to 384 well distribution...")
    
    #set flex to 96 well
    pipette.configure_nozzle_layout(
    style=ALL,
    start="A1",
    tip_racks=full_tip_racks
        )
     
    # Pick up a tip
    pipette.pick_up_tip()
        
    #mix source
    pipette.mix(5, 25, source_plate["A1"])
        
    # Aspirate 45µL from the source plate (96-well) into the pipette tip
    pipette.aspirate(45, source_plate['A1'])  # Example source well, change as needed
    
    protocol.pause("check for bubbles")
    protocol.delay(seconds=5) # pause for 5 seconds
    
    
    
    # Dispense 7µL to each of the four quadrant wells in the 384-well plate
    # The corresponding well in each quadrant gets the same source
    #pipette.touch_tip(dest_plate["A1"], radius=0.5, v_offset=-5)  # Touch tip to the side of the well
    pipette.dispense(7, dest_plate['A1'].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
    pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
    pipette.dispense(7, dest_plate['A2'].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
    pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
    pipette.dispense(7, dest_plate['B1'].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
    pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
    pipette.dispense(7, dest_plate['B2'].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
    pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)    
    # Drop the tip
    pipette.drop_tip(trash)
    #pipette.return_tip()  # Discard the tip after dispensing
    
    protocol.comment("Distribution complete!, now adding beads")
    protocol.pause("Remove tip rack from A2 and add vortexed beads to the NEST, to continue otherwise there will be a clash")
    
      
    #set flex to column mode
    pipette.configure_nozzle_layout(
        style=COLUMN,
        start="A1",
        tip_racks=partial_tip_racks_secondary
    )
    
    # Generate the well groups for the step
    well_groups = generate_384_well_groups()
    well_groups = well_groups[:] # all ([:1]) or first 2 groups ((0,1))
    
    # In your protocol:
    for i, group in enumerate(well_groups):
        protocol.comment(str(dest_plate[group[0]]))   
        protocol.comment(str(dest_plate[group[1]]))
        protocol.comment(str(dest_plate[group[2]]))
        protocol.comment(str(dest_plate[group[3]]))
        pipette.pick_up_tip()
        pipette.mix(10, 30, small_reservoir["A3"])
        # Aspirate 28µL (7µL × 4 quadrants) from the source well
        pipette.aspirate(30, small_reservoir['A3'], rate=0.5)
        protocol.delay(seconds=1) 
        # Dispense 7µL to each of the four quadrant wells in the 384-well plate
        # The corresponding well in each quadrant gets the same source
        #pipette.touch_tip(dest_plate[group[0]], radius=0.5, v_offset=-5)  # Touch tip to the side of the well
        pipette.dispense(7, dest_plate[group[0]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[1]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[2]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[3]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        
        pipette.drop_tip(trash)  # Discard the tip after dispensing
        
    protocol.pause("all wells should have beads, you have 2 hours to rest, shaking at 1200")
#endregion 

#region step 2 - washx3 in a loop, add detection antibody
##################################################################################
##################################################################################
    protocol.comment("STEP 2 commencing. Washing the plate 4x via vacuum, and then dispensing detection antibody")
       
    #set flex to 96 well and tips wash
    pipette.configure_nozzle_layout(
    style=ALL,
    start="A1",
    tip_racks=full_tip_racks_wash
    )
    
    # Refresh the tip racks to ensure they are empty
    pipette.reset_tipracks()
    
    #pick up full tips for wasing - 200ul
    pipette.pick_up_tip()
    
    #Aspirate 200ul from the source plate (96-well) into the pipette tip
    pipette.aspirate(180, wash_reservoir['A1'])  
        
    #Wash and wait 4 times. 
    for i in range(1, 5):   
        #pre-dispense 10
        pipette.dispense(10, wash_reservoir['A1'])  
        #dispense sequentially to all 4 quadrants    
        pipette.dispense(40, dest_plate['A1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        pipette.dispense(40, dest_plate['A2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        pipette.dispense(40, dest_plate['B1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        pipette.dispense(40, dest_plate['B2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        #Aspirate 200ul from the source plate (96-well) into the pipette tip
        if i!=4:
            pipette.aspirate(170, wash_reservoir['A1'])  
        #await vacuum
        protocol.pause("Dispense " + str(i) + "/4 complete. Please vacuum step and place back the filter plate.")
    
    #empty wash buffer 
    pipette.blow_out(trash)
    #return wash tips
    pipette.return_tip()    

    #dispense detection antibodies:
    protocol.comment("Now dispensing detection antibody from A4 of NEST to 384 well plate")
        
    # Generate the well groups for the step
    well_groups = generate_384_well_groups()
    well_groups = well_groups[:] # all wells or [:2]
    
    #set pipette mode to partial
    pipette.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=partial_tip_racks_tertiary
        )
    
    # Refresh the tip racks refreshed
    #pipette.reset_tipracks()
    
    #Dispense for loop using 50ul tip.
    for i, group in enumerate(well_groups):
        #comment wells actioning
        protocol.comment(str(dest_plate[group[0]]))   
        protocol.comment(str(dest_plate[group[1]]))
        protocol.comment(str(dest_plate[group[2]]))
        protocol.comment(str(dest_plate[group[3]]))
        #pick up new tips for detection antibody
        pipette.pick_up_tip()
        # Aspirate 28µL (7µL × 4 quadrants) from the source well. Example source well, change as needed
        pipette.aspirate(30, small_reservoir['A4'], rate=0.5)  
        #delay 
        protocol.delay(seconds=1) # pause for 5 seconds
        # Dispense 7µL to each of the four quadrant wells in the 384-well plate
        # The corresponding well in each quadrant gets the same source
        pipette.dispense(7, dest_plate[group[0]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[1]].bottom(z=well_height_sample), rate=sample_rate)  # Top-Right quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[2]].bottom(z=well_height_sample), rate=sample_rate)  # Bot-Left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[3]].bottom(z=well_height_sample), rate=sample_rate)  # Bot-Right quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        #discard tips
        pipette.drop_tip(trash)  # Discard the tip after dispensing
    #step is now complete
    protocol.pause("Step 2 complete! All wells now have 7µL of detection antibody. You have 60  minutes to rest. When ready for the next step continue.")
#endregion 

#region step 3 - Add strep-avidin_pe
##################################################################################
##################################################################################
    protocol.comment("STEP 3 commencing. To add StREPAVIDIN PE.")
    
    # Generate the well groups for the step
    well_groups = generate_384_well_groups()
    well_groups = well_groups[:] # all wells or [:2]
    
    #set pipette mode to partial
    pipette.configure_nozzle_layout(
        style=COLUMN,
        start="A12",
        tip_racks=partial_tip_racks_quaternary
        )
    
    # Refresh the tip racks to ensure they are empty
    #pipette.reset_tipracks()
    
    
    #In your protocol:
    for i, group in enumerate(well_groups):
        protocol.comment(str(dest_plate[group[0]]))   
        protocol.comment(str(dest_plate[group[1]]))
        protocol.comment(str(dest_plate[group[2]]))
        protocol.comment(str(dest_plate[group[3]]))
        #pick up new tips for detection antibody
        pipette.pick_up_tip()
        # Aspirate 28µL (7µL × 4 quadrants) from the source well
        pipette.aspirate(30, small_reservoir['A5'], rate=0.5)  # Example source well, change as needed
        protocol.delay(seconds=1) # pause for 5 seconds
        # Dispense 7µL to each of the four quadrant wells in the 384-well plate
        # The corresponding well in each quadrant gets the same source
        #pipette.touch_tip(dest_plate[group[0]], radius=0.5, v_offset=-5)  # Touch tip to the side of the well
        pipette.dispense(7, dest_plate[group[0]].bottom(z=well_height_sample), rate=sample_rate)  # Top-left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[1]].bottom(z=well_height_sample), rate=sample_rate)  # Top-Right quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[2]].bottom(z=well_height_sample), rate=sample_rate)  # Bot-Left quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        pipette.dispense(7, dest_plate[group[3]].bottom(z=well_height_sample), rate=sample_rate)  # Bot-Right quadrant
        pipette.touch_tip(v_offset=touch_v_offset,speed=30.0, radius=touchtip_ratio)
        #discard tips
        pipette.drop_tip(trash)  # Discard the tip after dispensing
    #step 3 complete    
    protocol.pause("All wells now have 7µL of strepav_pe. Step 3 complete! Click continue when ready post vacuum to wash")
#endregion

#region step 4 - wash and resuspend
##################################################################################
##################################################################################
    protocol.comment("STEP 4 commencingwash commencing. I.e. wash/refill ready for assay.")
    
    #set flex to 96 well and tips wash
    pipette.configure_nozzle_layout(
    style=ALL,
    start="A1",
    tip_racks=full_tip_racks_wash
    )
     
    # Refresh the tip racks to ensure they are empty
    pipette.reset_tipracks()
    
    #pick up full tips for wasing - 200ul
    pipette.pick_up_tip()
    
    #Aspirate 200ul from the wash plate (96-well) into the pipette tip
    pipette.aspirate(180, wash_reservoir['A1'])  
        
    #Wash and wait 4 times. 
    for i in range(1, 5):   
        #pre-dispense 10
        pipette.dispense(10, wash_reservoir['A1'])  
        #dispense sequentially to all 4 quadrants    
        pipette.dispense(40, dest_plate['A1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        pipette.dispense(40, dest_plate['A2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        pipette.dispense(40, dest_plate['B1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        pipette.dispense(40, dest_plate['B2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
        if i!=5:
            #Aspirate 200ul from the source plate (96-well) into the pipette tip
            pipette.aspirate(170, wash_reservoir['A1']) 
            protocol.pause("Dispense " + str(i) + "/4 complete. Please vacuum and place back the filter plate.")
        else:
            pipette.aspirate(90, wash_reservoir['A1']) 
            #pre-dispense 10
            pipette.dispense(10, wash_reservoir['A1'])  
            #dispense sequentially to all 4 quadrants    
            pipette.dispense(20, dest_plate['A1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
            pipette.dispense(20, dest_plate['A2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
            pipette.dispense(20, dest_plate['B1'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
            pipette.dispense(20, dest_plate['B2'].bottom(z=well_height_wash), rate=wash_rate)  # Top-left quadrant
            protocol.comment("Dispense " + str(i) + "Do not vacuum, final dispense, ready for run.")
    
    #empty wash buffer 
    pipette.blow_out(trash)
    #return wash tips
    pipette.return_tip() 

#endregion   