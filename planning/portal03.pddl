(define (problem portal-03)
  (:domain portal)
  (:objects
    p1 - player
    room1 - room
    room2 - room
    room3 - room
    room4 - room)
  (:init
    (at p1 room1)
    (connected room1 room2)
    (connected room3 room2)
    (connected room4 room3)
    (at portal1 room3)
    (at portal2 portal-void)
    (can-create-portal p1 portal2)
    (can-create-portal-at room1 room1)
    (can-create-portal-at room2 room1)
    (can-create-portal-at room3 room1)
    (can-create-portal-at room1 room2)
    (can-create-portal-at room2 room2)
    (can-create-portal-at room3 room2)
    (can-create-portal-at room1 room3)
    (can-create-portal-at room2 room3)
    (can-create-portal-at room3 room3)
    (can-create-portal-at room4 room3)
    (can-create-portal-at room3 room4)
    (can-create-portal-at room4 room4))
  (:goal (at p1 room4)))
