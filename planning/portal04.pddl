(define (problem portal-04)
  (:domain portal)
  (:objects
    p1 - player
    room1 - room
    room2 - room
    room3 - room
    cube1 - cube
    button1 - button
    door1 - door)
  (:init
    (at p1 room1)
    (connected room1 room2)
    (connected room1 button1)
    (connected button1 room1)
    (at cube1 room2)
    (at portal1 room1)
    (at portal2 portal-void)
    (can-create-portal p1 portal2)
    (can-create-portal-at room1 room1)
    (can-create-portal-at room2 room1)
    (can-create-portal-at room2 room2)
    (connector-connects door1 room1 room3)
    (door-requires door1 button1))
  (:goal (at p1 room3)))
