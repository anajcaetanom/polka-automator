graph [
    directed 0

    # =================================
    #              NODES
    # =================================

    # hosts H1 to H6
    node [ id 1 label "h1" type "host" ]
    node [ id 2 label "h2" type "host" ]
    node [ id 3 label "h3" type "host" ]
    node [ id 4 label "h4" type "host" ]
    node [ id 5 label "h5" type "host" ]
    node [ id 6 label "h6" type "host" ]

    # edge nodes (leafs) E1 to E6
    node [ id 11 label "e1" type "leaf" ]
    node [ id 12 label "e2" type "leaf" ]
    node [ id 13 label "e3" type "leaf" ]
    node [ id 14 label "e4" type "leaf" ]
    node [ id 15 label "e5" type "leaf" ]
    node [ id 16 label "e6" type "leaf" ]

    # core nodes S1 to S6
    node [ id 21 label "s1" type "core" ]
    node [ id 22 label "s2" type "core" ]
    node [ id 23 label "s3" type "core" ]
    node [ id 24 label "s4" type "core" ]
    node [ id 25 label "s5" type "core" ]
    node [ id 26 label "s6" type "core" ]

    # =================================
    #               LINKS
    # =================================

    edge [ source 1 target 11 ]
    edge [ source 11 target 21 ]

    edge [ source 2 target 12 ]
    edge [ source 12 target 22 ]

    edge [ source 3 target 13 ]
    edge [ source 13 target 23 ]

    edge [ source 4 target 14 ]
    edge [ source 14 target 24 ]

    edge [ source 5 target 15 ]
    edge [ source 15 target 25 ]

    edge [ source 6 target 16 ]
    edge [ source 16 target 26 ]

    # conexões entre nós de core
    edge [ source 21 target 22 ]
    edge [ source 22 target 23 ]
    edge [ source 24 target 25 ]
    edge [ source 25 target 26 ]
    edge [ source 21 target 24 ]
    edge [ source 21 target 24 ]
    edge [ source 23 target 26 ]
]
