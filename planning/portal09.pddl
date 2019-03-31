(define (problem portal-09)
  (:domain portal)
  (:objects
    p1 - player
    room1 - room
    room2 - room
    room3 - room
    room4 - room
    cube1 - cube
    button1 - button
    button2 - button
    door1 - door
    grill1 - grill
    )
  (:init
    (at p1 room1)
    (at portal1 room2)
    (at portal2 portal-void)
    (can-create-portal p1 portal2)
    (at cube1 room1)

    (connected room3 button1)
    (connected button1 room3)

    (connector-connects door1 room3 room4)
    (door-requires door1 button1)
    (connector-connects grill1 room1 room3)

    (can-create-portal-at room1 room1)
    (can-create-portal-at room2 room1)
    (can-create-portal-at room1 room2)
    (can-create-portal-at room2 room2)
    (can-create-portal-at room3 room3)
    )
  (:goal (at p1 room4)))
