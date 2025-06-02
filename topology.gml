graph [
    directed 0

    # =================================
    #              NODES
    # =================================

    # hosts H1 to H11
    node [ id 1 label "h1" type "host" ]
    node [ id 2 label "h2" type "host" ]
    node [ id 3 label "h3" type "host" ]
    node [ id 4 label "h4" type "host" ]
    node [ id 5 label "h5" type "host" ]
    node [ id 6 label "h6" type "host" ]
    node [ id 7 label "h7" type "host" ]
    node [ id 8 label "h8" type "host" ]
    node [ id 9 label "h9" type "host" ]
    node [ id 10 label "h10" type "host" ]
    node [ id 11 label "h11" type "host" ]

    # edge nodes (leafs) E1 to E10
    node [ id 12 label "e1" type "leaf" ]
    node [ id 13 label "e2" type "leaf" ]
    node [ id 14 label "e3" type "leaf" ]
    node [ id 15 label "e4" type "leaf" ]
    node [ id 16 label "e5" type "leaf" ]
    node [ id 17 label "e6" type "leaf" ]
    node [ id 18 label "e7" type "leaf" ]
    node [ id 19 label "e8" type "leaf" ]
    node [ id 20 label "e9" type "leaf" ]
    node [ id 21 label "e10" type "leaf" ]

    # core nodes S1 to S10
    node [ id 22 label "s1" type "core" ]
    node [ id 23 label "s2" type "core" ]
    node [ id 24 label "s3" type "core" ]
    node [ id 25 label "s4" type "core" ]
    node [ id 26 label "s5" type "core" ]
    node [ id 27 label "s6" type "core" ]
    node [ id 28 label "s7" type "core" ]
    node [ id 29 label "s8" type "core" ]
    node [ id 30 label "s9" type "core" ]
    node [ id 31 label "s10" type "core" ]

    # =================================
    #               LINKS
    # =================================

    edge [ source 1 target 12 ]
    edge [ source 11 target 12 ]
    edge [ source 12 target 22 ]

    edge [ source 2 target 13 ]
    edge [ source 13 target 23 ]

    edge [ source 3 target 14 ]
    edge [ source 14 target 24 ]

    edge [ source 4 target 15 ]
    edge [ source 15 target 25 ]

    edge [ source 5 target 16 ]
    edge [ source 16 target 26 ]

    edge [ source 6 target 17 ]
    edge [ source 17 target 27 ]

    edge [ source 7 target 18 ]
    edge [ source 18 target 28 ]

    edge [ source 8 target 19 ]
    edge [ source 19 target 29 ]

    edge [ source 9 target 20 ]
    edge [ source 20 target 30 ]

    edge [ source 10 target 21 ]
    edge [ source 21 target 31 ]

    edge [ source 22 target 23 ]
    edge [ source 23 target 24 ]
    edge [ source 24 target 25 ]
    edge [ source 25 target 26 ]
    edge [ source 26 target 27 ]
    edge [ source 27 target 28 ]
    edge [ source 28 target 29 ]
    edge [ source 29 target 30 ]
    edge [ source 30 target 31 ]

]