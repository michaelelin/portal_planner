(define (domain portal)
  (:requirements :strips :typing :equality)

  (:types
    location - object
    entity - object
    connector - object

    room - location
    void - location
    button - location

    movable - entity
    switch - entity
    portal - entity

    door - connector
    grill - connector

    player - movable
    item - movable

    cube - item
    )

  (:constants
    portal1 - portal
    portal2 - portal
    portal-void - void
    )

  (:predicates
    (at ?e - entity
        ?l - location)
    (connected ?l1 - location
               ?l2 - location)
    (carrying ?p - player
              ?o - item)
    (connector-connects ?connector - connector
                        ?r1 - room
                        ?r2 - room)
    (door-requires ?door - door
                   ?b - button)
    (can-create-portal ?player - player
                       ?portal - portal)
    (can-create-portal-at ?l1 - location
                          ?l2 - location)
    (switch-activates-portal ?switch - switch
                             ?portal - portal
                             ?loc - location))

  (:action move
   :parameters (
                ?player - player
                ?from - location
                ?to - location
                )
   :precondition (and (connected ?from ?to)
                      (at ?player ?from)
                      (not (= ?from ?to)))
   :effect (and (at ?player ?to)
                (not (at ?player ?from))))

  (:action pick-up
   :parameters (
                ?player - player
                ?obj - item
                ?loc - location
                )
   :precondition (and (at ?obj ?loc)
                      (at ?player ?loc)
                      (not (exists (?o - item)
                                   (carrying ?player ?o))))
   :effect (and (carrying ?player ?obj)
                (not (at ?obj ?loc))))

  (:action put-down
   :parameters (
                ?player - player
                ?obj - item
                ?loc - location
                )
   :precondition (and (at ?player ?loc)
                      (carrying ?player ?obj))
   :effect (and (not (carrying ?player ?obj))
                (at ?obj ?loc)))

  (:action enter-portal
   :parameters (
                ?player - player
                ?portal1 - portal
                ?portal2 - portal
                ?from - room
                ?to - room
                )
   :precondition (and (at ?player ?from)
                      (at ?portal1 ?from)
                      (at ?portal2 ?to)
                      (not (= ?portal1 ?portal2)))
   :effect (and (not (at ?player ?from))
                (at ?player ?to)))

  (:action enter-door
   :parameters (
                ?player - player
                ?door - door
                ?from - room
                ?to - room
                )
   :precondition (and (at ?player ?from)
                      (connector-connects ?door ?from ?to)
                      (forall (?button - button)
                              (imply (door-requires ?door ?button)
                                     (exists (?m - movable)
                                             (at ?m ?button)))))
   :effect (and (not (at ?player ?from))
                (at ?player ?to)))

  ; Don't have any portals to reset
  (:action enter-grill0
   :parameters (
                ?player - player
                ?grill - grill
                ?from - room
                ?to - room
                )
   ; For now, just don't allow to walk in with an item
   ; instead of vaporizing it
   :precondition (and (at ?player ?from)
                      (connector-connects ?grill ?from ?to)
                      (not (exists (?o - item)
                                   (carrying ?player ?o)))
                      (not (exists (?p - portal)
                                   (and (can-create-portal ?player ?p)
                                        (not (at ?p portal-void))))))
   :effect (and (not (at ?player ?from))
                (at ?player ?to)))
  ; Reset one portal
  (:action enter-grill1
   :parameters (
                ?player - player
                ?grill - grill
                ?from - room
                ?to - room
                ?p1 - portal
                ?p2 - portal
                ?p1-loc - room
                )
   ; For now, just don't allow to walk in with an item
   ; instead of vaporizing it
   :precondition (and (at ?player ?from)
                      (connector-connects ?grill ?from ?to)
                      (not (exists (?o - item)
                                   (carrying ?player ?o)))
                      (and (can-create-portal ?player ?p1)
                           (not (at ?p1 portal-void))
                           (at ?p1 ?p1-loc))
                      (not (and (can-create-portal ?player ?p2)
                                (not (at ?p1 portal-void)))))
   :effect (and (not (at ?player ?from))
                (at ?player ?to)
                (not (at ?p1 ?p1-loc))
                (at ?p1 portal-void)))
  ; Reset both portals
  (:action enter-grill2
   :parameters (
                ?player - player
                ?grill - grill
                ?from - room
                ?to - room
                ?p1-loc - room
                ?p2-loc - room
                )
   ; For now, just don't allow to walk in with an item
   ; instead of vaporizing it
   :precondition (and (at ?player ?from)
                      (connector-connects ?grill ?from ?to)
                      (not (exists (?o - item)
                                   (carrying ?player ?o)))
                      (and (can-create-portal ?player portal1)
                           (not (at portal1 portal-void))
                           (at portal1 ?p1-loc))
                      (and (can-create-portal ?player portal2)
                           (not (at portal2 portal-void))
                           (at portal2 ?p2-loc)))
   :effect (and (not (at ?player ?from))
                (at ?player ?to)
                (not (at portal1 ?p1-loc))
                (at portal1 portal-void)
                (not (at portal2 ?p2-loc))
                (at portal2 portal-void)))


  (:action create-portal
   :parameters (
                ?player - player
                ?portal - portal
                ?player-loc - location
                ?portal-prev-loc - location
                ?portal-new-loc - location
                )
   :precondition (and (at ?player ?player-loc)
                      (at ?portal ?portal-prev-loc)
                      (can-create-portal ?player ?portal)
                      (can-create-portal-at ?portal-new-loc ?player-loc)
                      (not (exists (?o - item)
                                   (carrying ?player ?o))))
   :effect (and (not (at ?portal ?portal-prev-loc))
                (at ?portal ?portal-new-loc)))

  )

