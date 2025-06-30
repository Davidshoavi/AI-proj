(define (domain item-sorting)
  (:requirements :strips)
  (:predicates
    (on-table ?i ?t)
    (robot-gripper-empty)
    (robot-gripping ?i)
  )
 
  (:action put-down
    :parameters (?i ?t)
    :precondition (robot-gripping ?i)
    :effect (and
               (not (robot-gripping ?i))
               (robot-gripper-empty)
               (on-table ?i ?t)
            )
  )
   (:action pick-up
    :parameters (?i ?t)
    :precondition (and (on-table ?i ?t) (robot-gripper-empty))
    :effect (and
               (not (on-table ?i ?t))
               (not (robot-gripper-empty))
               (robot-gripping ?i)
            )
  )
)
