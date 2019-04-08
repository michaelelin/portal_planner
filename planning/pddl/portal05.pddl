(define (problem portal-05)
  (:domain portal)
  (:objects
    p1 - player
    room1 - room
    room2 - room
    room3 - room
    room4 - room
    room5 - room
    cube1 - cube
    cube2 - cube
    button1 - button
    button2 - button
    door1 - door)
  (:init
    (at p1 room1)
    (at portal1 room4)
    (at portal2 portal-void)
    (can-create-portal p1 portal2)
    (at cube1 room2)
    (at cube2 room3)
    (connected room1 room3)
    (connected room2 room1)
    (connected room4 room1)
    (connected room1 button1)
    (connected button1 room1)
    (connected room1 button2)
    (connected button2 room1)
    (connector-connects door1 room1 room5)
    (connector-connects door1 room5 room1)
    (door-requires door1 button1)
    (door-requires door1 button2)
    (can-create-portal-at room1 room1)
    (can-create-portal-at room2 room1)
    (can-create-portal-at room3 room1)
    (can-create-portal-at room4 room1)
    (can-create-portal-at room1 room2)
    (can-create-portal-at room2 room2)
    (can-create-portal-at room3 room2)
    (can-create-portal-at room4 room2)
    (can-create-portal-at room3 room3)
    (can-create-portal-at room1 room4)
    (can-create-portal-at room2 room4)
    (can-create-portal-at room3 room4)
    (can-create-portal-at room4 room4))
  (:goal (at p1 room5)))
