"""
Pseudo Code
"""



"""
High Level Pseudocode:
===========================================

Function Dispense Container
    Input  <- Container ID
    Determine Container Attributes from ID
    Dispense container in Sorting Station
    Output -> Container Attributes
End Function

Function Load Container
    Input  -> Container Attributes
    If Qbot already has 3 containers
        OR Destination is different
        OR Total mass exceeds 90 grams
            Exit the Function
    Else
        QArm picks up container from Sorting Station
        QArm drops off container onto QBot
End Function

Function Transfer Container
    Input -> Bin Number, Sensor Type
    While Sensor for Bin Number not Activated
        Move QBot forward
End Function

Function Deposit Container
    Turn QBot towards bin
    Move Qbot forward until a distance threshold
    Turn QBot to Align Hopper to Bin
    [Optional: Use File Data]
    Rotate Hopper to Deposit
    Move QBot Back to Yellow Line
End Function

Function Return Home
    While not at the end of the line
        QBot follows line in a loop
    Rotate QBot around
End Function

Program Main
    Initialize Environment and Reset
    Loop Forever
        Generate Random Container ID
        Dispense Container
        Load Container
        Transfer Container
        Deposit Container
        Return Home
    End Loop 
End Program
"""