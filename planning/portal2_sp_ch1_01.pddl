(define (problem portal2-sp-ch1-01)
  (:domain portal)
  (:objects
    p1 - player
    room1 - room
    room2 - room
    room3 - room
    room4 - room
    room5 - room
    room6 - room
    cube1 - cube
    button1 - button
    switch1 - switch
    switch2 - switch
    switch3 - switch
    door1 - door
    )
  (:init
    (at p1 room1)
    (at portal1 room2)
    (at portal2 portal-void)
    (at cube1 room3)
    (at switch1 room2)
    (at switch2 room2)
    (at switch3 room3)

    (connected room1 room2)
    (connected room4 button1)
    (connected button1 room4)

    (connector-connects door1 room5 room6)
    (door-requires door1 button1)

    (switch-activates-portal switch1 portal2 room4)
    (switch-activates-portal switch2 portal2 room5)
    (switch-activates-portal switch3 portal2 room3)
    )
  (:goal (at p1 room6)))
