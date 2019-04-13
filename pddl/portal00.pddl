(define (problem portal-00)
  (:domain portal)
  (:objects
    p1 - player
    room1 - room
    room2 - room
    room3 - room
    room4 - room
    cube1 - cube
    button1 - button
    door1 - door)
  (:init
    (connected room2 room3)
    (connected room3 room2)
    (at p1 room1)
    (at cube1 room3)
    (connected button1 room3)
    (connected room3 button1)
    (at portal1 room1)
    (at portal2 room2)
    (connector-connects door1 room3 room4)
    (connector-connects door1 room4 room3)
    (door-requires door1 button1))
  (:goal (at p1 room4)))
